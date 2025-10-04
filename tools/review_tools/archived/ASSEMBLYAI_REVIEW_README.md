# AssemblyAI Manual Review System

A dedicated manual review engine optimized for AssemblyAI transcripts, providing intelligent flagging and correction capabilities.

## Overview

The AssemblyAI Review System provides:
- **Native AssemblyAI Integration**: Uses confidence scores directly from AssemblyAI (no Whisper alignment needed)
- **Smart Pattern Detection**: Automatically flags phone numbers, dates, money amounts, names, and more
- **Priority-Based Flagging**: High/medium/low priority flags help you focus on critical corrections
- **Interactive Web UI**: Modern, user-friendly interface for reviewing and correcting transcripts
- **Correction Tracking**: Save and export your corrections with full audit trails

## Key Features

### Automatic Flagging

The system automatically flags words for review based on:

#### Confidence-Based Flags
- **Critical Confidence** (< 50%): Very low confidence - needs immediate review
- **Low Confidence** (< 70%): Below threshold - should be reviewed

#### Pattern-Based Flags
- **Phone Numbers**: Both formatted (210-555-1234) and spelled-out (2-1-0 5-5-5...)
- **Case Numbers**: 6+ digit sequences that could be case identifiers
- **Money Amounts**: Dollar amounts and financial figures
- **Dates**: Date mentions in various formats
- **Times**: Appointment times and time mentions
- **Names**: Capitalized words likely to be proper nouns
- **Numbers**: Any numeric content for accuracy verification

### Priority System

**High Priority** (🔴 Red):
- Critical confidence issues (< 50%)
- Phone numbers
- Case numbers
- Spelled-out number sequences

**Medium Priority** (🟠 Orange):
- Low confidence (50-70%)
- Money amounts
- Dates
- Names/proper nouns

**Low Priority** (🔵 Blue):
- General numbers
- Minor confidence issues

## Usage

### Automatic Review Generation

When using AssemblyAI as your transcription engine, reviews are automatically generated during processing:

1. Audio file is transcribed by AssemblyAI
2. Confidence JSON is saved with word-level data
3. Review file is automatically generated
4. Review JSON includes all flagged words with context

### Manual Review Generation

Generate a review for an existing transcript:

```bash
cd tools/review_tools
python assemblyai_review_generator.py path/to/transcript.confidence.json path/to/transcript.txt
```

### Launching the Review UI

#### Option 1: Batch File (Windows)
```bash
cd tools/review_tools
launch_assemblyai_review.bat
```

#### Option 2: Python Script
```bash
cd tools/review_tools
python launch_assemblyai_review.py
```

The UI will automatically open in your default browser at `http://localhost:8002`

## Review UI Guide

### Loading a Review File

1. Click "Load Review File" button
2. Select a `.review.json` file from your review directory
3. The system will load all words and display statistics

### Understanding the Statistics Dashboard

- **Total Words**: All words in the transcript
- **Flagged Words**: Words that need review
- **Flag Percentage**: Percentage of words flagged
- **Avg Confidence**: Overall transcript confidence
- **High Priority**: Count of critical issues
- **Corrections Made**: Your review progress

### Filtering Options

**Filter by Priority**: Focus on specific priority levels
- All Flags
- High Priority (most critical)
- Medium Priority
- Low Priority

**Filter by Type**: Focus on specific pattern types
- Phone numbers
- Case numbers
- Money amounts
- Dates/times
- Names
- Confidence issues

**Show Only Flagged**: Toggle to show all words or just flagged words

### Making Corrections

For each flagged word:

1. **Review Context**: See surrounding words for context
2. **Check Flags**: Review why the word was flagged
3. **View Metadata**: Check confidence, speaker, and timing
4. **Enter Correction**: Type the corrected word in the input field
5. **Apply**: Click "✓ Apply" to save the correction
6. **Remove**: Click "✗ Remove" to undo a correction (if needed)

### Keyboard Shortcuts

- **Ctrl+S**: Save review file with corrections

### Exporting Your Work

**Export Corrections** (💾):
- Saves a JSON file with all corrections
- Includes original/corrected word pairs
- Contains timestamps for each correction

**Export Corrected Transcript** (📄):
- Generates a new transcript with all corrections applied
- Plain text format
- Ready for use

**Save Review File** (💿):
- Saves the review JSON with embedded corrections
- Includes full audit trail
- Can be reloaded later to continue work

## Review File Format

The review JSON file contains:

