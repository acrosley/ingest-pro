"""
AssemblyAI-Specific Review Generator

Generates manual review data optimized for AssemblyAI transcripts.
Uses native AssemblyAI confidence scores and speaker labels.
"""

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("CallPipeline.AssemblyAIReview")


@dataclass
class AssemblyAIReviewConfig:
    """
    Configuration for AssemblyAI review generation.
    
    Edit these settings to customize the review behavior:
    - Confidence thresholds control when words are flagged for low confidence
    - Common words (like "the", "and", "of") get a lower threshold since they're usually correct
    - Pattern detection flags enable/disable specific types of flagging
    """
    
    enabled: bool = True
    output_directory: Optional[str] = None
    
    # Confidence thresholds (0.0 to 1.0)
    low_confidence_threshold: float = 0.60              # Flag words below this confidence (lowered from 0.70)
    critical_confidence_threshold: float = 0.50         # Critical flag for very low confidence
    common_words_confidence_threshold: float = 0.25     # Lower threshold for common words (naturally lower)
    
    # Pattern detection flags (enable/disable specific flagging)
    flag_phone_numbers: bool = True
    flag_case_numbers: bool = True
    flag_money_amounts: bool = True
    flag_dates: bool = True
    flag_times: bool = True
    flag_names: bool = True
    flag_spelled_words: bool = True
    flag_numbers: bool = True
    
    # Context settings (words shown before/after flagged words)
    context_words_before: int = 5
    context_words_after: int = 5
    
    def to_metadata(self) -> Dict[str, object]:
        metadata = asdict(self)
        metadata.pop("output_directory", None)
        return metadata


@dataclass
class WordFlag:
    """Represents a flag on a word."""
    
    type: str
    reason: str
    priority: str  # high, medium, low
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "reason": self.reason,
            "priority": self.priority,
            **self.metadata
        }


@dataclass
class ReviewWord:
    """Represents a word for review."""
    
    word: str
    confidence: Optional[float]
    start_time: Optional[float]
    end_time: Optional[float]
    speaker: Optional[str]
    index: int
    flags: List[WordFlag] = field(default_factory=list)
    context_before: str = ""
    context_after: str = ""
    suggested_correction: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "word": self.word,
            "confidence": self.confidence,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "speaker": self.speaker,
            "index": self.index,
            "flags": [f.to_dict() for f in self.flags],
            "context_before": self.context_before,
            "context_after": self.context_after,
            "suggested_correction": self.suggested_correction,
        }


