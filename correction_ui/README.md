# Transcript Correction UI

A streamlined, efficient tool for reviewing and correcting AI-transcribed audio with confidence-based flagging.

## Features

### 🎯 Core Features
- **Audio Sync**: Waveform visualization with click-to-seek and word-level audio playback
- **Smart Flagging**: Automatically highlights low-confidence words, names, phone numbers, dates, and more
- **Quick Editing**: Single-click to play, double-click to edit any flagged word
- **Extended Playback**: Hear words with context (1 word before + 2 after) for better intelligibility
- **Apply to All**: Fix all instances of a word at once with one click
- **Dictionary**: Add words to dictionary to stop flagging them
- **Keyboard Navigation**: Jump between flagged words with Ctrl+Arrow keys
- **Selection Editing**: Highlight text and press Enter to edit
- **Speaker Management**: Add/remove speakers, edit names, and cycle individual speaker assignments
- **Real-time Search**: Find and highlight any word in the transcript instantly
- **Export**: Generate corrected transcript files with all edits applied

### ⚡ Performance
- Optimized rendering for large transcripts (hundreds of hours)
- Minimal UI design for distraction-free correction
- Keyboard shortcuts for faster workflow

### 🎨 UI Design
- Clean, Typora-inspired editor with plain text and highlighted flags
- Color-coded word highlights:
  - 🔴 **Red**: Critical low confidence (< 30%)
  - 🟡 **Yellow**: Low confidence (< threshold)
  - 🟣 **Purple**: Names/proper nouns
  - 🟢 **Green**: Phone numbers
  - 🔵 **Blue**: Numbers
  - ✅ **Green underline**: Corrected words

## Quick Start

### 1. Launch the Tool

**Windows:**
```bash
launch.bat
```

**Mac/Linux:**
```bash
python launch.py
```

The tool will automatically:
- Start a local web server on port 8080
- Open your browser to http://localhost:8080
- Load demo data if available

### 2. Load Your Files

1. Click "Load Files" in the sidebar
2. Select your confidence JSON file (e.g., `x105_2025-07-29.10-04.027.confidence.json`)
3. Select the matching audio file (e.g., `Alex_2025-07-29_10-04_1m1s.wav`)
4. Click "Load Files"

### 3. Review and Correct

**Edit Words:**
- Click any flagged (highlighted) word
- Review the context and confidence score
- Type your correction
- Click "Apply" or press Enter

**Edit Speakers:**
- Click any speaker name (e.g., "Speaker A:")
- Enter the real name
- Click "Apply to All" to update all instances

**Navigate Audio:**
- Click anywhere on the waveform to jump to that time
- Double-click a word to play just that word
- Use the play/pause button or press Space

**Search:**
- Type in the search box to highlight matching words
- Results update in real-time

### 4. Export Corrected Transcript

- Click "💾 Export Corrected Transcript" (or press Ctrl+S)
- Two files are generated:
  1. `corrected_transcript.txt` - Clean transcript with all corrections
  2. `corrections.json` - Log of all changes made

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Space` | Play/Pause audio |
| `Ctrl+S` | Export corrected transcript |
| `Esc` | Close modal dialogs |
| `Enter` | Apply correction (in modal) or edit selection |
| `Ctrl+→` or `Ctrl+↓` | Jump to next flagged word |
| `Ctrl+←` or `Ctrl+↑` | Jump to previous flagged word |
| **Single click** word | Play audio from that point |
| **Double-click** word | Open editor for that word |

## Configuration

### Confidence Threshold
Use the slider in the sidebar to adjust what's considered "low confidence":
- **Default**: 70%
- **Lower** (e.g., 50%): Flags fewer words, faster review
- **Higher** (e.g., 85%): Flags more words, more thorough

### Flag Filters
Toggle which types of flags to show:
- ☑️ Show Low Confidence
- ☑️ Show Names
- ☑️ Show Numbers
- ☑️ Show Phone Numbers
- ☑️ Show Dates

Unchecking a filter hides those highlights but doesn't remove the flags.

## File Formats

### Input: Confidence JSON
Expected format from `assemblyai_review_generator.py`:

```json
{
  "transcript": "[00:01] Speaker A: Hello...",
  "overall_confidence": 0.85,
  "word_data": [
    {
      "word": "Hello",
      "confidence": 0.95,
      "start_time": 1.0,
      "end_time": 1.5,
      "speaker_tag": "A"
    }
  ]
}
```

### Output: Corrected Transcript
Plain text format with speaker names and timestamps:

```
[00:01] John Smith: Hello, this is John.
[00:05] Sarah Johnson: Hi John, how can I help you?
```

### Output: Corrections JSON
Log of all changes for auditing:

```json
{
  "timestamp": "2025-10-04T12:34:56.789Z",
  "corrections": {
    "42": "corrected_word",
    "87": "another_correction"
  },
  "speakerNames": {
    "A": "John Smith",
    "B": "Sarah Johnson"
  },
  "stats": {
    "totalWords": 247,
    "correctionCount": 12
  }
}
```

## Tips for Fast Correction

1. **Start with high-priority flags**: Focus on phone numbers and critical low-confidence words first
2. **Use speaker shortcuts**: Correct speaker names early to make the transcript more readable
3. **Double-click to verify**: When unsure, double-click the word to hear it in context
4. **Adjust threshold**: If too many words are flagged, lower the confidence threshold
5. **Use search**: Find and correct all instances of a problematic word quickly
6. **Save frequently**: Export periodically to avoid losing work

## Troubleshooting

**"Port already in use" error:**
- Close other applications using port 8080
- Or edit `launch.py` and change `PORT = 8080` to another number

**Audio won't play:**
- Check that the audio file format is supported (WAV, MP3, M4A)
- Make sure the audio file path is accessible to the browser

**Flags not showing:**
- Check that flag filters in the sidebar are enabled
- Verify confidence threshold isn't set too low
- Ensure confidence JSON has valid word_data

**Slow performance:**
- Close other browser tabs
- Try a smaller transcript first to test
- Ensure you're using a modern browser (Chrome, Firefox, Edge)

## Integration with Pipeline

This tool integrates with the `assemblyai_review_generator.py` module:

1. Pipeline generates confidence JSON from transcription
2. Review generator flags words based on configurable rules
3. Correction UI loads the flagged transcript
4. User makes corrections in the UI
5. Export generates corrected transcript for final use

## Requirements

- Python 3.7+
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Confidence JSON files from AssemblyAI transcription
- Audio files in WAV, MP3, or M4A format

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `assemblyai_review_generator.py` for flagging configuration
3. Check browser console for JavaScript errors (F12)

