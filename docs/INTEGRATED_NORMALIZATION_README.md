# Integrated Transcript Normalization

## Overview

Transcript normalization has been integrated into the main `processor_v2.8.py` pipeline. This means that all transcripts will be automatically normalized as they are processed, ensuring consistent speaker labels and timestamps across all call recordings.

## How It Works

### 1. **Automatic Integration**
- The processor now includes a `transcript_normalizer_module.py` that contains all the normalization logic
- Transcripts are normalized during the analysis phase, before being saved to JSON
- The normalization is applied to both new transcripts and existing transcripts processed on startup

### 2. **Configuration Control**
- Normalization can be enabled/disabled via the configuration file
- Add this line to your `[Analysis]` section in `call_pipeline.ini`:
  ```ini
  EnableTranscriptNormalization = true
  ```

### 3. **Backward Compatibility**
- If the normalization module is not found, the processor falls back to legacy parsing
- If normalization fails for any reason, it falls back to legacy parsing
- Existing functionality is preserved

## Files Added/Modified

### New Files
- `transcript_normalizer_module.py` - Contains the normalization logic
- `call_pipeline_with_normalization.ini` - Sample configuration with normalization enabled
- `INTEGRATED_NORMALIZATION_README.md` - This documentation

### Modified Files
- `processor_v2.8.py` - Integrated normalization into the transcript processing pipeline

## Configuration

### Enable Normalization
Add to your `call_pipeline.ini`:
```ini
[Analysis]
EnableTranscriptNormalization = true
```

### Disable Normalization
```ini
[Analysis]
EnableTranscriptNormalization = false
```

## Benefits

### 1. **Consistent Speaker Labels**
- All speakers are normalized to: `Agent`, `Caller`, `System`, `Medical Staff`, `Unknown`
- Handles variations like "Audio:", "Voicemail:", "Operator:", etc.

### 2. **Structured Timestamps**
- Extracts timestamps from various formats: `[HH:MM:SS]`, `[MM:SS]`
- Handles embedded timestamps within text blocks

### 3. **Multiple Format Support**
- Pattern 1: `[timestamp] **Speaker:** text`
- Pattern 2: `Speaker: [timestamp] text`
- Pattern 3: `[timestamp] Speaker: text`
- Pattern 4: `[timestamp] text` (with context-based speaker detection)

### 4. **Metadata Tracking**
- Adds `normalization_info` to JSON output with:
  - `normalized_at`: When normalization occurred
  - `original_segments`: Number of original segments
  - `normalized_segments`: Number of normalized segments
  - `normalization_method`: Method used for normalization

## Example Output

### Before Normalization
```json
{
  "transcript": [
    {
      "timestamp": "",
      "speaker": "",
      "text": "[00:00:01] **Audio:** Hi, and thanks for calling... [00:00:05] Your call has been forwarded..."
    }
  ]
}
```

### After Normalization
```json
{
  "transcript": [
    {
      "timestamp": "00:00:01",
      "speaker": "System",
      "text": "Hi, and thanks for calling..."
    },
    {
      "timestamp": "00:00:05",
      "speaker": "System",
      "text": "Your call has been forwarded..."
    }
  ],
  "normalization_info": {
    "normalized_at": "2025-01-27T10:30:45.123456",
    "original_segments": 1,
    "normalized_segments": 2,
    "normalization_method": "raw_text_parsing"
  }
}
```

## Migration from Batch Normalizer

### If You Used the Batch Normalizer Previously

1. **Your existing normalized files are still valid** - no need to re-process them
2. **New files will be automatically normalized** - no need to run batch normalization
3. **You can disable normalization** if you prefer the old behavior

### To Apply Normalization to Existing Files

If you want to normalize existing files that weren't processed with the integrated normalizer:

1. **Option 1**: Set `ProcessExistingOnStart = true` in your config and restart the processor
2. **Option 2**: Use the batch normalizer tools we created earlier
3. **Option 3**: Manually run the processor on specific files

## Troubleshooting

### Normalization Not Working
1. Check that `EnableTranscriptNormalization = true` in your config
2. Verify `transcript_normalizer_module.py` is in the same directory as `processor_v2.8.py`
3. Check the logs for any normalization errors

### Fallback to Legacy Parsing
If you see warnings about "falling back to legacy parsing":
1. This is normal and expected for some edge cases
2. The processor will still work, just without normalization
3. Check the logs for specific error messages

### Performance Impact
- Normalization adds minimal processing time
- The normalization is done in-memory during analysis
- No additional disk I/O is required

## Best Practices

1. **Test with a small subset** of files first
2. **Monitor the logs** for any normalization issues
3. **Keep backups** of your original files
4. **Review the normalization results** to ensure they meet your expectations

## Future Enhancements

The integrated normalization system is designed to be extensible:
- Additional speaker mappings can be added to `speaker_mappings`
- New parsing patterns can be added to `parse_transcript_text`
- Context detection can be improved in `determine_speaker_from_context`

## Support

If you encounter issues with the integrated normalization:
1. Check the processor logs for error messages
2. Verify your configuration settings
3. Test with a simple transcript file
4. Consider temporarily disabling normalization if needed