# Pattern recognition for high-value information
_PHONE_PATTERN = re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
_PHONE_SEGMENT_PATTERN = re.compile(r'^[\d-]+$')  # For spelled-out numbers like "2-1-0"
_CASE_NUMBER_PATTERN = re.compile(r'\b\d{6,}\b')
_MONEY_PATTERN = re.compile(r'\$[\d,]+(?:\.\d{2})?|\b\d+\s*(?:dollars?|cents?)\b', re.IGNORECASE)
_DATE_PATTERN = re.compile(
    r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|'
    r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
    r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
    r'\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)\b',
    re.IGNORECASE
)
_TIME_PATTERN = re.compile(r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b', re.IGNORECASE)
_NUMBER_PATTERN = re.compile(r'\b\d+\b')
_SPELLED_NUMBER_PATTERN = re.compile(r'^[0-9-]+$')  # Like "2-2-7" or "88-22"


def _is_likely_name(word: str) -> bool:
    """Check if word is likely a proper name (capitalized, reasonable length)."""
    if not word or len(word) < 2:
        return False
    
    # Must be capitalized
    if not word[0].isupper():
        return False
    
    # Strip punctuation for checking
    clean_word = word.strip('.,!?;:\'"')
    
    # NOT a name if it's a number or contains mostly digits
    if clean_word.isdigit():
        return False
    
    # NOT a name if it's a hyphenated/dashed number (like "0-2-2-7" or "2-2-7")
    if re.match(r'^[\d-]+$', clean_word):
        return False
    
    # NOT a name if it's an ordinal number (1st, 2nd, 3rd, 23rd, etc.)
    if re.match(r'^\d+(st|nd|rd|th)$', clean_word, re.IGNORECASE):
        return False
    
    # NOT a name if it's a month (these are often in dates, not names)
    months = {
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December',
        'Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 'Sep', 'Sept', 'Oct', 'Nov', 'Dec'
    }
    if clean_word in months:
        return False
    
    # NOT a name if it's a day of the week
    days = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
            'Mon', 'Tue', 'Tues', 'Wed', 'Thu', 'Thur', 'Thurs', 'Fri', 'Sat', 'Sun'}
    if clean_word in days:
        return False
    
    # Common non-name words (capitalized words that aren't proper nouns)
    common_words = {
        'I', 'A', 'The', 'Hello', 'Hi', 'Yes', 'No', 'Okay', 'Ok', 
        'Thank', 'Thanks', 'Please', 'Sorry', 'And', 'But', 'Or',
        'This', 'That', 'These', 'Those', 'What', 'When', 'Where',
        'Why', 'How', 'Who', 'Which', 'Of', 'So', 'To', 'From',
        'For', 'With', 'Can', 'Will', 'Was', 'Were', 'Are', 'Is',
        'Have', 'Has', 'Do', 'Does', 'Did', 'Would', 'Could', 'Should',
        'My', 'Your', 'Their', 'Our', 'His', 'Her', 'Its',
        # Additional common words at sentence start
        'On', 'In', 'It', 'At', 'By', 'Up', 'Out', 'Off', 'About',
        'Yeah', 'Yep', 'Nope', 'Let', 'Correct', 'Right', 'Wrong',
        'Maybe', 'Exactly', 'Actually', 'Well', 'Sure', 'Fine',
        # Common contractions (capitalized at sentence start)
        "I'm", "I've", "I'll", "I'd", "You're", "You've", "You'll", "You'd",
        "He's", "She's", "It's", "We're", "We've", "We'll", "We'd",
        "They're", "They've", "They'll", "They'd",
        "Don't", "Doesn't", "Didn't", "Won't", "Wouldn't", "Can't", "Couldn't",
        "Shouldn't", "Haven't", "Hasn't", "Hadn't", "Isn't", "Aren't", "Wasn't", "Weren't"
    }
    
    # Check if word is in common words set
    if clean_word in common_words:
        return False
    
    # If it passed all the filters, it's likely a name
    return True


def _is_common_word(word: str) -> bool:
    """Check if word is a common word that should have lower confidence threshold."""
    # Common words list - synchronized with UI config
    common_words = {
        # Articles, pronouns, basic words
        'I', 'A', 'The', 'An', 'Hello', 'Hi', 'Yes', 'No', 'Okay', 'Ok', 
        'Thank', 'Thanks', 'Please', 'Sorry', 'And', 'But', 'Or',
        'This', 'That', 'These', 'Those', 'What', 'When', 'Where',
        'Why', 'How', 'Who', 'Which', 'Of', 'So', 'To', 'From',
        'For', 'With', 'Can', 'Will', 'Was', 'Were', 'Are', 'Is', 'Be', 'Been',
        'Have', 'Has', 'Do', 'Does', 'Did', 'Would', 'Could', 'Should',
        'My', 'Your', 'Their', 'Our', 'His', 'Her', 'Its',
        'On', 'In', 'It', 'At', 'By', 'Up', 'Out', 'Off', 'About', 'As',
        'Yeah', 'Yep', 'Nope', 'Let', 'Correct', 'Right', 'Wrong',
        'Maybe', 'Exactly', 'Actually', 'Well', 'Sure', 'Fine',
        # Common action words
        'Get', 'Got', 'Give', 'Go', 'Going', 'Come', 'Want', 'Need', 'See', 'Saw',
        'Make', 'Made', 'Take', 'Took', 'Know', 'Think', 'Say', 'Said', 'Tell',
        'Ask', 'Asked', 'Call', 'Called', 'Try', 'Trying',
        # Common call center / medical words
        'Please', 'Press', 'If', 'Then', 'Just', 'Now', 'Here', 'There',
        'Through', 'Request', 'Medical', 'Department', 'Release', 'Information',
        'Number', 'Office', 'Record', 'Records', 'Patient',
        # Days of week
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
        # Contractions
        "I'm", "I've", "I'll", "I'd", "You're", "You've", "You'll", "You'd",
        "He's", "She's", "It's", "We're", "We've", "We'll", "We'd",
        "They're", "They've", "They'll", "They'd",
        "Don't", "Doesn't", "Didn't", "Won't", "Wouldn't", "Can't", "Couldn't",
        "Shouldn't", "Haven't", "Hasn't", "Hadn't", "Isn't", "Aren't", "Wasn't", "Weren't",
        # Time indicators
        "AM", "PM", "A.M.", "P.M.", "am", "pm", "a.m.", "p.m.",
        # Directions
        "North", "South", "East", "West", "north", "south", "east", "west"
    }
    
    # Also check lowercase version for case-insensitive matching
    return word in common_words or word.lower() in {w.lower() for w in common_words}


