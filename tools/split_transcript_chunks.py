import argparse
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any


TS_SPEAKER_RX = re.compile(
    r"\[(?P<ts>\d{2}:\d{2}(?::\d{2}|:\d{2,3})?)\]\s*(?:(?P<label>Agent|Caller)\s*:\s*)?",
    re.IGNORECASE,
)

# Speaker-only tokens, optionally bolded like **Agent:** or **Caller:**
SPEAKER_ONLY_RX = re.compile(r"^(?:\s*)?(?:\*\*)?(?P<label>Agent|Caller)(?:\*\*)?\s*:\s*", re.IGNORECASE)


def split_inline_segments(text: str, default_ts: str, default_speaker: str) -> List[Dict[str, str]]:
    segments: List[Dict[str, str]] = []
    last_end = 0
    last_ts = default_ts or ""
    last_speaker = default_speaker or ""
    matches = list(TS_SPEAKER_RX.finditer(text))

    # If the first match is not at index 0, keep the leading chunk under defaults
    if not matches:
        return [{"timestamp": last_ts, "speaker": normalize_speaker(last_speaker), "text": text.strip()}]

    # Leading chunk before first bracket
    first = matches[0]
    if first.start() > 0:
        lead = text[: first.start()].strip()
        if lead:
            segments.append({"timestamp": last_ts, "speaker": normalize_speaker(last_speaker), "text": lead})
    # Iterate each timestamp marker, the content is up to next marker
    for i, m in enumerate(matches):
        ts = m.group("ts") or last_ts
        label = m.group("label")
        spk = label.capitalize() if label else last_speaker
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[m.end() : next_start].strip()
        if chunk:
            # If chunk starts with a speaker-only token, strip it and override speaker when missing
            m2 = SPEAKER_ONLY_RX.match(chunk)
            use_speaker = spk
            if m2:
                sp2 = m2.group("label")
                chunk = chunk[m2.end():].strip()
                if not use_speaker:
                    use_speaker = sp2
            segments.append({"timestamp": ts, "speaker": normalize_speaker(use_speaker), "text": chunk})
        last_ts, last_speaker = ts, spk
    return segments


def normalize_speaker(s: str) -> str:
    s = (s or "").strip().capitalize()
    return "Agent" if s.lower() == "agent" else ("Caller" if s.lower() == "caller" else s)


def split_speaker_only_segments(text: str, default_ts: str, default_speaker: str) -> List[Dict[str, str]]:
    segments: List[Dict[str, str]] = []
    matches = list(SPEAKER_ONLY_RX.finditer(text))
    if not matches:
        return [{"timestamp": default_ts or "", "speaker": normalize_speaker(default_speaker), "text": text.strip()}]
    # Leading chunk (before first labeled block)
    if matches[0].start() > 0:
        lead = text[: matches[0].start()].strip()
        if lead:
            segments.append({"timestamp": default_ts or "", "speaker": normalize_speaker(default_speaker), "text": lead})
    # Labeled chunks
    for i, m in enumerate(matches):
        spk = m.group("label")
        next_start = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[m.end() : next_start].strip()
        if chunk:
            segments.append({"timestamp": default_ts or "", "speaker": normalize_speaker(spk), "text": chunk})
    return segments


def strip_leading_stars_spaces(s: str) -> str:
    """Remove any leading asterisks and whitespace from text, preserving the rest."""
    return re.sub(r"^[\s\*]+", "", s or "")


def process_file(path: Path, dry_run: bool = False) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    tr = data.get("transcript")
    if not isinstance(tr, list):
        return False

    new_tr: List[Dict[str, Any]] = []
    changed_split = False
    for item in tr:
        if not isinstance(item, dict):
            continue
        ts = str(item.get("timestamp", ""))
        sp = str(item.get("speaker", ""))
        txt = str(item.get("text", ""))
        # Detect embedded markers beyond position 0
        if TS_SPEAKER_RX.search(txt):
            chunks = split_inline_segments(txt, ts, sp)
            new_tr.extend(chunks)
            changed_split = True
        elif SPEAKER_ONLY_RX.search(txt):
            chunks = split_speaker_only_segments(txt, ts, sp)
            new_tr.extend(chunks)
            changed_split = True
        else:
            new_tr.append({"timestamp": ts, "speaker": normalize_speaker(sp), "text": txt})

    # Final sanitization: strip leading '*' and spaces from every text
    changed_sanitize = False
    for row in new_tr:
        t = row.get("text", "")
        nt = strip_leading_stars_spaces(t)
        if nt != t:
            row["text"] = nt
            changed_sanitize = True

    if not (changed_split or changed_sanitize):
        return False

    if dry_run:
        notes = []
        if changed_split:
            notes.append(f"split {len(tr)} -> {len(new_tr)} rows")
        if changed_sanitize:
            notes.append("sanitized leading * and spaces")
        print(f"[DRY] {path.name}: {'; '.join(notes)}")
        return True

    data["transcript"] = new_tr
    tmp = path.with_suffix(".tmp.json")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)
    notes = []
    if changed_split:
        notes.append(f"split {len(tr)} -> {len(new_tr)} rows")
    if changed_sanitize:
        notes.append("sanitized leading * and spaces")
    print(f"[OK] {path.name}: {'; '.join(notes)}")
    return True


def main():
    ap = argparse.ArgumentParser(description="Split inline timestamp/speaker chunks inside transcript text")
    ap.add_argument("--json-dir", required=True, help="Directory with JSON files (e.g., ALL_JSON_FILES)")
    ap.add_argument("--limit", type=int, default=0, help="Max files to modify (0 = all)")
    ap.add_argument("--dry-run", action="store_true", help="Only report changes")
    args = ap.parse_args()

    root = Path(args.json_dir)
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}")
        return

    changed = 0
    for p in sorted(root.glob("*.json")):
        if args.limit and changed >= args.limit:
            break
        if process_file(p, dry_run=args.dry_run):
            changed += 1

    print(f"Done. changed={changed}")


if __name__ == "__main__":
    main()


