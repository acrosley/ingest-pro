# AssemblyAI Manual Review System - Complete Setup

## 🎯 Overview

A comprehensive manual review engine specifically built for AssemblyAI transcripts. This system provides intelligent flagging, priority-based corrections, and an intuitive web interface for reviewing and correcting transcripts.

## ✨ What Was Built

### 1. Core Review Engine (`assemblyai_review_generator.py`)
- **Native AssemblyAI Integration**: Uses confidence scores directly from AssemblyAI
- **Smart Pattern Detection**: Automatically flags phone numbers, case numbers, money amounts, dates, times, and names
- **Three-Priority System**: High/Medium/Low priority flags
- **Context Awareness**: Shows surrounding words for better decision making
- **Expected Terms Integration**: Uses your `nouns_to_expect.txt` file

### 2. Interactive Web UI (`assemblyai_review_ui.html`)
- **Modern, Responsive Design**: Beautiful gradient interface with smooth animations
- **Real-time Statistics**: Dashboard showing progress and metrics
- **Advanced Filtering**: Filter by priority, type, or flagged status
- **Inline Corrections**: Edit words directly in the interface
- **Multiple Export Options**: Corrections JSON, corrected transcript, or full review file
- **Progress Tracking**: Visual progress bar and correction counter
- **Keyboard Shortcuts**: Ctrl+S to save

### 3. Launcher Scripts
- **Python Launcher** (`launch_assemblyai_review.py`): Starts local web server
- **Batch File** (`launch_assemblyai_review.bat`): Windows quick-launch
- **Test Script** (`test_assemblyai_review.py`): Validate setup

### 4. Pipeline Integration
- **Automatic Review Generation**: Reviews created during transcription
- **Engine Detection**: Uses AssemblyAI-specific review for AssemblyAI transcripts
- **Fallback Support**: Standard review for other engines
- **Configuration Sync**: Inherits settings from main config

## 🚀 Quick Start

### Step 1: Ensure AssemblyAI is Configured

In `config/call_pipeline.ini`:
```ini
[Transcription]
TranscriptionEngine = assemblyai
AssemblyAI_SpeechModel = universal  # or slam_1
AssemblyAI_ApiKey = your_key_here

[Review]
Enabled = true
LowConfidenceThreshold = 0.70
```

### Step 2: Process Some Audio Files

Run your processor to transcribe audio:
```bash
python processor.py
```

This will generate:
- `transcript.txt` - The transcript
- `transcript.confidence.json` - Confidence data
- `transcript.review.json` - Review file with flagged words

### Step 3: Launch the Review UI

#### Windows:
```bash
cd tools\review_tools
launch_assemblyai_review.bat
```

#### Or using Python:
```bash
cd tools/review_tools
python launch_assemblyai_review.py
```

The UI will open at `http://localhost:8002`

### Step 4: Load and Review

1. Click "Load Review File"
2. Select a `.review.json` file
3. Review flagged words (shown in red/orange/blue based on priority)
4. Make corrections as needed
5. Export your corrections or corrected transcript

## 📊 What Gets Flagged

### High Priority (Red) 🔴
- **Critical Confidence** (< 50%): Very unreliable transcription
- **Phone Numbers**: Like "210-555-1234" or spelled "2-1-0"
- **Case Numbers**: 6+ digit sequences
- **Phone Sequences**: "2-2-7" "8-8-2-2" patterns

### Medium Priority (Orange) 🟠
- **Low Confidence** (50-70%): Below threshold
- **Money Amounts**: "$500" or "fifty dollars"
- **Dates**: "June 23rd" or "6/23/2025"
- **Names**: Capitalized words (proper nouns)

### Low Priority (Blue) 🔵
- **Numbers**: Any numeric content
- **General Confidence**: Minor issues

## 🎨 UI Features

### Statistics Dashboard
- Total words in transcript
- Number of flagged words
- Flag percentage
- Average confidence
- High priority count
- Corrections made (your progress)

### Filtering Options
- **By Priority**: Focus on high/medium/low
- **By Type**: Phone numbers, names, dates, etc.
- **Flagged Only**: Hide unflagged words

### Word Review Card
Each word shows:
- The word itself (with corrections strikethrough)
- Confidence badge (color-coded)
- Speaker tag
- Timestamp
- Context (words before and after)
- All flags with reasons
- Correction input field

### Export Options
- **💾 Export Corrections**: JSON with all changes
- **📄 Export Corrected Transcript**: New transcript with fixes
- **💿 Save Review File**: Complete review with audit trail

## 🔧 Testing

Test the review generator:
```bash
cd tools/review_tools
python test_assemblyai_review.py
```

This will:
1. Find demo transcripts
2. Generate a test review
3. Show statistics
4. Confirm everything works

## 📁 File Locations

