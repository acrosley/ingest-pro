# Transcription Engines Comparison

This document compares the two transcription engines supported by the call pipeline.

## Quick Comparison

| Feature | Google Cloud STT | Google Gemini |
|---------|-----------------|---------------|
| **Word-level confidence scores** | ✅ Yes | ❌ No |
| **Word timestamps** | ✅ Yes | ⚠️ Partial (line-level) |
| **Speaker diarization** | ✅ Automatic | ⚠️ Via prompt |
| **Accuracy** | ⭐⭐⭐⭐ Very High | ⭐⭐⭐⭐⭐ Excellent |
| **Free tier** | 60 min/month | Based on API quota |
| **Cost (paid)** | $1.44-$2.16/hour | Variable |
| **Setup complexity** | Medium | Easy |
| **Processing speed** | Fast | Fast |
| **Custom vocabulary** | ✅ Yes | ✅ Via prompt |
| **Punctuation** | ✅ Automatic | ✅ Automatic |
| **Best for** | Quality control, compliance | General transcription |

## Detailed Comparison

### Google Cloud Speech-to-Text

**Strengths:**
- Provides detailed word-level confidence scores (0.0-1.0 for each word)
- Excellent speaker diarization built into the API
- Precise word-level timestamps
- Enterprise-grade quality and reliability
- Optimized models for phone calls
- Configurable via API parameters

**Limitations:**
- Requires Google Cloud account and service account setup
- More complex initial configuration
- Free tier limit of 60 minutes/month
- May be overkill for simple transcription needs

**Best Use Cases:**
- Quality assurance and compliance review
- Identifying low-confidence words that need verification
- Legal transcription requiring high accuracy metrics
- Call analytics with speaker identification
- Building training datasets with confidence metrics

**Configuration:**
```ini
[Transcription]
TranscriptionEngine = google_cloud_stt
GoogleCloudSTT_EnableWordConfidence = true
GoogleCloudSTT_EnableSpeakerDiarization = true
```

**Output Files:**
- `{filename}.txt` - Plain text transcript
- `{filename}.confidence.json` - Word-level confidence data

### Google Gemini

**Strengths:**
- Highly accurate transcription
- Easier setup (just API key)
- Excellent at understanding context and ambiguous speech
- Can follow complex transcription instructions via prompts
- Flexible with custom vocabulary via prompts
- Better at handling accents and difficult audio

**Limitations:**
- No word-level confidence scores
- Speaker diarization depends on prompt engineering
- No detailed timing information per word
- Less suitable for quality control workflows

**Best Use Cases:**
- General call transcription
- Situations where accuracy matters more than metrics
- Quick setup and deployment
- Processing calls with difficult audio or accents
- When you don't need confidence scores

**Configuration:**
```ini
[Transcription]
TranscriptionEngine = gemini
GeminiModelName = gemini-2.0-flash
```

**Output Files:**
- `{filename}.txt` - Plain text transcript

## When to Use Which Engine

### Use Google Cloud STT when:
- ✅ You need word-level confidence scores
- ✅ You're building a compliance or QA workflow
- ✅ You need to flag uncertain transcriptions for review
- ✅ You want automatic, high-quality speaker diarization
- ✅ You need precise word timestamps
- ✅ You have fewer than 60 minutes of audio per month (free tier)

### Use Gemini when:
- ✅ You just need accurate transcripts
- ✅ You're processing difficult audio or multiple accents
- ✅ You want the simplest setup
- ✅ You don't need confidence metrics
- ✅ You're already using Gemini for analysis

### Use Both (Hybrid Approach):
You can also use both engines strategically:

1. **Primary transcription with Gemini** for accuracy
2. **Re-transcribe flagged calls with Google Cloud STT** to get confidence scores

To switch between them, just update `TranscriptionEngine` in `config/call_pipeline.ini`.

## Word-Level Confidence: Why It Matters

Word-level confidence scores help you:

### 1. Quality Control
Flag transcripts with low overall confidence for manual review:
```python
if overall_confidence < 0.85:
    # Send for human review
```

### 2. Identify Problem Terms
Find specific words that are consistently misheard:
```python
low_confidence_words = [
    word for word in word_data 
    if word['confidence'] < 0.70
]
```

### 3. Legal Compliance
For legal/compliance use, you can require high confidence:
```python
critical_terms = ['settlement', 'agreement', 'liability']
for word in word_data:
    if word['word'].lower() in critical_terms:
        if word['confidence'] < 0.95:
            # Flag for verification
```

### 4. Continuous Improvement
Track which terms need to be added to your custom vocabulary:
```python
# Find names/terms that are always low confidence
# Add them to config/nouns_to_expect.txt
```

## Performance Considerations

### Processing Speed
- **Google Cloud STT**: ~2-4x real-time (5-minute call → 1-2 minutes)
- **Gemini**: ~2-3x real-time (5-minute call → 1.5-2.5 minutes)

Both are fast enough for real-time pipelines.

### Accuracy
Both engines provide excellent accuracy (95%+), but:
- **Gemini**: Slightly better with context and ambiguous words
- **Google Cloud STT**: More consistent across different audio qualities

### Cost (Beyond Free Tier)
- **Google Cloud STT**: Predictable pricing ($1.44-$2.16/hour)
- **Gemini**: Variable based on token usage

## Example: Processing 100 Calls/Month

**Scenario**: Law firm with 100 calls/month, averaging 6 minutes each = 600 minutes total

### Option 1: Google Cloud STT Only
- Free tier covers: 60 minutes
- Paid: 540 minutes = 9 hours × $2.16 = **$19.44/month**
- **Benefit**: Full confidence scores on all calls

### Option 2: Gemini Only
- Depends on Gemini API quota/pricing
- **Benefit**: Possibly higher accuracy, simpler setup

### Option 3: Hybrid (Recommended)
- Gemini for all 100 calls
- Google Cloud STT for 10-20 flagged calls only
- Free tier covers flagged calls
- **Cost**: Just Gemini API usage
- **Benefit**: Best of both worlds

## Migration Guide

### Switching from Gemini to Google Cloud STT

1. Follow [GOOGLE_CLOUD_STT_SETUP.md](./GOOGLE_CLOUD_STT_SETUP.md)
2. Update `config/call_pipeline.ini`:
   ```ini
   TranscriptionEngine = google_cloud_stt
   ```
3. Restart the processor
4. New transcripts will include `.confidence.json` files

### Switching from Google Cloud STT to Gemini

1. Update `config/call_pipeline.ini`:
   ```ini
   TranscriptionEngine = gemini
   ```
2. Restart the processor
3. Existing `.confidence.json` files remain but new ones won't be created

## Conclusion

Both engines are excellent choices:

- **For most users**: Start with **Gemini** for simplicity and accuracy
- **For compliance/QA workflows**: Use **Google Cloud STT** for confidence metrics
- **For production at scale**: Consider a **hybrid approach**

The architecture supports both, so you can easily experiment and switch based on your needs.