def _detect_phone_number_sequence(words: List[Dict], start_idx: int, window: int = 10) -> Optional[Tuple[int, int]]:
    """
    Detect if this is part of a spelled-out phone number sequence.
    Returns (start_index, end_index) of the phone number sequence, or None.
    """
    # Look for pattern like: "2 1 0" or "2-2-7" "8-8-2-2"
    end_idx = min(start_idx + window, len(words))
    segment_words = words[start_idx:end_idx]
    
    phone_parts = []
    current_idx = start_idx
    
    for i, wd in enumerate(segment_words):
        word = wd.get("word", "").strip(".,!?")
        
        # Check if it's a number or number-dash pattern
        if _SPELLED_NUMBER_PATTERN.match(word) or word.isdigit():
            phone_parts.append(word)
            current_idx = start_idx + i
        else:
            # Stop if we hit a non-number word
            break
        
        # If we have enough parts for a phone number, we found one
        if len(phone_parts) >= 3:  # At least area code + some digits
            return (start_idx, current_idx + 1)
    
    return None


def _flag_word(
    word_data: Dict,
    word_index: int,
    all_words: List[Dict],
    config: AssemblyAIReviewConfig,
    expected_terms: Optional[List[str]] = None
) -> List[WordFlag]:
    """
    Analyze a word and generate flags for manual review.
    
    Args:
        word_data: Word data from AssemblyAI (word, confidence, start_time, etc.)
        word_index: Index of word in transcript
        all_words: All words in transcript for context analysis
        config: Review configuration
        expected_terms: Expected terms from nouns_to_expect.txt
        
    Returns:
        List of flags for this word
    """
    flags = []
    
    word = word_data.get("word", "").strip()
    confidence = word_data.get("confidence")
    
    if not word:
        return flags
    
    # Strip punctuation for analysis
    clean_word = word.strip(".,!?;:'\"")
    
    # Check if word is in expected terms (exact or partial match)
    is_expected = False
    if expected_terms:
        clean_word_lower = clean_word.lower()
        for term in expected_terms:
            if not term:
                continue
            term_lower = term.lower()
            # Check exact match or if word is part of the term phrase
            if term_lower == clean_word_lower or clean_word_lower in term_lower.split():
                is_expected = True
                break
    
    # === CONFIDENCE-BASED FLAGS ===
    # Skip confidence flags for expected terms (we know they're correct)
    
    if confidence is not None and not is_expected:
        # Check if it's a common word (they get lower threshold)
        is_common_word = _is_common_word(clean_word)
        
        # Use different threshold for common words
        critical_threshold = config.common_words_confidence_threshold if is_common_word else config.critical_confidence_threshold
        
        if confidence < critical_threshold:
            flags.append(WordFlag(
                type="critical_confidence",
                reason=f"Critical: Very low confidence ({confidence:.2%})",
                priority="high",
                metadata={"confidence": confidence}
            ))
        elif not is_common_word and confidence < config.low_confidence_threshold:
            # Only flag low confidence for non-common words
            flags.append(WordFlag(
                type="low_confidence",
                reason=f"Low confidence ({confidence:.2%})",
                priority="medium",
                metadata={"confidence": confidence}
            ))
    
    # === PATTERN-BASED FLAGS ===
    
    # Phone numbers - check both single word and sequences
    if config.flag_phone_numbers:
        if _PHONE_PATTERN.search(word):
            flags.append(WordFlag(
                type="phone_number",
                reason="Phone number detected - verify accuracy",
                priority="high"
            ))
        elif _SPELLED_NUMBER_PATTERN.match(clean_word):
            # Check if this is part of a spelled-out phone number
            phone_seq = _detect_phone_number_sequence(all_words, word_index)
            if phone_seq:
                flags.append(WordFlag(
                    type="phone_number_segment",
                    reason="Part of spelled-out phone number - verify sequence",
                    priority="high",
                    metadata={"sequence_range": phone_seq}
                ))
    
    # Case numbers (6+ digit sequences)
    if config.flag_case_numbers and _CASE_NUMBER_PATTERN.search(clean_word):
        flags.append(WordFlag(
            type="case_number",
            reason="Possible case number - verify accuracy",
            priority="high"
        ))
    
    # Money amounts
    if config.flag_money_amounts and _MONEY_PATTERN.search(word):
        flags.append(WordFlag(
            type="money_amount",
            reason="Dollar amount detected - verify accuracy",
            priority="high"
        ))
    
    # Dates
    if config.flag_dates and _DATE_PATTERN.search(word):
        flags.append(WordFlag(
            type="date",
            reason="Date detected - verify accuracy",
            priority="medium"
        ))
    
    # Times
    if config.flag_times and _TIME_PATTERN.search(word):
        flags.append(WordFlag(
            type="time",
            reason="Time detected - verify accuracy",
            priority="medium"
        ))
    
    # Numbers in general
    if config.flag_numbers and _NUMBER_PATTERN.search(clean_word):
        # Don't double-flag if already flagged as phone/case number
        if not any(f.type in ["phone_number", "case_number", "phone_number_segment"] for f in flags):
            flags.append(WordFlag(
                type="number",
                reason="Number detected - verify accuracy",
                priority="low"
            ))
    
    # Names (proper nouns)
    if config.flag_names and _is_likely_name(clean_word):
        # Check if it's in expected terms
        is_expected = False
        if expected_terms:
            is_expected = any(
                clean_word.lower() in term.lower() 
                for term in expected_terms
            )
        
        if not is_expected:
            flags.append(WordFlag(
                type="name",
                reason="Possible name/proper noun - verify spelling",
                priority="medium"
            ))
    
    return flags


