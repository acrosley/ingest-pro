#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
smart_rename.py — config + keyring + Gemini-driven renamer

Reads call_pipeline.ini:
  [Paths]
  WatchDirectories = W:\...\Alex\Audio, W:\...\Andrew\Audio, ...
  TranscriptInputDirectory = W:\Staff_Call_Recordings
  ...
  [Gemini]
  ModelName = gemini-2.5-flash
  ApiTimeoutSeconds = 1200
  KeyringServiceName = MyGeminiApp
  KeyringUsername = gemini_api_key_user

Behavior:
  For each user derived from WatchDirectories (parent of 'Audio'), scan:
    <UserDir>\Summaries\*.md
  Build target filename:
    {Agent}_{YYYY-MM-DD}_{HH}-{MM}_{<XmYs?>}_{Caller}.md
  Agent = user folder name (e.g., 'Alex').

Safety:
  - Dry-run unless --apply.
  - Ensures uniqueness by suffixing _2, _3, ...
  - Sanitizes invalid filename chars; clamps length to 180 chars.
"""

import argparse
import configparser
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, Iterable, List

# ---------------- Optional Gemini client (google-genai) ----------------
try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

# ---------------- Regexes ----------------
OVERALL_RX = re.compile(r"(?ims)^\s*(?:\*\*|\#\#\s*)?A\.\s*Overall\s*Call\s*Summary\s*:?(?:\*\*)?\s*(?P<line>.+)$")
CALLED_RX  = re.compile(r"^\s*(?P<name>[^,.;:]+?)\s+called\b", re.IGNORECASE)

CALL_DATE_RX     = re.compile(r'"call_date"\s*:\s*"(?P<date>\d{4}-\d{2}-\d{2})"')
CALL_TIME_RX     = re.compile(r'"call_time"\s*:\s*"(?P<time>[^"]+)"')
CALL_DURATION_RX = re.compile(r'"call_duration"\s*:\s*"(?P<dur>[^"]+)"')

TIME_AMPM_RX = re.compile(r"\b(?P<h>\d{1,2}):(?P<m>\d{2})\s*(?P<ampm>[APap][Mm])\b")
TIME_24H_RX  = re.compile(r"\b(?P<h>\d{2}):(?P<m>\d{2})\b")

INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]')

# ---------------- Utilities ----------------
def clamp_filename(s: str, max_len: int = 180) -> str:
    s = INVALID_FILENAME_CHARS.sub("", s).strip()
    return s[:max_len].rstrip("._- ")

def ensure_unique(target_dir: Path, filename: str) -> Path:
    candidate = target_dir / filename
    if not candidate.exists():
        return candidate
    stem, suffix = candidate.stem, candidate.suffix
    i = 2
    while True:
        cand = target_dir / f"{stem}_{i}{suffix}"
        if not cand.exists():
            return cand
        i += 1

def parse_ampm_to_24h(text: str) -> Optional[Tuple[int, int]]:
    m = TIME_AMPM_RX.search(text or "")
    if not m:
        return None
    h, mi = int(m.group("h")), int(m.group("m"))
    ap = m.group("ampm").upper()
    if not (1 <= h <= 12 and 0 <= mi <= 59):
        return None
    return ((0 if h == 12 else h), mi) if ap == "AM" else ((12 if h == 12 else h + 12), mi)

def parse_24h(text: str) -> Optional[Tuple[int, int]]:
    m = TIME_24H_RX.search(text or "")
    if not m:
        return None
    h, mi = int(m.group("h")), int(m.group("m"))
    if 0 <= h <= 23 and 0 <= mi <= 59:
        return (h, mi)
    return None

def _compact_from_seconds(total: int) -> str:
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h: return f"{h}h{m}m{s}s"
    if m: return f"{m}m{s}s"
    return f"{s}s"

def normalize_duration_to_compact(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    m = re.match(r"^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$", s)
    if m and any(g is not None for g in m.groups()):
        h = int(m.group(1) or 0); mi = int(m.group(2) or 0); se = int(m.group(3) or 0)
        return _compact_from_seconds(h * 3600 + mi * 60 + se)
    parts = s.split(":")
    try:
        if len(parts) == 2:
            mm, ss = int(parts[0]), int(parts[1]); return _compact_from_seconds(mm * 60 + ss)
        if len(parts) == 3:
            hh, mm, ss = int(parts[0]), int(parts[1]), int(parts[2])
            return _compact_from_seconds(hh * 3600 + mm * 60 + ss)
    except ValueError:
        pass
    n = re.match(r"^(\d+)\s*s?$", s)
    if n:
        return _compact_from_seconds(int(n.group(1)))
    return None

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def mtime_local(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime)

def find_overall_line(text: str) -> Optional[str]:
    m = OVERALL_RX.search(text)
    return m.group("line").strip() if m else None

def simple_caller_from_line(line: str) -> Optional[str]:
    m = CALLED_RX.match(line or "")
    if not m:
        return None
    name = m.group("name").strip()
    name = re.sub(r"[^\w\s.'-]", "", name).strip()
    return name.title() if name.isupper() else name

def get_list_from_csv(value: str) -> List[str]:
    if not value:
        return []
    return [p.strip() for p in re.split(r"[;,]", value) if p.strip()]

# ---------------- Config + Keyring ----------------
def load_config(path: Path) -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    cfg.read(path, encoding="utf-8")
    return cfg

def get_gemini_key_from_keyring(cfg: configparser.ConfigParser) -> Optional[str]:
    service = cfg.get("Gemini", "KeyringServiceName", fallback=None)
    user    = cfg.get("Gemini", "KeyringUsername",    fallback=None)
    if not service or not user:
        return None
    try:
        import keyring  # ensure your file is NOT named keyring.py
    except Exception:
        return None
    try:
        return keyring.get_password(service, user)
    except Exception:
        return None

def make_gemini_client(cfg: configparser.ConfigParser):
    if genai is None or types is None:
        return None, None, 0
    api_key = get_gemini_key_from_keyring(cfg) or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, None, 0
    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        return None, None, 0
    model   = cfg.get("Gemini", "ModelName", fallback="gemini-2.5-flash")
    timeout = cfg.getint("Gemini", "ApiTimeoutSeconds", fallback=1200)
    return client, model, timeout

# ---------------- Gemini extraction ----------------
def extract_with_gemini(client, model: str, text: str) -> Dict[str, Optional[str]]:
    # Prefer the Overall line with some context; else first 2000 chars
    line = find_overall_line(text)
    if line:
        idx = text.find(line); start = max(0, idx - 800); end = min(len(text), idx + len(line) + 800)
        snippet = text[start:end]
    else:
        snippet = text[:2000]

    schema = types.Schema(
        type="OBJECT",
        required=["caller_name"],
        properties={
            "caller_name":      types.Schema(type="STRING"),
            "call_date":        types.Schema(type="STRING", format="date"),         # YYYY-MM-DD
            "call_time_24h":    types.Schema(type="STRING", pattern=r"^\d{2}:\d{2}$"),  # HH:MM
            "duration_compact": types.Schema(type="STRING"),                        # XmYs / XhYmZs / Ys
        },
    )
    system = (
        "Extract fields from a law-firm call summary. Prefer the 'A. Overall Call Summary' sentence. "
        "Return ONLY JSON matching the schema. Use null for unknown."
    )

    try:
        resp = client.models.generate_content(
            model=model,
            contents=[f"Extract fields from this Markdown snippet:\n\n{snippet}"],
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0,
                response_mime_type="application/json",
                response_schema=schema,
                max_output_tokens=200,
            ),
        )
        raw = (resp.text or "").strip()
        import json as _json
        data = _json.loads(raw)
        # Normalize absent keys to None
        for k in ("caller_name", "call_date", "call_time_24h", "duration_compact"):
            if k not in data:
                data[k] = None
        return data
    except Exception:
        return {"caller_name": None, "call_date": None, "call_time_24h": None, "duration_compact": None}

# ---------------- Core logic ----------------
def derive_fields(md_path: Path, user_dir: Path, client, model: str) -> Dict[str, Optional[str]]:
    agent = user_dir.name
    text  = read_text(md_path)

    caller = date = time_hhmm = duration = None

    if client:
        g = extract_with_gemini(client, model, text)
        caller   = g.get("caller_name") or caller
        date     = g.get("call_date") or date
        time_hhmm = g.get("call_time_24h") or time_hhmm
        duration = g.get("duration_compact") or duration

    # Fallbacks: call_details JSON if present
    if not date:
        m = CALL_DATE_RX.search(text)
        if m: date = m.group("date")
    if not time_hhmm:
        m = CALL_TIME_RX.search(text)
        if m:
            hhmm = parse_ampm_to_24h(m.group("time")) or parse_24h(m.group("time"))
            if hhmm: time_hhmm = f"{hhmm[0]:02d}:{hhmm[1]:02d}"
    if not duration:
        m = CALL_DURATION_RX.search(text)
        if m:
            duration = normalize_duration_to_compact(m.group("dur"))

    if not caller:
        line = find_overall_line(text)
        caller = simple_caller_from_line(line) if line else None

    # Last resort: file mtime
    if not date or not time_hhmm:
        dt = mtime_local(md_path)
        if not date:
            date = dt.strftime("%Y-%m-%d")
        if not time_hhmm:
            time_hhmm = dt.strftime("%H:%M")

    return {"agent": agent, "date": date, "time_hhmm": time_hhmm, "duration_compact": duration, "caller": caller}

def build_target_filename(fields: Dict[str, Optional[str]]) -> Optional[str]:
    agent = fields.get("agent")
    date  = fields.get("date")
    time  = fields.get("time_hhmm")
    caller = fields.get("caller") or "Unknown"
    dur    = fields.get("duration_compact")

    if not agent or not date or not time:
        return None

    hh, mm = time.split(":")
    parts = [agent, date, f"{hh}-{mm}"]
    if dur: parts.append(dur)
    parts.append(clamp_filename(caller, 60))
    return clamp_filename("_".join(parts) + ".md")

def iter_user_dirs_from_watch(cfg: configparser.ConfigParser) -> List[Path]:
    watch = cfg.get("Paths", "WatchDirectories", fallback="")
    entries = get_list_from_csv(watch)
    user_dirs: List[Path] = []
    for p in entries:
        pth = Path(p)
        # Expect ...\<User>\Audio; user dir is parent
        if pth.name.lower() == "audio":
            user_dirs.append(pth.parent)
        else:
            # If entries are already user dirs, accept as-is
            user_dirs.append(pth)
    # Deduplicate while preserving order
    seen = set()
    uniq: List[Path] = []
    for u in user_dirs:
        if str(u).lower() not in seen:
            uniq.append(u)
            seen.add(str(u).lower())
    return uniq

def iter_summary_files(user_dir: Path) -> Iterable[Path]:
    p = user_dir / "Summaries"
    if not p.exists():
        return []
    return (f for f in p.glob("*.md") if f.is_file())

# ---------------- CLI ----------------
def main():
    ap = argparse.ArgumentParser(description="Rename Markdown summaries using Gemini + Overall Call Summary")
    ap.add_argument("--config", default="call_pipeline.ini", help="Path to call_pipeline.ini")
    ap.add_argument("--apply", action="store_true", help="Perform renames (otherwise dry-run)")
    ap.add_argument("--model", default=None, help="Override Gemini model (e.g., gemini-2.5-flash)")
    ap.add_argument("--verbose", action="store_true", help="Verbose logging")
    ap.add_argument("--require-api-key", action="store_true",
                    help="Fail if Gemini API key/client is not available")
    ap.add_argument("--no-llm", action="store_true",
                    help="Disable Gemini usage entirely (regex/mtime only)")
    args = ap.parse_args()

    # Load config
    cfg = load_config(Path(args.config))

    # Build user directories from WatchDirectories
    user_dirs = iter_user_dirs_from_watch(cfg)
    if not user_dirs:
        print("No user directories resolved from [Paths] WatchDirectories.", file=sys.stderr)
        sys.exit(2)

    # Init Gemini (optional)
    if args.no_llm:
        client, cfg_model, _timeout = (None, None, 0)
    else:
        client, cfg_model, _timeout = make_gemini_client(cfg)
    model = args.model or cfg_model or "gemini-2.5-flash"

    if args.require-api-key and client is None:
        print("ERROR: --require-api-key set but Gemini client is not available (missing library or API key).",
              file=sys.stderr)
        sys.exit(3)
    if client is None and not args.no_llm:
        print("INFO: Gemini client not available or API key missing; using regex/mtime only.", file=sys.stderr)

    seen = renamed = skipped = 0
    for user_dir in user_dirs:
        for md_path in iter_summary_files(user_dir):
            seen += 1
            fields = derive_fields(md_path, user_dir, client, model)
            target_name = build_target_filename(fields)
            if not target_name:
                skipped += 1
                if args.verbose:
                    print(f"[SKIP] {md_path} (insufficient fields: {fields})")
                continue

            target_path = ensure_unique(md_path.parent, target_name)
            if args.apply:
                try:
                    os.replace(md_path, target_path)
                    renamed += 1
                    print(f"[RENAMED] {md_path.name} -> {target_path.name}")
                except Exception as e:
                    skipped += 1
                    print(f"[ERROR] {md_path.name} -> {target_path.name}: {e}", file=sys.stderr)
            else:
                print(f"[DRY-RUN] {md_path.name} -> {target_path.name}")

            if client:
                time.sleep(0.05)  # gentle pacing

    print(f"\nSummary: seen={seen}, renamed={renamed}, skipped={skipped}, apply={args.apply}")

if __name__ == "__main__":
    main()
