import argparse
import configparser
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


AGENT_STYLE_RX = re.compile(
    r"^(?P<agent>[^_]+)_(?P<date>\d{4}-\d{2}-\d{2})_(?P<hh>\d{2})-(?P<mm>\d{2})(?:_(?P<dur>[0-9hms]+))?_(?P<trail>.+)$",
    re.IGNORECASE,
)

XSTYLE_RX = re.compile(r"^x\d{3}_\d{4}-\d{2}-\d{2}\.\d{2}-\d{2}\.\d{3}$", re.IGNORECASE)


def to_mm_ss(duration_compact: Optional[str]) -> Optional[str]:
    if not duration_compact:
        return None
    s = duration_compact.strip().lower()
    m = re.match(r"^(?:(?P<h>\d+)h)?(?:(?P<m>\d+)m)?(?:(?P<s>\d+)s)?$", s)
    if not m:
        return None
    hours = int(m.group("h") or 0)
    minutes = int(m.group("m") or 0)
    seconds = int(m.group("s") or 0)
    total = hours * 3600 + minutes * 60 + seconds
    mm, ss = divmod(total, 60)
    return f"{mm:02d}:{ss:02d}"


def to_ampm(hh: int, mm: int) -> str:
    ap = "AM" if hh < 12 else "PM"
    h12 = 12 if hh % 12 == 0 else (hh % 12)
    return f"{h12}:{mm:02d} {ap}"


def find_matching_transcript(transcripts_root: Path, agent: str, date: str, hh: str, mm: str) -> Optional[Path]:
    agent_dir = transcripts_root / agent / "Transcripts"
    if not agent_dir.exists():
        return None
    # Look for x###_YYYY-MM-DD.HH-MM.sss.txt
    pattern = f"x???_{date}.{hh}-{mm}.*.txt"
    candidates = list(agent_dir.glob(pattern))
    if len(candidates) == 1:
        return candidates[0]
    # If multiple, choose the newest
    if candidates:
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return candidates[0]
    return None


def ensure_unique(target: Path) -> Path:
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    i = 2
    while True:
        cand = target.with_name(f"{stem}_{i}{suffix}")
        if not cand.exists():
            return cand
        i += 1


def load_staff_name_to_ext(staff_map_path: Optional[Path]):
    first_to_ext = {}
    full_to_ext = {}
    if not staff_map_path or not staff_map_path.exists():
        return first_to_ext, full_to_ext
    try:
        lines = staff_map_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return first_to_ext, full_to_ext
    if not lines:
        return first_to_ext, full_to_ext
    # Heuristic: skip header row if present
    start_idx = 1 if len(lines) > 1 else 0
    for line in lines[start_idx:]:
        if not line.strip():
            continue
        parts = re.split(r"\t|\s{2,}", line.strip())
        full_name = None
        phone = None
        if len(parts) >= 6:
            # Role, Last, First, Full Name, Email, Phone
            last = parts[1].strip()
            first = parts[2].strip()
            full_name = parts[3].strip() or (f"{first} {last}".strip())
            phone = parts[5].strip()
        elif len(parts) >= 3:
            first = parts[0].strip(); last = parts[1].strip(); phone = parts[2].strip(); full_name = (f"{first} {last}").strip()
        else:
            continue
        digits = re.findall(r"\d", phone or "")
        if len(digits) >= 3:
            ext = "".join(digits[-3:])
            if full_name:
                full_to_ext[full_name.lower()] = ext
                first_to_ext[first.lower()] = ext
    return first_to_ext, full_to_ext


