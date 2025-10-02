"""Utilities for generating word-level review data from transcripts and audio."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import whisper  # type: ignore
except Exception:  # pragma: no cover - optional dependency resolution happens at runtime
    whisper = None  # type: ignore


logger = logging.getLogger("CallPipeline.Review")


@dataclass
class ReviewConfig:
    """Configuration container for review generation."""

    enabled: bool = True
    alignment_model: str = "base"
    alignment_device: str = "cpu"
    output_directory: Optional[str] = None
    low_confidence_threshold: float = 0.70  # Lowered from 0.85 for more reasonable flagging
    alignment_match_threshold: float = 0.6
    alignment_search_window: int = 8
    flag_numbers: bool = True
    flag_unknown_lexicon: bool = False  # Disabled by default - too many false positives
    min_lexicon_word_length: int = 4
    reuse_alignment_model: bool = True
    prefer_google_cloud_confidence: bool = True  # Use .confidence.json if available

    def to_metadata(self) -> Dict[str, object]:
        metadata = asdict(self)
        # Avoid leaking output_directory specifics in metadata to keep JSON tidy
        metadata.pop("output_directory", None)
        return metadata


@dataclass
class WordReview:
    """Represents a single reviewed word."""

    word: str
    start: Optional[float]
    end: Optional[float]
    confidence: Optional[float]
    flags: List[Dict[str, object]] = field(default_factory=list)
    whisper_alternative: Optional[str] = None
    alignment_score: Optional[float] = None
    context_before: str = ""
    context_after: str = ""

    def to_dict(self) -> Dict[str, object]:
        result = {
            "word": self.word,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "flags": self.flags,
        }
        if self.whisper_alternative:
            result["whisper_alternative"] = self.whisper_alternative
        if self.alignment_score is not None:
            result["alignment_score"] = self.alignment_score
        if self.context_before:
            result["context_before"] = self.context_before
        if self.context_after:
            result["context_after"] = self.context_after
        return result


_MODEL_CACHE: Dict[Tuple[str, str], object] = {}


def load_review_config(config_parser) -> ReviewConfig:
    """Load review configuration from the pipeline config parser."""

    section = "Review"
    if not config_parser.has_section(section):
        return ReviewConfig()

    get = config_parser.get
    getint = config_parser.getint
    getfloat = config_parser.getfloat
    getboolean = config_parser.getboolean

    return ReviewConfig(
        enabled=getboolean(section, "Enabled", fallback=True),
        alignment_model=get(section, "AlignmentModel", fallback="base").strip() or "base",
        alignment_device=get(section, "AlignmentDevice", fallback="cpu").strip() or "cpu",
        output_directory=(get(section, "OutputDirectory", fallback="").strip() or None),
        low_confidence_threshold=getfloat(section, "LowConfidenceThreshold", fallback=0.70),
        alignment_match_threshold=getfloat(section, "AlignmentMatchThreshold", fallback=0.6),
        alignment_search_window=getint(section, "AlignmentSearchWindow", fallback=8),
        flag_numbers=getboolean(section, "FlagNumbers", fallback=True),
        flag_unknown_lexicon=getboolean(section, "FlagUnknownLexicon", fallback=True),
        min_lexicon_word_length=getint(section, "MinLexiconWordLength", fallback=4),
        reuse_alignment_model=getboolean(section, "ReuseAlignmentModel", fallback=True),
        prefer_google_cloud_confidence=getboolean(section, "PreferGoogleCloudConfidence", fallback=True),
    )


def _get_alignment_model(config: ReviewConfig):
    if whisper is None:
        raise RuntimeError("openai-whisper is required for review alignment but is not installed")

    key = (config.alignment_model, config.alignment_device)
    if config.reuse_alignment_model and key in _MODEL_CACHE:
        return _MODEL_CACHE[key]

    logger.debug(
        "Loading Whisper model '%s' on device '%s' for review alignment", config.alignment_model, config.alignment_device
    )
    model = whisper.load_model(config.alignment_model, device=config.alignment_device)
    if config.reuse_alignment_model:
        _MODEL_CACHE[key] = model
    return model


def _load_google_cloud_confidence(transcript_path: Path) -> Optional[Dict[str, object]]:
    """Load Google Cloud STT confidence data if available.
    
    Returns the parsed confidence JSON, or None if not found.
    """
    confidence_path = transcript_path.parent / f"{transcript_path.stem}.confidence.json"
    
    if not confidence_path.exists():
        return None
    
    try:
        with open(confidence_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        
        # Validate structure
        if "word_data" in data and isinstance(data["word_data"], list):
            logger.info("Using Google Cloud STT confidence data from %s", confidence_path)
            return data
        else:
            logger.warning("Invalid confidence file structure at %s", confidence_path)
            return None
    
    except Exception as e:
        logger.warning("Failed to load confidence data from %s: %s", confidence_path, e)
        return None


def _extract_whisper_words(audio_path: Path, config: ReviewConfig) -> List[Dict[str, object]]:
    model = _get_alignment_model(config)
    logger.debug("Starting alignment transcription for %s", audio_path)
    result = model.transcribe(
        str(audio_path),
        task="transcribe",
        word_timestamps=True,
        condition_on_previous_text=False,
        temperature=0.0,
    )
    words: List[Dict[str, object]] = []
    for segment in result.get("segments", []):
        for word in segment.get("words", []) or []:
            cleaned_word = word.get("word", "")
            if not cleaned_word:
                continue
            words.append(
                {
                    "word": cleaned_word.strip(),
                    "start": word.get("start"),
                    "end": word.get("end"),
                    "confidence": word.get("probability")
                    if word.get("probability") is not None
                    else word.get("confidence"),
                }
            )
    return words


_WORD_RE = re.compile(r"[\w']+", re.UNICODE)
_TIMESTAMP_RE = re.compile(r"\[\d{2}:\d{2}(?::\d{2})?\]")
_SPEAKER_LABEL_RE = re.compile(r"\*\*(?:Agent|Caller):\*\*")

# Pattern recognition for high-value information
_PHONE_PATTERN = re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
_CASE_NUMBER_PATTERN = re.compile(r'\b\d{6,}\b')
_MONEY_PATTERN = re.compile(r'\$[\d,]+(?:\.\d{2})?|\b\d+\s*dollars?\b', re.IGNORECASE)
_DATE_PATTERN = re.compile(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)\b', re.IGNORECASE)
_TIME_PATTERN = re.compile(r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b', re.IGNORECASE)
_SPELLING_PATTERN = re.compile(r'\b[A-Z](?:\s+[A-Z]){2,}\b')  # H O U A I S


def _strip_transcript_metadata(text: str) -> str:
    """Remove timestamps and speaker labels from Gemini-formatted transcript."""
    # Remove timestamps like [00:00:02]
    text = _TIMESTAMP_RE.sub("", text)
    # Remove speaker labels like **Agent:** or **Caller:**
    text = _SPEAKER_LABEL_RE.sub("", text)
    return text


def _tokenize_transcript(text: str) -> List[str]:
    """Tokenize transcript text after removing metadata."""
    # Strip metadata first to avoid tokenizing timestamps and speaker labels
    clean_text = _strip_transcript_metadata(text)
    return _WORD_RE.findall(clean_text)


def _normalize_token(token: str) -> str:
    return re.sub(r"[^a-z0-9']", "", token.lower())


def _is_phone_number(text: str) -> bool:
    """Check if text contains or is a phone number."""
    return bool(_PHONE_PATTERN.search(text))


def _is_case_number(text: str) -> bool:
    """Check if text is a case number (6+ consecutive digits)."""
    return bool(_CASE_NUMBER_PATTERN.match(text))


def _is_money_amount(text: str) -> bool:
    """Check if text mentions money/dollar amounts."""
    return bool(_MONEY_PATTERN.search(text))


def _is_date(text: str) -> bool:
    """Check if text contains a date."""
    return bool(_DATE_PATTERN.search(text))


def _is_time(text: str) -> bool:
    """Check if text contains a time."""
    return bool(_TIME_PATTERN.search(text))


def _is_spelled_out(words: List[str], index: int, window: int = 3) -> bool:
    """
    Check if this is part of a spelled-out word (e.g., H O U A I S).
    Look at surrounding words to detect pattern of single letters.
    """
    start = max(0, index - window)
    end = min(len(words), index + window + 1)
    context = ' '.join(words[start:end])
    return bool(_SPELLING_PATTERN.search(context))


def _is_proper_noun(token: str, expected_terms: Optional[Iterable[str]] = None) -> bool:
    """
    Check if token is likely a proper noun (capitalized, not common word).
    """
    if not token or len(token) < 2:
        return False
    
    # Check if it's capitalized
    if not token[0].isupper():
        return False
    
    # Common words that are often capitalized but aren't proper nouns
    common_words = {'I', 'A', 'The', 'Hello', 'Hi', 'Yes', 'No', 'Okay', 'Ok', 'Thank', 'Thanks'}
    if token in common_words:
        return False
    
    # If we have expected terms, check if it's in there
    if expected_terms:
        normalized_terms = {term.lower() for term in expected_terms if term}
        if token.lower() in normalized_terms:
            return False  # It's expected, so not flagging
    
    return True


def _align_tokens(
    transcript_tokens: Sequence[str],
    whisper_words: Sequence[Dict[str, object]],
    match_threshold: float,
    search_window: int,
) -> List[Tuple[str, Optional[Dict[str, object]], float]]:
    aligned: List[Tuple[str, Optional[Dict[str, object]], float]] = []
    whisper_index = 0
    whisper_length = len(whisper_words)

    for token in transcript_tokens:
        normalized = _normalize_token(token)
        best_idx: Optional[int] = None
        best_score = 0.0

        for candidate_idx in range(whisper_index, min(whisper_length, whisper_index + search_window)):
            whisper_token_raw = str(whisper_words[candidate_idx].get("word", ""))
            whisper_token = _normalize_token(whisper_token_raw)
            if not whisper_token and normalized:
                continue
            score = SequenceMatcher(None, normalized, whisper_token).ratio() if normalized or whisper_token else 1.0
            if score > best_score:
                best_score = score
                best_idx = candidate_idx
                if score >= 1.0:
                    break

        if best_idx is not None and best_score >= match_threshold:
            aligned.append((token, whisper_words[best_idx], best_score))
            whisper_index = best_idx + 1
        else:
            aligned.append((token, None, 0.0))
    return aligned


def _flag_word_for_review(
    token: str,
    token_index: int,
    all_tokens: List[str],
    whisper_word: Optional[Dict[str, object]],
    alignment_score: float,
    config: ReviewConfig,
    expected_terms: Optional[Iterable[str]],
    original_text: str = "",
) -> List[Dict[str, object]]:
    """
    Flag words for manual review based on patterns and comparison.
    Returns list of flag dictionaries with type and metadata.
    """
    flags: List[Dict[str, object]] = []
    
    # Get whisper version for comparison
    whisper_token = whisper_word.get("word", "").strip() if whisper_word else None
    whisper_confidence = whisper_word.get("confidence") if whisper_word else None
    
    # PATTERN-BASED FLAGGING (High-value information)
    
    # 1. Phone numbers - critical for callbacks
    if _is_phone_number(token) or (whisper_token and _is_phone_number(whisper_token)):
        flags.append({
            "type": "phone_number",
            "reason": "Phone number detected - verify accuracy",
            "priority": "high"
        })
    
    # 2. Case numbers - critical for legal case tracking
    if _is_case_number(token) or (whisper_token and _is_case_number(whisper_token)):
        flags.append({
            "type": "case_number",
            "reason": "Case number detected - verify accuracy",
            "priority": "high"
        })
    
    # 3. Money amounts - important for settlements, fees
    if _is_money_amount(token) or (whisper_token and _is_money_amount(whisper_token)):
        flags.append({
            "type": "money_amount",
            "reason": "Dollar amount detected - verify accuracy",
            "priority": "medium"
        })
    
    # 4. Dates - important for appointments, deadlines
    if _is_date(token) or (whisper_token and _is_date(whisper_token)):
        flags.append({
            "type": "date",
            "reason": "Date detected - verify accuracy",
            "priority": "medium"
        })
    
    # 5. Times - appointment scheduling
    if _is_time(token) or (whisper_token and _is_time(whisper_token)):
        flags.append({
            "type": "time",
            "reason": "Time detected - verify accuracy",
            "priority": "medium"
        })
    
    # 6. Spelled-out words (names, etc.) - H O U A I S
    if _is_spelled_out(all_tokens, token_index):
        flags.append({
            "type": "spelling",
            "reason": "Spelled-out word detected - verify spelling",
            "priority": "high"
        })
    
    # 7. Proper nouns (names, companies) - identity verification
    if _is_proper_noun(token, expected_terms):
        flags.append({
            "type": "proper_noun",
            "reason": "Proper noun (name/company) - verify identity",
            "priority": "medium"
        })
    
    # COMPARISON-BASED FLAGGING (Transcription discrepancies)
    
    # 8. Gemini vs Whisper mismatch
    if whisper_token and _normalize_token(token) != _normalize_token(whisper_token):
        # Significant difference in transcription
        if alignment_score < 0.8:  # Not a close match
            flags.append({
                "type": "transcription_mismatch",
                "reason": "Gemini and Whisper transcribed differently",
                "priority": "high",
                "gemini_version": token,
                "whisper_version": whisper_token,
                "similarity_score": alignment_score
            })
    
    # 9. Low alignment confidence (word couldn't be aligned well)
    if alignment_score < config.alignment_match_threshold and not whisper_word:
        flags.append({
            "type": "alignment_failed",
            "reason": "Could not align with Whisper output",
            "priority": "low",
            "note": "Gemini confident but Whisper missed this word"
        })
    
    # 10. Low Whisper confidence (when available)
    if whisper_confidence is not None and whisper_confidence < config.low_confidence_threshold:
        flags.append({
            "type": "low_confidence",
            "reason": f"Whisper confidence: {whisper_confidence:.2f}",
            "priority": "medium",
            "confidence": whisper_confidence
        })
    
    return flags


def generate_review(
    audio_path: Path,
    transcript_path: Path,
    review_config: ReviewConfig,
    expected_terms: Optional[Iterable[str]] = None,
) -> Optional[Path]:
    """Generate a review JSON artifact for a transcript/audio pair.
    
    This function performs word-level analysis to identify potentially problematic words.
    
    The process:
    1. Checks for Google Cloud STT confidence data (.confidence.json)
    2. If available, uses that data directly (faster, more accurate)
    3. Otherwise, falls back to Whisper for alignment and confidence
    4. Strips metadata (timestamps, speaker labels) from the transcript
    5. Tokenizes only the actual spoken words
    6. Aligns tokens with timing/confidence data
    7. Flags words based on confidence thresholds and other criteria
    
    Flags:
    - low_confidence: Word has confidence below threshold (default 0.70)
    - number: Word contains digits (important for case numbers, phone numbers)
    - unknown_lexicon: Word not in expected terms AND has low confidence
    """

    if not review_config.enabled:
        logger.debug("Review generation disabled in configuration")
        return None

    audio_path = Path(audio_path)
    transcript_path = Path(transcript_path)

    if not audio_path.exists():
        logger.warning("Review generation skipped: audio file missing at %s", audio_path)
        return None

    if not transcript_path.exists():
        logger.warning("Review generation skipped: transcript file missing at %s", transcript_path)
        return None

    with open(transcript_path, "r", encoding="utf-8") as fh:
        transcript_text = fh.read()

    if not transcript_text.strip():
        logger.info("Review generation skipped: transcript empty for %s", transcript_path)
        return None

    transcript_tokens = _tokenize_transcript(transcript_text)
    if not transcript_tokens:
        logger.info("Review generation skipped: no tokens parsed for %s", transcript_path)
        return None

    # Try to use Google Cloud STT confidence data first
    google_cloud_data = None
    confidence_source = "whisper"
    
    if review_config.prefer_google_cloud_confidence:
        google_cloud_data = _load_google_cloud_confidence(transcript_path)
        if google_cloud_data:
            confidence_source = "google_cloud_stt"
            # Convert Google Cloud format to whisper-like format for compatibility
            whisper_words = [
                {
                    "word": wd.get("word", "").strip(),
                    "start": wd.get("start_time"),
                    "end": wd.get("end_time"),
                    "confidence": wd.get("confidence"),
                }
                for wd in google_cloud_data.get("word_data", [])
            ]
            logger.info("Using Google Cloud STT confidence (overall: %.2f)", 
                       google_cloud_data.get("overall_confidence", 0))
        else:
            # Fallback to Whisper
            whisper_words = _extract_whisper_words(audio_path, review_config)
    else:
        whisper_words = _extract_whisper_words(audio_path, review_config)
    aligned = _align_tokens(
        transcript_tokens,
        whisper_words,
        match_threshold=review_config.alignment_match_threshold,
        search_window=max(1, review_config.alignment_search_window),
    )

    word_reviews: List[WordReview] = []
    flag_totals: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {"high": 0, "medium": 0, "low": 0}

    for idx, (original_token, whisper_data, alignment_score) in enumerate(aligned):
        start = whisper_data.get("start") if whisper_data else None
        end = whisper_data.get("end") if whisper_data else None
        whisper_token = whisper_data.get("word", "").strip() if whisper_data else None
        
        # Get confidence from whisper if available
        if whisper_data and whisper_data.get("confidence") is not None:
            confidence = float(whisper_data.get("confidence"))
        else:
            confidence = None
        
        # Get context for display in UI
        context_before = " ".join(transcript_tokens[max(0, idx-3):idx])
        context_after = " ".join(transcript_tokens[idx+1:min(len(transcript_tokens), idx+4)])
        
        # Get flags using new pattern and comparison-based logic
        flags = _flag_word_for_review(
            token=original_token,
            token_index=idx,
            all_tokens=transcript_tokens,
            whisper_word=whisper_data,
            alignment_score=alignment_score,
            config=review_config,
            expected_terms=expected_terms,
            original_text=transcript_text
        )
        
        # Count flag types and priorities
        for flag in flags:
            flag_type = flag.get("type", "unknown")
            flag_totals[flag_type] = flag_totals.get(flag_type, 0) + 1
            priority = flag.get("priority", "low")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        word_reviews.append(WordReview(
            word=original_token,
            start=start,
            end=end,
            confidence=confidence,
            flags=flags,
            whisper_alternative=whisper_token if whisper_token != original_token else None,
            alignment_score=alignment_score,
            context_before=context_before,
            context_after=context_after
        ))

    output_dir = Path(review_config.output_directory) if review_config.output_directory else transcript_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{transcript_path.stem}.review.json"

    # Calculate statistics
    total_words = len(word_reviews)
    flagged_words = sum(1 for w in word_reviews if w.flags)
    
    review_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audio_file": audio_path.name,
        "transcript_file": transcript_path.name,
        "config": review_config.to_metadata(),
        "confidence_source": confidence_source,  # Track which engine provided confidence
        "overall_confidence": google_cloud_data.get("overall_confidence") if google_cloud_data else None,
        "statistics": {
            "total_words": total_words,
            "flagged_words": flagged_words,
            "flag_percentage": round((flagged_words / total_words * 100) if total_words > 0 else 0, 1),
            "priority_counts": priority_counts,
        },
        "words": [word.to_dict() for word in word_reviews],
        "flags_summary": flag_totals,
        "corrections": [],  # For tracking manual corrections
        "audit": [],
    }

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(review_payload, fh, indent=2, ensure_ascii=False)

    logger.info("Review JSON written to %s", output_path)
    return output_path

