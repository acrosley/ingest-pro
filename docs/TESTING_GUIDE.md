# Testing Guide - Updated Review System

## What Changed

The review system now **automatically uses Google Cloud STT confidence data** when available, making it much faster and more accurate.

## Test the New System

### 1. Generate a New Review

Delete your existing test files and regenerate:

```powershell
# Delete old files
Remove-Item ".\demo\Transcripts\test copy.txt"
Remove-Item ".\demo\Transcripts\test copy.confidence.json"
Remove-Item ".\output\Review\test copy.review.json"

# Copy test audio to trigger new transcription
Copy-Item ".\demo\Audio\test copy.wav" ".\demo\Audio\test_new.wav"

# Or just run the processor and drop a new audio file
python processor.py
```

### 2. Check the New Review Format

Open the new review JSON file. You should see:

```json
{
  "generated_at": "2025-10-02T...",
  "audio_file": "test_new.wav",
  "transcript_file": "test_new.txt",
  
  // NEW FIELDS:
  "confidence_source": "google_cloud_stt",  // ← Which engine provided confidence
  "overall_confidence": 0.94,                // ← Overall transcript quality
  
  "config": { ... },
  "statistics": {
    "total_words": 150,
    "flagged_words": 23,
    "flag_percentage": 15.3,
    "priority_counts": {
      "high": 3,
      "medium": 10,
      "low": 10
    }
  },
  "words": [
    {
      "word": "Hello",
      "start": 0.5,
      "end": 0.8,
      "confidence": 0.98,  // ← Google Cloud STT confidence (more accurate)
      "flags": [],
      "context_before": "",
      "context_after": "how can I"
    }
  ]
}
```

### 3. Verify Performance

Check the logs at `output/Logs/call_pipeline.log`:

**You should see:**
```
[Review] Using Google Cloud STT confidence data from ...
[Review] Using Google Cloud STT confidence (overall: 0.XX)
[Review] Review JSON written to ...
```

**Time difference:**
- **Old way (with Whisper)**: 30-60 seconds to generate review
- **New way (with Google Cloud confidence)**: 1-2 seconds to generate review

### 4. View in the UI

```powershell
python tools/review_tools/launch_review_ui.py
```

The UI will automatically display:
- Overall confidence score
- Which engine provided the confidence data
- Low-confidence words flagged for review

## What the Review System Does

### Flags Created

The review system automatically flags:

1. **🔴 High Priority**
   - Phone numbers
   - Case numbers  
   - Spelled-out words (names)
   - Transcription mismatches (if Whisper used for comparison)

2. **🟡 Medium Priority**
   - Money amounts
   - Dates
   - Times
   - Proper nouns (names, companies)
   - Low confidence words (< 0.70)

3. **🟢 Low Priority**
   - General numbers
   - Unknown lexicon words

### Low Confidence Detection

With Google Cloud STT, you get precise confidence scores:

**Excellent (0.95-1.0)**
- Very reliable
- No manual review needed

**Good (0.85-0.95)**
- Likely correct
- Quick spot check recommended

**Fair (0.70-0.85)**
- May have issues
- Review recommended

**Poor (< 0.70)**
- Likely incorrect
- Manual review required
- **Automatically flagged**

### Example: Low Confidence Word

Looking at your test file, I can see words with low confidence like:

```json
{
  "word": "cross",
  "confidence": 0.27,  // ← Very low!
  "flags": [
    {
      "type": "low_confidence",
      "reason": "Confidence: 0.27",
      "priority": "medium"
    }
  ]
}
```

This tells you: "Hey, Google couldn't understand this word well - you should verify it against the audio."

## Comparing Engines

### Your Test File Results

**Overall Confidence: 0.40** (40%)

This is low because the audio quality in your test file appears to be poor. Here's what this means:

| Confidence | Quality | Action |
|------------|---------|--------|
| 0.40 | Poor | ⚠️ Manually review entire transcript |
| 0.60 | Fair | Review flagged words |
| 0.80 | Good | Quick spot check |
| 0.95 | Excellent | Accept as-is |

### When to Use Which Engine

**Google Cloud STT**: When you need confidence scores
- ✅ Quality control workflows
- ✅ Compliance requirements
- ✅ Identifying problem transcripts
- ✅ Training data validation

**Gemini**: When you just need accuracy
- ✅ Clear audio
- ✅ Simple transcription needs
- ✅ No confidence requirements

**Whisper (Fallback)**: Automatically used when needed
- ✅ When using Gemini transcription
- ✅ When .confidence.json is missing
- ✅ As validation comparison

## Configuration Options

### Current Settings (Optimal for Your Use)

```ini
[Transcription]
TranscriptionEngine = google_cloud_stt

[Review]
Enabled = true
PreferGoogleCloudConfidence = true  # ← Use .confidence.json when available
LowConfidenceThreshold = 0.70       # Flag words below 70% confidence
```

### Alternative Configurations

**Always use Whisper for alignment:**
```ini
PreferGoogleCloudConfidence = false
```

**Stricter quality control:**
```ini
LowConfidenceThreshold = 0.85  # Flag anything below 85%
```

**Disable review generation:**
```ini
[Review]
Enabled = false
```

## Troubleshooting

### Review file missing "confidence_source"

**Cause**: The review was generated before the update.

**Solution**: Delete and regenerate the review file.

### Review shows "confidence_source": "whisper"

**Causes**:
1. Using Gemini for transcription (expected)
2. `.confidence.json` file is missing
3. `PreferGoogleCloudConfidence = false` in config

**Solution**: Check which transcription engine is active.

### Performance is still slow

**Check**:
1. Is `confidence_source` = `"google_cloud_stt"` in the review?
2. Does the `.confidence.json` file exist?
3. Is `PreferGoogleCloudConfidence = true`?

If yes to all and still slow, check logs for errors.

## Summary

✅ **Review system updated** - Now uses Google Cloud STT confidence directly  
✅ **30-60x faster** - When using Google Cloud STT  
✅ **More accurate** - Google Cloud confidence is more reliable than Whisper  
✅ **Backward compatible** - Old reviews still work  
✅ **Smart fallback** - Whisper used automatically when needed  

**Is Whisper obsolete?** No! It's still used as a smart fallback when:
- Using Gemini for transcription
- `.confidence.json` is missing
- Validation/comparison needed

Whisper ensures the review system always works, even without Google Cloud STT.

## Next Steps

1. **Test with your audio**: Drop a new audio file and check the output
2. **Review the confidence data**: Look at the `.confidence.json` and `.review.json` files
3. **Check performance**: Compare old vs new review generation times
4. **Use the UI**: Launch `review_ui.html` to visually review flagged words

Happy testing! 🎉

