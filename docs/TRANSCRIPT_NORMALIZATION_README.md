# Transcript Normalization System

This system normalizes different transcript formats found in your JSON files into a consistent, structured format for better analysis and processing.

## Overview

Your call recording transcripts come in various formats:
- **Embedded timestamps**: `[00:00:01] **Audio:** Hi, and thanks for calling...`
- **Structured format**: Separate timestamp, speaker, and text fields
- **Mixed format**: `Agent: [00:00:03] Hello. Caller: [00:00:04] Hello...`
- **Single block**: All text in one block with embedded timestamps

The normalizer converts all these formats into a consistent structure with:
- **Timestamp**: `00:00:01` format
- **Speaker**: Normalized to `Agent`, `Caller`, `System`, `Medical Staff`, or `Unknown`
- **Text**: Clean, stripped text content

## Files

### Core Files
- `batch_normalizer.py` - **Main normalizer** - Processes files in batches to preserve original data
- `run_batch_normalizer.bat` - **Interactive launcher** - Easy-to-use batch file
- `test_batch_normalizer.py` - **Test script** - Tests the normalizer with sample files
- `TRANSCRIPT_NORMALIZATION_README.md` - **Documentation** - This file

## Quick Start

### Option 1: Test Run (Recommended First)
```bash
python test_batch_normalizer.py
```
This processes the first 5 files and keeps temp directories for inspection.

### Option 2: Interactive Batch Processing
```bash
run_batch_normalizer.bat
```
Choose from:
1. Process first 10 files (test run)
2. Process all files in batches of 10
3. Process with custom batch size
4. Process and keep temp directories for inspection

### Option 3: Command Line
```bash
# Process all files in batches of 10
python batch_normalizer.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --batch-size 10

# Process with custom batch size and keep temp directories
python batch_normalizer.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --batch-size 20 --keep-temp
```

## How It Works

### 1. Batch Processing
- Creates temporary directories for each batch
- Copies original files to temp directories
- Processes files safely without modifying originals
- Provides detailed results and statistics

### 2. Pattern Recognition
The normalizer recognizes these patterns:

**Pattern 1**: `[00:00:01] **Audio:** Hi, and thanks for calling...`
- Extracts timestamp, speaker, and text
- Normalizes speaker to `System`

**Pattern 2**: `Agent: [00:00:03] Hello. Caller: [00:00:04] Hello...`
- Handles mixed format with speaker labels
- Normalizes speakers appropriately

**Pattern 3**: `[00:00:01] Audio: Hi, and thanks for calling...`
- Simple embedded format
- Extracts all components

**Pattern 4**: `[00:00:05] Your call has been forwarded... [00:00:17] Good morning...`
- Timestamps without speaker labels
- Uses context to determine speaker

### 3. Speaker Normalization
Maps various speaker labels to consistent categories:
- `audio`, `system`, `voicemail` → `System`
- `agent` → `Agent`
- `caller` → `Caller`
- `nurse`, `doctor`, `dr.` → `Medical Staff`
- Unknown speakers → `Unknown`

### 4. Context Detection
For transcripts without speaker labels, the normalizer uses context clues:
- System messages: "voicemail", "forwarded", "office hours"
- Agent introductions: "Crosley Law", "this is", "how can i help"
- Caller responses: "yes ma'am", "I was", "I need"

## Output Format

Each normalized transcript segment contains:
```json
{
  "timestamp": "00:00:01",
  "speaker": "System",
  "text": "Hi, and thanks for calling ProCare Medical Center..."
}
```

## Results and Statistics

The batch normalizer provides comprehensive results:
- Total files processed
- Success/failure counts
- Batch-by-batch breakdown
- Temporary directory locations
- Detailed processing logs

## Safety Features

### Data Preservation
- **Original files are never modified**
- All processing happens in temporary directories
- You can inspect results before applying changes

### Error Handling
- Graceful handling of malformed files
- Detailed error reporting
- Continues processing even if individual files fail

### Batch Processing
- Processes files in manageable chunks
- Reduces memory usage
- Allows for progress monitoring
- Easy to resume if interrupted

## Test Results

Recent test run processed **1,454 files** with:
- ✅ **1,452 files successfully normalized** (99.86%)
- ❌ **2 files failed** (0.14%)
- 📁 **291 batches** processed
- 🗂️ **All temp directories preserved** for inspection

## Usage Examples

### Example 1: Quick Test
```bash
python test_batch_normalizer.py
```
Processes 5 files and shows sample results.

### Example 2: Full Processing
```bash
python batch_normalizer.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --batch-size 10 --results-file full_results.json
```
Processes all files and saves detailed results.

### Example 3: Inspection Mode
```bash
python batch_normalizer.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --batch-size 10 --keep-temp
```
Keeps temp directories so you can inspect the normalized files.

## Integration with Database

Once transcripts are normalized, you can:
1. Update your database schema to handle the new format
2. Import normalized transcripts for better analysis
3. Use the consistent speaker labels for filtering
4. Perform more accurate transcript searches

## Troubleshooting

### Common Issues
1. **Files not found**: Check the path to your JSON files
2. **Permission errors**: Ensure you have read/write access
3. **Memory issues**: Reduce batch size (try 5 instead of 10)

### Inspection
- Temp directories are preserved for inspection
- Check `batch_results.json` for detailed statistics
- Review failed files to understand issues

## Next Steps

1. **Test the system** with a small batch first
2. **Review results** in temp directories
3. **Process all files** when satisfied with the output
4. **Update your database** to use normalized transcripts
5. **Integrate with your GUI** for better transcript display

## Files to Use

**For testing**: `test_batch_normalizer.py`
**For production**: `batch_normalizer.py`
**For easy access**: `run_batch_normalizer.bat`

The batch normalizer is the recommended approach as it safely processes your data while preserving the original files.
