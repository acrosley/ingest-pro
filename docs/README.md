# Call Transcription and Processing System

A comprehensive system for real-time call transcription, processing, and analysis using OpenAI Whisper and Google Gemini AI.

## Features

- **Live Transcription**: Real-time audio transcription using Whisper models
- **File Monitoring**: Automatic processing of audio files as they are created
- **AI Analysis**: Intelligent analysis of transcripts using Google Gemini AI
- **Staff Mapping**: Automatic identification and mapping of staff members
- **Configurable Pipeline**: Flexible configuration through INI files
- **Logging**: Comprehensive logging with rotation

## Project Structure

```text
calls_v2/
├── call_pipeline.ini                     # Global configuration
├── processor_v2.8.py                     # Live watcher: transcribe + analyze + rename
├── processor_backfill.py                 # Backfill: transcribe/analyze missed files
├── live_transcribe.py                    # Simple mic → Whisper demo (local)
├── prompts.txt                           # Analysis prompt template (for Gemini)
├── staff_map.txt                         # Staff mapping used for renaming
├── nouns_to_expect.txt                   # Optional list to bias STT for proper nouns
├── requirements.txt                      # Python dependencies
├── README.md
├── start_venv.bat                        # Create/activate venv and install deps
├── run_processor.bat                     # Activate venv and run processor_v2.8.py
├── run_backfill.bat                      # Activate venv and run processor_backfill.py
├── run_gui.bat                           # Activate venv and run Streamlit GUI
├── gui/
│   └── streamlit_gui_call_processor_control_panel.py
├── live/
│   ├── live_test.py
│   ├── websocket.py
│   └── whisper/                          # Bundled Whisper package (for local tests)
├── legacy models/                        # Previous pipeline versions
└── notes/

# Runtime folders (on shared volume configured in call_pipeline.ini)
W:\Staff_Call_Recordings\
├── <Agent>/
│   ├── Audio/                            # Incoming audio files (watched)
│   ├── Transcripts/                      # Generated .txt transcripts
│   └── Summaries/                        # Generated .md summaries
└── _Pipeline_Output/
    ├── ALL_JSON_FILES/                   # Centralized JSON outputs
    ├── Logs/
    │   ├── call_pipeline.log             # Live processor logs
    │   └── backfill_call_pipeline.log    # Backfill logs
    └── Database/
        └── processed_files.json          # De-dupe DB (transcripts already analyzed)
```

## Prerequisites

- Python 3.8 or higher
- Windows 10/11 (tested on Windows 10)
- Microphone access for live transcription
- Google Gemini API key

## Installation

1. **Clone or download the project** to your local machine

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up your Google Gemini API key**:
   ```bash
   python set_gemini_key.py
   ```
   Edit the script to include your actual API key before running.

## Configuration

### Main Configuration (`call_pipeline.ini`)

The system uses a configuration file to manage various settings:

- **Paths**: Input/output directories and file locations
- **File Monitoring**: Audio file detection and processing settings
- **Transcription**: Whisper model settings and worker configuration
- **Analysis**: AI analysis parameters and output formats
- **Gemini**: API settings and model configuration
- **Logging**: Log file settings and rotation

### Staff Mapping (`staff_map.txt`)

Map staff member names to their identifiers for consistent processing.

### Expected Nouns (`nouns_to_expect.txt`)

List of nouns that should be recognized during analysis.

## Usage

### Live Transcription

For real-time audio transcription:

```bash
python live_transcribe.py
```

This will:
- Load the Whisper model
- Start listening to your microphone
- Transcribe speech in real-time
- Display results as you speak

### File Processing Pipeline

For processing existing audio files:

```bash
python processor_v2.8.py
```

This will:
- Monitor specified directories for new audio files
- Automatically transcribe audio files
- Analyze transcripts using AI
- Generate structured output files
- Log all activities

## Quick Start Script

Use the provided batch files:
- `start_venv.bat` – one-time setup and dependency install
- `run_processor.bat` – start the live processor
- `run_backfill.bat` – process missed items (no transcript or missing JSON)
- `run_gui.bat` – launch the Streamlit control panel at `http://localhost:8501`

## Troubleshooting

- Logs are in: `W:\Staff_Call_Recordings\_Pipeline_Output\Logs`
- JSON outputs: `W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES`
- Transcripts: `W:\Staff_Call_Recordings\<Agent>\Transcripts`
- Summaries: `W:\Staff_Call_Recordings\<Agent>\Summaries`

## Development

### Adding New Features

1. The system is modular and can be extended easily
2. New analysis types can be added to the AI processing pipeline
3. Additional audio formats can be supported by extending the file monitoring

### Version History

- **v2.8**: Current stable version with comprehensive processing pipeline
- **Legacy models**: Previous versions available in the `legacy models/` directory

## License

This project is for internal use at Crosley Law Firm.

## Support

For issues or questions, check the logs first, then consult the configuration files and documentation in the `notes/` directory. 