```json
{
  "generated_at": "2025-10-02T10:30:00Z",
  "review_engine": "assemblyai_native",
  "confidence_file": "transcript.confidence.json",
  "transcript_file": "transcript.txt",
  "overall_confidence": 0.85,
  "statistics": {
    "total_words": 450,
    "flagged_words": 45,
    "flag_percentage": 10.0,
    "priority_counts": {
      "high": 5,
      "medium": 15,
      "low": 25
    },
    "average_confidence": 0.85
  },
  "flag_summary": {
    "phone_number": 2,
    "low_confidence": 20,
    "name": 15,
    ...
  },
  "words": [
    {
      "word": "Crosley",
      "confidence": 0.30,
      "start_time": 0.56,
      "end_time": 0.96,
      "speaker": "A",
      "index": 3,
      "flags": [
        {
          "type": "low_confidence",
          "reason": "Low confidence (30.0%)",
          "priority": "medium",
          "confidence": 0.30
        }
      ],
      "context_before": "Thanks for calling",
      "context_after": "Law Firm This is"
    },
    ...
  ],
  "corrections": [
    {
      "word_index": 3,
      "original_word": "Crosley",
      "corrected_word": "Crossley",
      "corrected_at": "2025-10-02T11:15:00Z"
    }
  ],
  "audit": [
    {
      "action": "corrections_saved",
      "timestamp": "2025-10-02T11:15:00Z",
      "corrections_count": 1
    }
  ]
}
```

## Configuration

Configure review settings in `config/call_pipeline.ini`:

```ini
[Review]
# Enable/disable review generation
Enabled = true

# Output directory for review files
OutputDirectory = .\output\Review

# Confidence threshold for flagging (0.0-1.0)
LowConfidenceThreshold = 0.70

# Pattern detection flags
FlagNumbers = true
```

## Integration with Pipeline

The AssemblyAI review system integrates automatically:

1. **Transcription** → AssemblyAI transcribes audio
2. **Confidence Export** → Word-level confidence saved
3. **Review Generation** → Automatic flagging and analysis
4. **Manual Review** → You review and correct flagged words
5. **Export** → Corrected transcript ready for use

## Best Practices

### Review Strategy

1. **Start with High Priority**: Address critical issues first
2. **Use Filters**: Focus on specific types (phone numbers, names, etc.)
3. **Check Context**: Always read surrounding words
4. **Listen to Audio**: If available, verify against original audio
5. **Save Regularly**: Use Ctrl+S or "Save Review File" frequently

### Common Scenarios

**Phone Numbers**: Always verify digit-by-digit, especially for spelled-out sequences

**Names**: Check against your staff_map.txt and nouns_to_expect.txt

**Case Numbers**: Critical for legal work - verify every digit

**Money Amounts**: Confirm exact amounts with context

**Dates/Times**: Verify appointment and deadline dates carefully

### Quality Assurance

- Review 100% of high-priority flags
- Sample-check medium and low priority flags
- Compare overall confidence with review results
- Track correction patterns to improve expected terms list

## Troubleshooting

### UI Won't Load
- Check that port 8002 is available
- Try manually opening the HTML file
- Check browser console for errors

### No Flags Showing
- Verify the review file has a "words" array
- Check filter settings (show only flagged might be hiding words)
- Ensure confidence JSON was properly generated

### Corrections Not Saving
- Check file permissions in output directory
- Ensure you clicked "Apply" before saving
- Verify JSON structure is valid

## Differences from Standard Review

The AssemblyAI review system differs from the standard review:

| Feature | Standard Review | AssemblyAI Review |
|---------|----------------|-------------------|
| **Confidence Source** | Whisper alignment | Native AssemblyAI |
| **Processing Speed** | Slower (requires Whisper) | Faster (direct data) |
| **Accuracy** | Good | Better (native scores) |
| **Pattern Detection** | Basic | Advanced |
| **Priority System** | No | Yes (3 levels) |
| **Speaker Info** | Limited | Full speaker tags |
| **UI** | Generic | AssemblyAI-optimized |

## Support

For issues or questions:
1. Check the logs in `output/Logs/call_pipeline.log`
2. Verify your AssemblyAI configuration in `call_pipeline.ini`
3. Ensure confidence JSON files are being generated
4. Review this documentation for usage tips

## Version History

**v1.0** (2025-10-02)
- Initial release
- Native AssemblyAI integration
- Pattern-based flagging
- Priority system
- Dedicated web UI
- Correction tracking and export

