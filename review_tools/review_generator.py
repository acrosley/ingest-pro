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
    low_confidence_threshold: float = 0.85
    alignment_match_threshold: float = 0.6
    alignment_search_window: int = 8
    flag_numbers: bool = True
    flag_unknown_lexicon: bool = True
    min_lexicon_word_length: int = 4
    reuse_alignment_model: bool = True

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
    flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "word": self.word,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "flags": self.flags,
        }


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
        low_confidence_threshold=getfloat(section, "LowConfidenceThreshold", fallback=0.85),
        alignment_match_threshold=getfloat(section, "AlignmentMatchThreshold", fallback=0.6),
        alignment_search_window=getint(section, "AlignmentSearchWindow", fallback=8),
        flag_numbers=getboolean(section, "FlagNumbers", fallback=True),
        flag_unknown_lexicon=getboolean(section, "FlagUnknownLexicon", fallback=True),
        min_lexicon_word_length=getint(section, "MinLexiconWordLength", fallback=4),
        reuse_alignment_model=getboolean(section, "ReuseAlignmentModel", fallback=True),
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


def _tokenize_transcript(text: str) -> List[str]:
    return _WORD_RE.findall(text)


def _normalize_token(token: str) -> str:
    return re.sub(r"[^a-z0-9']", "", token.lower())


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


def _flag_word(
    token: str,
    confidence: Optional[float],
    config: ReviewConfig,
    expected_terms: Optional[Iterable[str]],
) -> List[str]:
    flags: List[str] = []
    if confidence is not None and confidence < config.low_confidence_threshold:
        flags.append("low_confidence")

    if config.flag_numbers and any(ch.isdigit() for ch in token):
        flags.append("number")

    if config.flag_unknown_lexicon and len(token) >= config.min_lexicon_word_length:
        normalized = token.lower()
        if expected_terms is not None:
            normalized_terms = getattr(_flag_word, "_cached_terms", None)
            if normalized_terms is None or getattr(_flag_word, "_cached_source", None) is not expected_terms:
                normalized_terms = {term.lower() for term in expected_terms if term}
                setattr(_flag_word, "_cached_terms", normalized_terms)
                setattr(_flag_word, "_cached_source", expected_terms)
        else:
            normalized_terms = set()
        if normalized_terms and normalized not in normalized_terms:
            flags.append("unknown_lexicon")
    return flags


def generate_review(
    audio_path: Path,
    transcript_path: Path,
    review_config: ReviewConfig,
    expected_terms: Optional[Iterable[str]] = None,
) -> Optional[Path]:
    """Generate a review JSON artifact for a transcript/audio pair."""

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

    whisper_words = _extract_whisper_words(audio_path, review_config)
    aligned = _align_tokens(
        transcript_tokens,
        whisper_words,
        match_threshold=review_config.alignment_match_threshold,
        search_window=max(1, review_config.alignment_search_window),
    )

    word_reviews: List[WordReview] = []
    flag_totals: Dict[str, int] = {}

    for original_token, whisper_data, _score in aligned:
        start = whisper_data.get("start") if whisper_data else None
        end = whisper_data.get("end") if whisper_data else None
        if whisper_data and whisper_data.get("confidence") is not None:
            confidence = float(whisper_data.get("confidence"))
        elif whisper_data is None:
            confidence = 0.0
        else:
            confidence = None
        flags = _flag_word(original_token, confidence, review_config, expected_terms)
        for flag in flags:
            flag_totals[flag] = flag_totals.get(flag, 0) + 1
        word_reviews.append(WordReview(original_token, start, end, confidence, flags))

    output_dir = Path(review_config.output_directory) if review_config.output_directory else transcript_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{transcript_path.stem}.review.json"

    review_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audio_file": audio_path.name,
        "transcript_file": transcript_path.name,
        "config": review_config.to_metadata(),
        "words": [word.to_dict() for word in word_reviews],
        "flags_summary": flag_totals,
        "audit": [],
    }

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(review_payload, fh, indent=2, ensure_ascii=False)

    logger.info("Review JSON written to %s", output_path)
    return output_path

