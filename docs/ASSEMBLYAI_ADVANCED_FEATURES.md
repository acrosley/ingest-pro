# AssemblyAI Advanced Features Guide

This guide explains all the advanced features available in AssemblyAI and when to use them.

## 📋 Quick Reference

| Feature | Use Case | Default | Recommended For |
|---------|----------|---------|-----------------|
| **Word Boost** | Improve accuracy for specific terms | ON | Legal terms, names |
| **PII Redaction** | Privacy/HIPAA compliance | OFF | Sensitive data |
| **Dual Channel** | Separate speaker tracks | OFF | High-quality recordings |
| **Summarization** | Auto-generate summaries | OFF | Quick reviews |
| **Entity Detection** | Extract names, places, orgs | OFF | Analytics |
| **Sentiment Analysis** | Detect emotions | OFF | Call quality |
| **Auto Highlights** | Key moments | OFF | Long calls |
| **Content Safety** | Flag sensitive content | OFF | Compliance |

---

## 🎯 Core Transcription Features

### **1. Speaker Labels (Diarization)**
```ini
AssemblyAI_EnableSpeakerLabels = true
```

**What it does:** Automatically identifies different speakers in the conversation.

**Output:**
```
[00:00] Speaker A: Hello, thank you for calling Crosley Law Firm
[00:05] Speaker B: Hi, I need help with my case
```

**When to use:**
- ✅ Always (enabled by default)
- Most calls have 2+ speakers (agent + caller)

**When NOT to use:**
- ❌ Single speaker recordings (like voicemails)

---

### **2. Dual Channel / Multichannel**
```ini
AssemblyAI_DualChannel = false
```

**What it does:** Transcribes stereo recordings where each speaker is on a separate audio channel.

**When to use:**
- ✅ You have professional call recording with **separate tracks** for agent and caller
- ✅ Your audio files are stereo with different audio on left/right channels

**When NOT to use:**
- ❌ Regular phone recordings (mono)
- ❌ Conference calls mixed into single channel

**How to check:**
```powershell
python tools/detect_audio_format.py "your_audio.wav"
# Look for "Channels: 2"
```

---

## 🔍 Accuracy Enhancement

### **3. Word Boost**
```ini
AssemblyAI_EnableWordBoost = true
AssemblyAI_WordBoostParam = default
```

**What it does:** Boosts recognition accuracy for specific words/phrases from `config/nouns_to_expect.txt`.

**How it works:**
- Reads terms from `nouns_to_expect.txt`
- Tells AssemblyAI to prioritize these words
- Improves accuracy for legal terms, client names, company names

**Example:**
```
# nouns_to_expect.txt
Crosley Law Firm
Samir Ouais
Metro Methodist Hospital
```

**Word Boost Param options:**
- `default` - Standard boost (recommended)
- `low` - Subtle boost
- `high` - Strong boost (use if words still missed)

**When to use:**
- ✅ Always (enabled by default)
- Essential for legal/medical terminology
- Critical for proper names

---

## 🔒 Privacy & Compliance

### **4. PII (Personally Identifiable Information) Redaction**
```ini
AssemblyAI_RedactPii = false
AssemblyAI_RedactPiiAudio = false
AssemblyAI_RedactPiiPolicies = medical_process,person_name,phone_number,ssn
```

**What it does:** Automatically detects and redacts sensitive information.

**PII Types You Can Redact:**
- `medical_process` - Medical procedures
- `medical_condition` - Health conditions
- `injury` - Injury descriptions
- `blood_type` - Blood types
- `drug` - Medication names
- `date_of_birth` - Birthdays
- `drivers_license` - Driver's license numbers
- `email_address` - Email addresses
- `location` - Specific addresses
- `money_amount` - Financial amounts
- `person_name` - Names of people
- `phone_number` - Phone numbers
- `credit_card_number` - CC numbers
- `credit_card_cvv` - CVV codes
- `credit_card_expiration` - CC expiration dates
- `ssn` - Social Security Numbers

**Output examples:**

**Original:**
```
"My name is John Smith and my SSN is 123-45-6789"
```

