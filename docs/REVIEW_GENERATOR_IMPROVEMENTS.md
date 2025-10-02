# Review Generator Improvements

## Overview
This document describes the improvements made to the review generator to address the issue of excessive word flagging in the quality control review process.

## Problem Identified
The original review generator was flagging nearly every word in transcripts due to:
1. **Metadata tokenization**: Timestamps (`[00:00:02]`) and speaker labels (`**Agent:**`, `**Caller:**`) were being treated as words
2. **Overly strict thresholds**: Confidence threshold of 0.85 was too high, flagging many correctly transcribed words
3. **Poor lexicon matching**: Words were flagged as "unknown_lexicon" even when they were common English words, because only 18 specific proper nouns were in the expected terms list
4. **Alignment issues**: The Gemini transcript format wasn't being properly parsed before alignment with Whisper output

## Solution Implemented

### 1. Metadata Stripping (Critical Fix)
**File**: `tools/review_tools/review_generator.py`

Added new function `_strip_transcript_metadata()` that removes:
- Timestamps: `[00:00:02]` → removed
- Speaker labels: `**Agent:**`, `**Caller:**` → removed

**Before**:
```python
def _tokenize_transcript(text: str) -> List[str]:
    return _WORD_RE.findall(text)
```

**After**:
```python
def _tokenize_transcript(text: str) -> List[str]:
    """Tokenize transcript text after removing metadata."""
    # Strip metadata first to avoid tokenizing timestamps and speaker labels
    clean_text = _strip_transcript_metadata(text)
    return _WORD_RE.findall(clean_text)
```

**Impact**: Reduced token count from 116 (with metadata) to 79 (actual words only)

### 2. Adjusted Confidence Threshold
**Default changed**: `0.85` → `0.70`

**Rationale**: 
- 0.85 is extremely strict - even clearly audible words were flagged
- 0.70 provides a better balance between catching real issues and avoiding false positives
- Industry standard for speech recognition confidence is typically 0.60-0.75

### 3. Disabled Unknown Lexicon Flagging by Default
**Default changed**: `FlagUnknownLexicon = true` → `false`

**Rationale**:
- The expected nouns list contains only 18 proper nouns (Crosley, Oakwell, etc.)
- Common English words like "calling", "name", "transferring" were being flagged
- This feature only makes sense when:
  - You have a comprehensive lexicon of expected terms
  - Combined with low confidence scores (not standalone)

### 4. Improved Lexicon Flagging Logic
When `FlagUnknownLexicon` is enabled, it now:
- Parses multi-word terms from the expected nouns list ("Crosley Law Firm" → adds "Crosley", "Law", "Firm")
- Only flags words that are BOTH unknown AND have low confidence (< 0.80)
- Reduces false positives significantly

**Before**:
```python
if normalized_terms and normalized not in normalized_terms:
    flags.append("unknown_lexicon")
```

**After**:
```python
# Only flag if it's a significant word not in the expected terms
# AND has low confidence (to reduce false positives)
if normalized not in normalized_terms and (confidence is None or confidence < 0.80):
    flags.append("unknown_lexicon")
```

### 5. Enhanced Documentation
Added comprehensive docstring to `generate_review()` explaining:
- The two-stage transcription process (Gemini + Whisper)
- What each flag means
- The purpose of the alignment process

## Configuration Changes

### config/call_pipeline.ini
```ini
[Review]
LowConfidenceThreshold = 0.70    # Changed from 0.85
FlagUnknownLexicon = false       # Changed from true
```

## Results

### Before (Original Review):
- **Total tokens**: 116 (including timestamps and labels)
- **Flagged words**: 107 low_confidence, 27 numbers, 49 unknown_lexicon
- **Flag rate**: ~92% of all tokens flagged

### After (Improved Review):
- **Total tokens**: 79 (actual words only)
- **Expected flagged words**: ~10-20 (only genuine low-confidence words and numbers)
- **Expected flag rate**: ~15-25% (much more reasonable)

### Sample Comparison

**Original tokenization**:
```
['00', '00', '02', 'Agent', 'Thank', 'you', 'for', 'calling', ...]
```

**Improved tokenization**:
```
['Thank', 'you', 'for', 'calling', 'the', 'Crosley', 'Law', 'Firm', ...]
```

## How to Use

### Default Settings (Recommended)
The improved defaults work well for most use cases:
```ini
[Review]
Enabled = true
LowConfidenceThreshold = 0.70
FlagNumbers = true
FlagUnknownLexicon = false
```

### Enable Unknown Lexicon Checking (Advanced)
Only if you have a comprehensive expected terms list:
```ini
FlagUnknownLexicon = true
```

Then populate `config/nouns_to_expect.txt` with:
- Proper nouns (client names, company names, locations)
- Technical/legal terms specific to your practice
- Common phrases you want to verify

### Adjust Sensitivity
- **More strict** (flag more words): `LowConfidenceThreshold = 0.75`
- **More lenient** (flag fewer words): `LowConfidenceThreshold = 0.65`

## Architecture Notes

### Why Two Transcription Models?
1. **Gemini (Primary)**: Excellent overall accuracy, provides speaker diarization and timestamps
2. **Whisper (Review)**: Provides word-level confidence scores for quality control

This hybrid approach:
- Leverages Gemini's superior transcription quality
- Uses Whisper's word-level confidence as a safety check
- Allows manual review of potentially problematic words

### The Review JSON Output
The review JSON contains:
- **words**: Array of every word with timing and confidence
- **flags**: Quality indicators (low_confidence, number, unknown_lexicon)
- **flags_summary**: Count of each flag type
- **audit**: Reserved for manual review annotations

## Testing

Run the test to verify improvements:
```bash
python -c "from tools.review_tools.review_generator import _tokenize_transcript; \
           text = open('demo/Transcripts/test copy.txt').read(); \
           tokens = _tokenize_transcript(text); \
           print(f'Tokens: {len(tokens)}'); \
           print(f'Has timestamps: {\"00\" in tokens}'); \
           print(f'Has labels: {\"Agent\" in tokens}')"
```

Expected output:
```
Tokens: 79
Has timestamps: False
Has labels: False
```

## Future Enhancements

Potential improvements for consideration:
1. **Confidence calibration**: Adjust Whisper confidence scores based on empirical accuracy
2. **Context-aware flagging**: Don't flag names/nouns that appear multiple times
3. **Phonetic matching**: Use phonetic algorithms for better alignment
4. **Custom lexicon builder**: Auto-build expected terms from past transcripts
5. **Speaker-specific confidence**: Track per-agent confidence patterns

## Migration Notes

If you're upgrading from the previous version:
1. Existing review JSON files will have the old format (with timestamps/labels as tokens)
2. New reviews will use the improved format automatically
3. Consider re-running reviews on important past transcripts
4. Update any scripts that parse review JSON to expect fewer tokens

## Troubleshooting

### Still too many flags?
- Lower `LowConfidenceThreshold` to 0.65 or 0.60
- Check audio quality - poor audio leads to low confidence
- Verify Whisper model is loaded correctly

### Not enough flags?
- Raise `LowConfidenceThreshold` to 0.75 or 0.80
- Enable `FlagUnknownLexicon` with a good expected terms list
- Check that review generation is enabled in config

### Alignment issues?
- Ensure audio file matches the transcript
- Check that timestamps in transcript are accurate
- Verify Whisper model version compatibility

## Contact
For questions or issues, refer to the main project documentation.

