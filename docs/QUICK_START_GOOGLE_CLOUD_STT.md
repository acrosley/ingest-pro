# Quick Start: Google Cloud Speech-to-Text

Get word-level confidence scores in your transcripts in 5 steps!

## Prerequisites
- Google account
- The `ingest_pro` project already working

## Setup (5-10 minutes)

### Step 1: Google Cloud Setup
1. Go to https://console.cloud.google.com/
2. Create a new project (e.g., "Call Transcription")
3. Enable the Speech-to-Text API: https://console.cloud.google.com/apis/library/speech.googleapis.com

### Step 2: Create Service Account
1. Go to https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click "Create Service Account"
3. Name: `call-transcription-sa`
4. Grant role: "Cloud Speech Client"
5. Click "Done"

### Step 3: Download Credentials
1. Click on your new service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose "JSON" and download
5. Save the file somewhere secure (e.g., `C:\GoogleCloudKeys\call-transcription.json`)

### Step 4: Install and Configure
Open PowerShell:
```powershell
cd "C:\Users\Andrew.CLF\OneDrive - Crosley Law Firm\Desktop\ingest_pro"
.\venv\Scripts\activate
pip install google-cloud-speech
python config/set_google_cloud_credentials.py
```

When prompted, enter the path to your JSON file.

### Step 5: Update Configuration
The config file is already set to use Google Cloud STT! Just verify in `config/call_pipeline.ini`:
```ini
TranscriptionEngine = google_cloud_stt
```

## Done! 🎉

Run your processor as normal:
```powershell
python processor.py
```

New transcripts will include:
- `{filename}.txt` - The transcript
- `{filename}.confidence.json` - Word-level confidence scores!

## What You Get

Each `.confidence.json` file contains:
- Overall confidence score
- Per-word confidence scores (0.0 - 1.0)
- Word timestamps
- Speaker identification

Example:
```json
{
  "overall_confidence": 0.94,
  "word_data": [
    {
      "word": "Hello",
      "confidence": 0.98,
      "start_time": 0.5,
      "end_time": 0.8
    }
  ]
}
```

## Free Tier
- 60 minutes per month FREE
- After that: ~$2/hour

For most firms processing 60-100 short calls/month, the free tier is enough!

## Need Help?
- Full documentation: `docs/GOOGLE_CLOUD_STT_SETUP.md`
- Engine comparison: `docs/TRANSCRIPTION_ENGINES_COMPARISON.md`
- Troubleshooting: Check `output/Logs/call_pipeline.log`

## Switch Back to Gemini Anytime
Just change in `config/call_pipeline.ini`:
```ini
TranscriptionEngine = gemini
```

