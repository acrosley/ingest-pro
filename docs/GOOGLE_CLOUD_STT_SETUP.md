# Google Cloud Speech-to-Text Setup Guide

This guide will help you set up Google Cloud Speech-to-Text API for your call transcription pipeline.

## Why Google Cloud Speech-to-Text?

Google Cloud Speech-to-Text provides several advantages over other transcription services:

- **Word-level confidence scores**: Get confidence ratings for each transcribed word (0.0 to 1.0)
- **Speaker diarization**: Automatically identifies different speakers in the conversation
- **High accuracy**: Enterprise-grade transcription quality
- **Word timestamps**: Precise timing information for each word
- **Free tier**: 60 minutes of transcription per month for free
- **Enhanced models**: Phone call optimized models for better accuracy

Reference: [Google Cloud Speech-to-Text API Documentation](https://cloud.google.com/speech-to-text/docs/apis)

## Prerequisites

- A Google account
- Python 3.7 or higher
- The `ingest_pro` project installed and working

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "New Project"
4. Give your project a name (e.g., "Call Transcription")
5. Click "Create"

### 2. Enable the Speech-to-Text API

1. In the Google Cloud Console, make sure your new project is selected
2. Go to the [Speech-to-Text API page](https://console.cloud.google.com/apis/library/speech.googleapis.com)
3. Click "Enable"

### 3. Create a Service Account

1. Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Fill in the details:
   - **Service account name**: `call-transcription-sa` (or any name you prefer)
   - **Service account description**: "Service account for call transcription"
4. Click "Create and Continue"
5. Grant the service account the "Cloud Speech Client" role:
   - In the "Role" dropdown, search for "Cloud Speech Client"
   - Select it
6. Click "Continue"
7. Click "Done"

### 4. Create and Download Credentials

1. On the Service Accounts page, find the service account you just created
2. Click on it to open its details
3. Go to the "Keys" tab
4. Click "Add Key" > "Create new key"
5. Select "JSON" as the key type
6. Click "Create"
7. A JSON file will be downloaded to your computer
8. **Important**: Save this file in a secure location and remember the path

### 5. Install Required Python Package

Open PowerShell or Command Prompt and activate your virtual environment:

```powershell
cd "C:\Users\Andrew.CLF\OneDrive - Crosley Law Firm\Desktop\ingest_pro"
.\venv\Scripts\activate
pip install google-cloud-speech
```

### 6. Configure Credentials in the Project

Run the credentials setup script:

```powershell
python config/set_google_cloud_credentials.py
```

When prompted:
1. Enter the full path to the JSON credentials file you downloaded
2. The script will validate the file and store the path securely in your system's keyring

Example:
```
Enter the path to your Google Cloud credentials JSON file: C:\Users\Andrew.CLF\Downloads\call-transcription-sa-key.json

✓ Valid credentials file found!
  Project ID: call-transcription-12345

✓ Credentials path stored securely in keyring!
```

### 7. Configure the Pipeline

The configuration file `config/call_pipeline.ini` has already been updated with Google Cloud STT settings. You can customize them:

```ini
[Transcription]
# Choose the transcription engine
TranscriptionEngine = google_cloud_stt

# Google Cloud STT settings
GoogleCloudSTT_LanguageCode = en-US
GoogleCloudSTT_Model = latest_long
GoogleCloudSTT_UseEnhanced = true
GoogleCloudSTT_EnableWordConfidence = true
GoogleCloudSTT_EnableWordTimeOffsets = true
GoogleCloudSTT_EnableAutomaticPunctuation = true
GoogleCloudSTT_EnableSpeakerDiarization = true
GoogleCloudSTT_DiarizationSpeakerCount = 2
```

### Configuration Options Explained

- **TranscriptionEngine**: Set to `google_cloud_stt` to use Google Cloud, or `gemini` for Gemini API
- **GoogleCloudSTT_LanguageCode**: Language code (e.g., `en-US`, `es-ES`)
- **GoogleCloudSTT_Model**: Recognition model
  - `latest_long`: Best for longer audio (phone calls, videos)
  - `latest_short`: Best for short audio (voice commands)
  - `phone_call`: Optimized specifically for phone call audio
- **GoogleCloudSTT_UseEnhanced**: Use enhanced models for better accuracy (may cost more)
- **GoogleCloudSTT_EnableWordConfidence**: Enable word-level confidence scores
- **GoogleCloudSTT_EnableWordTimeOffsets**: Include precise timestamps for each word
- **GoogleCloudSTT_EnableAutomaticPunctuation**: Automatically add punctuation
- **GoogleCloudSTT_EnableSpeakerDiarization**: Identify different speakers
- **GoogleCloudSTT_DiarizationSpeakerCount**: Expected number of speakers (typically 2 for calls)

## Word-Level Confidence Scores

When using Google Cloud STT, confidence data is automatically saved alongside your transcripts:

**Location**: `{user_base_dir}/Transcripts/{filename}.confidence.json`

**Example confidence file**:
```json
{
  "transcript": "Agent: Hello, how can I help you today?\nCaller: I need help with my account.",
  "overall_confidence": 0.94,
  "word_data": [
    {
      "word": "Hello",
      "confidence": 0.98,
      "start_time": 0.5,
      "end_time": 0.8,
      "speaker_tag": 1
    },
    {
      "word": "how",
      "confidence": 0.95,
      "start_time": 0.9,
      "end_time": 1.1,
      "speaker_tag": 1
    }
  ],
  "metadata": {
    "service": "google_cloud_stt",
    "language_code": "en-US",
    "model": "latest_long"
  }
}
```

### Using Confidence Scores

You can use confidence scores to:
- **Identify uncertain transcriptions**: Words with confidence < 0.7 may need review
- **Quality control**: Flag calls with low overall confidence for manual review
- **Improve prompts**: Identify commonly misheard terms and add them to `nouns_to_expect.txt`
- **Training data**: Use high-confidence transcripts for training or validation

## Pricing

Google Cloud Speech-to-Text pricing (as of 2024-2025):

- **Free tier**: 60 minutes per month
- **Standard models**: $0.006 per 15 seconds ($1.44 per hour)
- **Enhanced models**: $0.009 per 15 seconds ($2.16 per hour)
- **Data logging opt-in discount**: 50% off if you allow Google to use your data

For most small law firms processing 60-100 calls per month (5-10 minutes each), the free tier should be sufficient.

**Monitoring your usage**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "Billing" > "Reports"
3. Filter by "Speech-to-Text API"

## Testing

Test the setup with the demo audio file:

```powershell
# Make sure the configuration is set to Google Cloud STT
python processor.py
```

Then copy a test audio file to the watched directory and verify:
1. A transcript file is created
2. A `.confidence.json` file is created
3. Check the log file for "[STT] Transcription engine: google_cloud_stt"

## Switching Between Engines

You can easily switch between Google Cloud STT and Gemini:

1. Open `config/call_pipeline.ini`
2. Change the `TranscriptionEngine` setting:
   - For Google Cloud STT: `TranscriptionEngine = google_cloud_stt`
   - For Gemini: `TranscriptionEngine = gemini`
3. Restart the processor

## Troubleshooting

### "Google Cloud credentials not found"

- Make sure you ran `config/set_google_cloud_credentials.py`
- Verify the credentials file still exists at the stored path
- Re-run the setup script

### "Permission denied" or "API not enabled"

- Make sure you enabled the Speech-to-Text API in your Google Cloud project
- Verify the service account has the "Cloud Speech Client" role

### "Quota exceeded"

- You've used more than 60 minutes this month on the free tier
- Check your usage in the Google Cloud Console
- Consider enabling billing or wait until next month

### "No transcription results"

- The audio quality may be too poor
- Try a different audio file
- Check if the language code matches your audio
- Try the `phone_call` model instead of `latest_long`

### Import Error: "No module named 'google.cloud.speech'"

```powershell
pip install google-cloud-speech
```

## Advanced Configuration

### Custom Models

If you have a Google Cloud custom model:

```ini
GoogleCloudSTT_Model = projects/YOUR_PROJECT_ID/locations/global/models/YOUR_MODEL_ID
```

### Alternative Language Codes

Common language codes:
- English (US): `en-US`
- English (UK): `en-GB`
- Spanish: `es-ES`
- French: `fr-FR`
- German: `de-DE`

Full list: [Supported Languages](https://cloud.google.com/speech-to-text/docs/languages)

## Support

For issues specific to:
- **Google Cloud STT API**: [Google Cloud Support](https://cloud.google.com/support)
- **This integration**: Check the logs in `output/Logs/call_pipeline.log`

## References

- [Google Cloud Speech-to-Text Documentation](https://cloud.google.com/speech-to-text/docs)
- [API Reference](https://cloud.google.com/speech-to-text/docs/apis)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
- [Best Practices](https://cloud.google.com/speech-to-text/docs/best-practices)