def _build_context(words: List[Dict], index: int, before: int, after: int) -> Tuple[str, str]:
    """Build context strings before and after a word."""
    start_idx = max(0, index - before)
    end_idx = min(len(words), index + after + 1)
    
    context_before = " ".join(
        w.get("word", "") for w in words[start_idx:index]
    )
    context_after = " ".join(
        w.get("word", "") for w in words[index + 1:end_idx]
    )
    
    return context_before, context_after


def generate_assemblyai_review(
    confidence_json_path: Path,
    transcript_path: Path,
    config: AssemblyAIReviewConfig,
    expected_terms: Optional[List[str]] = None
) -> Optional[Path]:
    """
    Generate a review file from AssemblyAI confidence JSON.
    
    Args:
        confidence_json_path: Path to .confidence.json file from AssemblyAI
        transcript_path: Path to .txt transcript file
        config: Review configuration
        expected_terms: Optional list of expected terms from nouns_to_expect.txt
        
    Returns:
        Path to generated review JSON file, or None if skipped
    """
    if not config.enabled:
        logger.debug("AssemblyAI review generation disabled")
        return None
    
    confidence_json_path = Path(confidence_json_path)
    transcript_path = Path(transcript_path)
    
    if not confidence_json_path.exists():
        logger.warning("Confidence JSON not found: %s", confidence_json_path)
        return None
    
    if not transcript_path.exists():
        logger.warning("Transcript not found: %s", transcript_path)
        return None
    
    # Load confidence data
    try:
        with open(confidence_json_path, "r", encoding="utf-8") as f:
            confidence_data = json.load(f)
    except Exception as e:
        logger.error("Failed to load confidence JSON: %s", e)
        return None
    
    # Validate structure [[memory:8448638]]
    if "word_data" not in confidence_data or not isinstance(confidence_data["word_data"], list):
        logger.error("Invalid confidence JSON structure: missing or invalid word_data")
        return None
    
    word_data_list = confidence_data["word_data"]
    overall_confidence = confidence_data.get("overall_confidence")
    
    if not word_data_list:
        logger.info("No words to review in confidence JSON")
        return None
    
    # Load transcript text for reference
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()
    except Exception as e:
        logger.warning("Could not load transcript text: %s", e)
        transcript_text = ""
    
    # Generate review for each word
    review_words: List[ReviewWord] = []
    flag_counts: Dict[str, int] = {}
    priority_counts: Dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    
    for idx, word_data in enumerate(word_data_list):
        word = word_data.get("word", "").strip()
        confidence = word_data.get("confidence")
        start_time = word_data.get("start_time")
        end_time = word_data.get("end_time")
        speaker = word_data.get("speaker_tag")
        
        # Generate flags
        flags = _flag_word(word_data, idx, word_data_list, config, expected_terms)
        
        # Count flags
        for flag in flags:
            flag_counts[flag.type] = flag_counts.get(flag.type, 0) + 1
            priority_counts[flag.priority] = priority_counts.get(flag.priority, 0) + 1
        
        # Build context
        context_before, context_after = _build_context(
            word_data_list,
            idx,
            config.context_words_before,
            config.context_words_after
        )
        
        review_words.append(ReviewWord(
            word=word,
            confidence=confidence,
            start_time=start_time,
            end_time=end_time,
            speaker=speaker,
            index=idx,
            flags=flags,
            context_before=context_before,
            context_after=context_after
        ))
    
    # Calculate statistics
    total_words = len(review_words)
    flagged_words = sum(1 for w in review_words if w.flags)
    
    # Prepare output
    output_dir = Path(config.output_directory) if config.output_directory else confidence_json_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{transcript_path.stem}.review.json"
    
    review_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "review_engine": "assemblyai_native",
        "confidence_file": confidence_json_path.name,
        "transcript_file": transcript_path.name,
        "config": config.to_metadata(),
        "overall_confidence": overall_confidence,
        "statistics": {
            "total_words": total_words,
            "flagged_words": flagged_words,
            "flag_percentage": round((flagged_words / total_words * 100) if total_words > 0 else 0, 1),
            "priority_counts": priority_counts,
            "average_confidence": sum(
                w.confidence for w in review_words if w.confidence is not None
            ) / len([w for w in review_words if w.confidence is not None]) if any(w.confidence for w in review_words) else None,
        },
        "flag_summary": flag_counts,
        "words": [w.to_dict() for w in review_words],
        "corrections": [],  # For tracking manual corrections
        "audit": [],  # For tracking review actions
    }
    
    # Write review file [[memory:8448638]]
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(review_data, f, indent=2, ensure_ascii=False)
        logger.info("AssemblyAI review written to %s (%d words, %d flagged)", 
                   output_path, total_words, flagged_words)
        return output_path
    except Exception as e:
        logger.error("Failed to write review file: %s", e)
        return None


def load_expected_terms(nouns_file: Path) -> List[str]:
    """Load expected terms from nouns_to_expect.txt."""
    terms = []
    
    if not nouns_file.exists():
        return terms
    
    try:
        with open(nouns_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    terms.append(line)
        logger.info("Loaded %d expected terms", len(terms))
    except Exception as e:
        logger.warning("Failed to load expected terms: %s", e)
    
    return terms


if __name__ == "__main__":
    # Quick test
    import sys
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) < 3:
        print("Usage: python assemblyai_review_generator.py <confidence.json> <transcript.txt>")
        sys.exit(1)
    
    conf_path = Path(sys.argv[1])
    trans_path = Path(sys.argv[2])
    
    config = AssemblyAIReviewConfig()
    expected = load_expected_terms(Path("config/nouns_to_expect.txt"))
    
    result = generate_assemblyai_review(conf_path, trans_path, config, expected)
    if result:
        print(f"Review generated: {result}")
    else:
        print("Review generation failed")