**With PII Redaction:**
```
"My name is [PERSON_NAME] and my SSN is [SSN]"
```

**When to use:**
- ✅ HIPAA-regulated environments
- ✅ Storing transcripts in insecure locations
- ✅ Sharing transcripts with third parties
- ✅ Privacy compliance requirements

**When NOT to use:**
- ❌ Internal case management (you need the actual info)
- ❌ Legal proceedings (need exact transcript)

**Audio Redaction:**
Set `AssemblyAI_RedactPiiAudio = true` to also redact the audio file (replaces with beeps).

---

## 📝 Formatting Options

### **5. Punctuation & Text Formatting**
```ini
AssemblyAI_Punctuate = true
AssemblyAI_FormatText = true
```

**What it does:**
- Adds punctuation (periods, commas, question marks)
- Formats text properly (capitalization, etc.)

**Example:**

**Without formatting:**
```
hello how can i help you today im calling about my case
```

**With formatting:**
```
Hello, how can I help you today? I'm calling about my case.
```

**When to use:**
- ✅ Always (enabled by default)
- Makes transcripts readable

---

### **6. Disfluencies Filter**
```ini
AssemblyAI_DisfluenciesFilter = false
```

**What it does:** Removes filler words like "um", "uh", "like", "you know".

**Example:**

**Without filter:**
```
Um, so like, I was wondering, you know, if you could help me
```

**With filter:**
```
So I was wondering if you could help me
```

**When to use:**
- ✅ Client-facing transcripts
- ✅ Formal documentation
- ✅ Reports and summaries

**When NOT to use:**
- ❌ Legal proceedings (need verbatim)
- ❌ Compliance audits (need exact words)
- ❌ Quality assurance (filler words may indicate uncertainty)

---

## 📊 Advanced Analysis

### **7. Summarization**
```ini
AssemblyAI_Summarization = false
AssemblyAI_SummaryModel = informative
AssemblyAI_SummaryType = bullets
```

**What it does:** AI-generated summary of the conversation.

**Summary Models:**
- `informative` - Detailed, comprehensive summary
- `conversational` - Natural language summary
- `catchy` - Brief, attention-grabbing summary

**Summary Types:**
- `bullets` - Bullet-point list
- `bullets_verbose` - Detailed bullet points
- `gist` - One-paragraph summary
- `headline` - Single sentence summary
- `paragraph` - Full paragraph summary

**Example Output:**
```json
{
  "summary": "- Caller inquired about case status\n- Agent confirmed hearing date\n- Scheduled follow-up call"
}
```

**When to use:**
- ✅ Long calls (>5 minutes)
- ✅ Management review
- ✅ Quick call previews

**Cost:** Adds ~$0.01 per transcript

---

### **8. Entity Detection**
```ini
AssemblyAI_EntityDetection = false
```

**What it does:** Automatically identifies and extracts:
- Person names
- Locations
- Organizations
- Dates
- Other entities

**Example Output:**
```json
{
  "entities": [
    {
      "entity_type": "person_name",
      "text": "John Smith",
      "start": 1500,
      "end": 2000
    },
    {
      "entity_type": "location",
      "text": "San Antonio",
      "start": 3000,
      "end": 3500
    }
  ]
}
```

**When to use:**
- ✅ Analytics and reporting
- ✅ CRM integration
- ✅ Database population
- ✅ Search/indexing

**Cost:** Adds ~$0.005 per transcript

---

### **9. Sentiment Analysis**
```ini
AssemblyAI_SentimentAnalysis = false
```

**What it does:** Detects sentiment (positive/neutral/negative) for each sentence.

**Example Output:**
```json
{
  "sentiment_analysis_results": [
    {
      "text": "Thank you so much for your help!",
      "sentiment": "POSITIVE",
      "confidence": 0.95
    },
    {
      "text": "I'm frustrated with this process.",
      "sentiment": "NEGATIVE",
      "confidence": 0.87
    }
  ]
}
```

**When to use:**
- ✅ Call quality monitoring
- ✅ Customer satisfaction analysis
- ✅ Agent performance review
- ✅ Identifying escalations