def normalize_one(json_path: Path, transcripts_root: Path, name_to_ext: dict, full_to_ext: dict) -> Tuple[bool, Optional[Path]]:
    stem = json_path.stem
    if XSTYLE_RX.match(stem):
        return False, None  # already normalized

    m = AGENT_STYLE_RX.match(stem)
    if not m:
        return False, None  # unknown pattern

    agent = m.group("agent").strip()
    date_s = m.group("date")
    HH = m.group("hh")
    MM = m.group("mm")
    dur_compact = m.group("dur")
    trail = m.group("trail") if "trail" in m.groupdict() else None

    transcript = find_matching_transcript(transcripts_root, agent, date_s, HH, MM)
    new_stem = None
    transcript_file = None
    transcript_path = None
    if transcript is not None:
        transcript_file = transcript.name
        transcript_path = str(transcript)
        new_stem = transcript.stem
    else:
        # Fallback: use staff_map to derive extension from agent name; else x000
        ext = name_to_ext.get(agent.lower()) or full_to_ext.get(agent.lower())
        ext = ext or "000"
        new_stem = f"x{ext}_{date_s}.{HH}-{MM}.000"

    # Load JSON
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        return False, None

    # Prepare fields
    call_time_ampm = to_ampm(int(HH), int(MM))
    call_duration = to_mm_ss(dur_compact)

    # Update schema-aligned fields (ensure section and keys exist)
    baseline_call_details = {
        "wav_file": "",
        "renamed to": None,
        "Agent": "",
        "call_date": "",
        "call_time": "",
        "call_duration": "",
    }
    call_details = {**baseline_call_details, **(data.get("call_details") or {})}
    call_details["wav_file"] = f"{new_stem}.wav" if new_stem else call_details.get("wav_file", "")
    agent_ext = name_to_ext.get(agent.lower()) or full_to_ext.get(agent.lower())
    full_name = None
    if agent_ext:
        for k, v in full_to_ext.items():
            if v == agent_ext:
                full_name = k.title()
                break
    call_details["Agent"] = (full_name if full_name else agent) or call_details.get("Agent", "")
    call_details["call_date"] = date_s or call_details.get("call_date", "")
    call_details["call_time"] = call_time_ampm or call_details.get("call_time", "")
    # Prefer computed duration; else keep existing; else empty string
    call_details["call_duration"] = call_duration or call_details.get("call_duration", "")
    # Caller from trailing portion of old naming convention (underscores to spaces)
    if trail:
        caller = trail.replace("_", " ").strip()
        # Remove common audio extensions or dots if any slipped in
        caller = re.sub(r"\.(wav|mp3|m4a|json|txt)$", "", caller, flags=re.IGNORECASE)
        call_details["caller"] = caller
    else:
        # Ensure key exists
        if "caller" not in call_details:
            call_details["caller"] = None
    # Reconstruct top-level with call_details first, then original keys in original order (unaltered)
    from collections import OrderedDict
    ordered_output = OrderedDict()
    ordered_output["call_details"] = call_details
    for k, v in data.items():
        if k == "call_details":
            continue
        ordered_output[k] = v

    # Write to new file (rename) with consistent ordering
    new_path = json_path.with_name(f"{new_stem}.json")
    new_path = ensure_unique(new_path)
    new_path.write_text(json.dumps(ordered_output, ensure_ascii=False, indent=2), encoding="utf-8")

    # Remove original
    try:
        json_path.unlink()
    except Exception:
        pass
    return True, new_path


def main():
    ap = argparse.ArgumentParser(description="Normalize JSON filenames and fill missing call_details")
    ap.add_argument("--config", default="call_pipeline.ini", help="Path to call_pipeline.ini")
    ap.add_argument("--json-dir", default=None, help="Override JsonOutputDirectory")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of files to process (0 = all)")
    ap.add_argument("--dry-run", action="store_true", help="Show planned changes without writing")
    args = ap.parse_args()

    cfg = configparser.ConfigParser()
    cfg.read(args.config, encoding="utf-8")

    transcripts_root = Path(cfg.get("Paths", "TranscriptInputDirectory").strip())
    staff_map_file = cfg.get("Paths", "StaffMapFile", fallback="").strip()
    name_to_ext, full_to_ext = load_staff_name_to_ext(Path(staff_map_file) if staff_map_file else None)
    json_dir = (
        Path(args.json_dir)
        if args.json_dir
        else Path(
            (cfg.get("Paths", "CentralJsonOutputDirectory", fallback="") or cfg.get("Paths", "JsonOutputDirectory", fallback="")).strip()
        )
    )
    if not json_dir or not json_dir.exists():
        print(f"ERROR: JSON dir not found: {json_dir}")
        return

    count = 0
    changed = 0
    for path in sorted(json_dir.glob("*.json")):
        count += 1
        if args.limit and changed >= args.limit:
            break
        stem = path.stem
        if XSTYLE_RX.match(stem):
            continue
        m = AGENT_STYLE_RX.match(stem)
        if not m:
            continue
        if args.dry_run:
            agent = m.group("agent"); date_s = m.group("date"); HH = m.group("hh"); MM = m.group("mm"); dur = m.group("dur")
            print(f"[DRY] {path.name} -> agent={agent}, date={date_s}, time={HH}:{MM}, dur={dur or ''}")
            continue
        ok, newp = normalize_one(path, transcripts_root, name_to_ext, full_to_ext)
        if ok:
            changed += 1
            print(f"[OK] {path.name} -> {newp.name}")

    print(f"Done. examined={count}, changed={changed}")


if __name__ == "__main__":
    main()


