# Expected Terms Fix

## Problem
Words like "Crosley", "Law", and "Firm" were being flagged individually as names, even though "Crosley Law Firm" exists in `config/nouns_to_expect.txt`.

## Root Cause
The flagging logic was only checking if individual words exactly matched expected terms, not if they were part of expected phrases.

## Solution

### 1. Updated Python Review Generator
**File**: `tools/review_tools/assemblyai_review_generator.py`

Modified `_is_proper_noun()` function to:
- Check if a word exactly matches an expected term
- Check if a word is part of any expected phrase (e.g., "Law" is part of "Crosley Law Firm")
- Split multi-word terms and check each word individually

```python
# Before: Only checked exact matches
if token_lower in normalized_terms:
    return False

# After: Checks both exact and partial matches
for term in expected_terms:
    term_lower = term.lower()
    if token_lower == term_lower:  # Exact match
        return False
    term_words = term_lower.split()
    if token_lower in term_words:  # Part of phrase
        return False
```

### 2. Updated JavaScript Converter
**File**: `tools/review_tools/assemblyai_review_ui.html`

Modified the name flagging logic in `convertConfidenceToReview()` to:
- Check against expected terms from confidence data
- Split multi-word terms and check each word
- Skip flagging if word is found in any expected term

```javascript
// Check if word is part of expected terms
const cleanWordLower = cleanWord.toLowerCase();
for (const term of confidenceData.expected_terms) {
    const termLower = term.toLowerCase();
    // Check exact match or if word is part of the term phrase
    if (termLower === cleanWordLower || 
        termLower.split(/\s+/).includes(cleanWordLower)) {
        isExpected = true;
        break;
    }
}
```

### 3. Updated Processor to Include Expected Terms
**File**: `processor.py`

Added expected terms to confidence.json output:
```python
confidence_data = {
    "transcript": result.transcript,
    "overall_confidence": result.confidence,
    "word_data": result.word_confidences,
    "metadata": result.metadata,
    "expected_terms": EXPECTED_NOUNS_LIST or []  # NEW
}
```

## How It Works Now

### Example: "Crosley Law Firm"

**nouns_to_expect.txt contains:**
- Crosley
- Crosley Law Firm
- Crosley Law

**Transcription:** "Thanks for calling Crosley Law Firm"

**Before Fix:**
- ❌ "Crosley" → Flagged as NAME
- ❌ "Law" → Flagged as NAME
- ❌ "Firm" → Flagged as NAME

**After Fix:**
- ✅ "Crosley" → NOT flagged (in expected terms)
- ✅ "Law" → NOT flagged (part of "Crosley Law Firm")
- ✅ "Firm" → NOT flagged (part of "Crosley Law Firm")

## Benefits

1. **Fewer False Positives**: Common business names, locations, and terms from your expected list won't be flagged
2. **Phrase Support**: Works with multi-word phrases like "Crosley Law Firm", "Methodist Hospital", etc.
3. **Both Generators**: Works in both Python generator and JavaScript converter
4. **Automatic**: No manual work needed - just keep `nouns_to_expect.txt` updated

## Usage

1. **Add terms to nouns_to_expect.txt:**
   ```
   Crosley
   Crosley Law Firm
   Methodist Hospital
   San Antonio
   ```

2. **Process audio files** - expected terms automatically included in confidence.json

3. **Review in UI** - terms from your list won't be flagged

4. **Both modes work:**
   - Loading `.review.json` (Python-generated)
   - Loading `.confidence.json` (JavaScript-converted)

## Testing

To test the fix:

1. Process a new audio file
2. Load the `.confidence.json` in the review UI
3. Check that words from `nouns_to_expect.txt` are NOT flagged as names
4. Verify multi-word phrases (like "Crosley Law Firm") have no individual word flags

## Notes

- Expected terms are case-insensitive (matching is done in lowercase)
- Punctuation is stripped before matching
- Terms are split on whitespace to check individual words
- Common words like "Thank", "Thanks", "Please" are still excluded even if capitalized