**Cost:** Adds ~$0.005 per transcript

---

### **10. Auto Highlights**
```ini
AssemblyAI_AutoHighlights = false
```

**What it does:** Identifies key phrases and important moments in the conversation.

**Example Output:**
```json
{
  "auto_highlights_result": {
    "results": [
      {
        "text": "settlement offer of fifty thousand dollars",
        "count": 3,
        "rank": 0.98,
        "timestamps": [{"start": 45000, "end": 47000}]
      }
    ]
  }
}
```

**When to use:**
- ✅ Long calls (>10 minutes)
- ✅ Quick review of key moments
- ✅ Training and quality review
- ✅ Finding specific topics

**Cost:** Adds ~$0.005 per transcript

---

### **11. Content Safety Detection**
```ini
AssemblyAI_ContentSafety = false
```

**What it does:** Flags sensitive content categories:
- Profanity
- Violence
- Sexual content
- Hate speech
- Self-harm
- Bullying

**Example Output:**
```json
{
  "content_safety_labels": {
    "results": [
      {
        "text": "threatening language",
        "labels": [
          {"label": "violence", "confidence": 0.89}
        ],
        "timestamp": {"start": 12000, "end": 14000}
      }
    ]
  }
}
```

**When to use:**
- ✅ Compliance monitoring
- ✅ HR investigations
- ✅ Risk management
- ✅ Content moderation

**Cost:** Adds ~$0.005 per transcript

---

## 💰 Cost Summary

| Feature | Cost Per Transcript |
|---------|---------------------|
| **Base Transcription** | $0.015/minute |
| Speaker Labels | Included |
| Timestamps | Included |
| Word Confidence | Included |
| Word Boost | Included |
| PII Redaction | Included |
| Summarization | +$0.01 |
| Entity Detection | +$0.005 |
| Sentiment Analysis | +$0.005 |
| Auto Highlights | +$0.005 |
| Content Safety | +$0.005 |

**Example:** 6-minute call with all features = $0.09 + $0.03 = **$0.12 per transcript**

---

## 🎯 Recommended Configurations

### **Basic Legal Transcription**
```ini
AssemblyAI_EnableSpeakerLabels = true
AssemblyAI_EnableWordBoost = true
AssemblyAI_Punctuate = true
AssemblyAI_FormatText = true
# Everything else = false
```
**Cost:** ~$0.09 per 6-min call

---

### **Compliance & Privacy**
```ini
AssemblyAI_EnableSpeakerLabels = true
AssemblyAI_EnableWordBoost = true
AssemblyAI_RedactPii = true
AssemblyAI_RedactPiiPolicies = person_name,phone_number,ssn,email_address
AssemblyAI_ContentSafety = true
```
**Cost:** ~$0.12 per 6-min call

---

### **Full Analytics Package**
```ini
AssemblyAI_EnableSpeakerLabels = true
AssemblyAI_EnableWordBoost = true
AssemblyAI_Summarization = true
AssemblyAI_EntityDetection = true
AssemblyAI_SentimentAnalysis = true
AssemblyAI_AutoHighlights = true
```
**Cost:** ~$0.14 per 6-min call

---

## 📚 Additional Resources

- **AssemblyAI Documentation**: https://www.assemblyai.com/docs
- **PII Redaction Guide**: https://www.assemblyai.com/docs/audio-intelligence/pii-redaction
- **Word Boost Guide**: https://www.assemblyai.com/docs/speech-to-text/custom-vocabulary
- **Pricing**: https://www.assemblyai.com/pricing

---

## 🔧 Testing Features

To test a specific feature:

1. **Enable in config:**
   ```ini
   AssemblyAI_EntityDetection = true
   ```

2. **Run test:**
   ```powershell
   python test_assemblyai.py
   ```

3. **Check output:**
   - Look in `test_results/*.json`
   - Additional features add extra fields to the JSON

4. **Review & adjust:**
   - If useful, keep enabled
   - If not needed, disable to save costs

---

**Created:** October 2, 2025
**Last Updated:** October 2, 2025