```
ingest_pro/
├── tools/
│   └── review_tools/
│       ├── assemblyai_review_generator.py   # Core engine
│       ├── assemblyai_review_ui.html        # Web interface
│       ├── launch_assemblyai_review.py      # Launcher
│       ├── launch_assemblyai_review.bat     # Windows launcher
│       ├── test_assemblyai_review.py        # Test script
│       └── ASSEMBLYAI_REVIEW_README.md      # Full documentation
├── output/
│   └── Review/
│       └── *.review.json                     # Generated reviews
├── demo/
│   └── Transcripts/
│       ├── *.txt                             # Transcripts
│       ├── *.confidence.json                 # Confidence data
│       └── *.review.json                     # Reviews
└── config/
    ├── call_pipeline.ini                     # Configuration
    └── nouns_to_expect.txt                   # Expected terms
```

## 🎯 Typical Workflow

### For Legal Call Reviews

1. **Transcribe**: Audio → AssemblyAI → Transcript + Confidence
2. **Auto-Review**: System generates review with flags
3. **Filter High Priority**: Focus on phone numbers, case numbers
4. **Verify Critical Info**: Double-check all high-priority flags
5. **Review Names**: Verify client and staff names
6. **Review Money/Dates**: Confirm financial and scheduling details
7. **Export**: Save corrected transcript
8. **Archive**: Keep review file with audit trail

### For Quality Assurance

1. **Load Review**: Open transcript review
2. **Check Statistics**: Review overall confidence
3. **Sample Check**: Review 100% of high priority, sample others
4. **Pattern Analysis**: Look for common mis-transcriptions
5. **Update Expected Terms**: Add commonly mis-heard terms to `nouns_to_expect.txt`
6. **Save Progress**: Regular saves with Ctrl+S

## 🔍 Understanding the Review File

The `.review.json` file contains:
- **Metadata**: When generated, source files, engine used
- **Statistics**: Totals, percentages, averages
- **Flag Summary**: Count of each flag type
- **Words Array**: Every word with confidence, timing, flags, context
- **Corrections Array**: Your edits with timestamps
- **Audit Trail**: History of review actions

## 💡 Pro Tips

### Improve Accuracy
1. **Add to nouns_to_expect.txt**: Staff names, common terms, client names
2. **Use Word Boost**: AssemblyAI will prioritize your expected terms
3. **Review Patterns**: Track common errors and adjust

### Speed Up Reviews
1. **Filter by Type**: Review all phone numbers at once
2. **Use High Priority First**: Address critical issues first
3. **Keyboard Shortcuts**: Ctrl+S to save quickly
4. **Context is King**: Read surrounding words before correcting

### Quality Assurance
1. **Check Flag Percentage**: High % might mean audio quality issues
2. **Review Confidence**: Low average might need re-transcription
3. **Audit Trail**: Track who made corrections and when
4. **Sample Testing**: QA 100% high, 50% medium, 10% low priority

## 🆚 Comparison: AssemblyAI Review vs Standard Review

| Feature | Standard Review | AssemblyAI Review |
|---------|----------------|-------------------|
| Speed | Slow (Whisper alignment) | Fast (native data) |
| Accuracy | Good | Better |
| Pattern Detection | Basic | Advanced |
| Priority System | ❌ No | ✅ Yes (3 levels) |
| Phone Detection | Basic | Spelled-out sequences too |
| Speaker Info | Limited | Full tags |
| UI | Generic | Purpose-built |
| Real-time Stats | ❌ No | ✅ Yes |
| Progress Tracking | ❌ No | ✅ Yes |
| Export Options | Limited | Multiple formats |

## 🐛 Troubleshooting

### Review Not Generated
**Problem**: No `.review.json` file created

**Solutions**:
- Check `[Review] Enabled = true` in config
- Verify confidence JSON exists
- Check logs: `output/Logs/call_pipeline.log`
- Run test script to validate

### UI Won't Load
**Problem**: Browser shows error or blank page

**Solutions**:
- Check port 8002 is available
- Try manually opening HTML file
- Check browser console (F12) for errors
- Use different browser

### No Words Flagged
**Problem**: Review shows zero flagged words

**Solutions**:
- Check confidence threshold settings
- Verify pattern flags are enabled
- Transcript might be very high quality (good!)
- Review filter settings (show only flagged)

### Corrections Not Saving
**Problem**: Edits don't persist

**Solutions**:
- Click "✓ Apply" before saving
- Check file permissions in output directory
- Use "💿 Save Review File" to persist
- Check browser console for JavaScript errors

## 📚 Additional Resources

- **Full Documentation**: `tools/review_tools/ASSEMBLYAI_REVIEW_README.md`
- **AssemblyAI Docs**: https://www.assemblyai.com/docs/
- **Main Project README**: `docs/README.md`

## 🎉 Next Steps

1. **Process your first transcript** with AssemblyAI
2. **Launch the review UI** and explore
3. **Review a sample transcript** to learn the interface
4. **Set up your workflow** based on your needs
5. **Customize expected terms** in `nouns_to_expect.txt`
6. **Train your team** on the review process

---

## Support

The AssemblyAI Review System is fully integrated into your call pipeline. For questions:
1. Review this documentation
2. Check the detailed README in `tools/review_tools/`
3. Run the test script to validate your setup
4. Check logs for error details

**Happy Reviewing! 🎯**

