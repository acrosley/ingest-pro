# Database Auto-Update Feature

## Overview

The call processing pipeline now includes **automatic database updates** that ensure new calls are immediately added to the SQLite database without manual intervention.

## How It Works

### Automatic Updates
- When `processor_v2.8.py` processes a new call and creates a JSON file, it automatically triggers a database update
- The system checks if the JSON file already exists in the database
- Only new files are added - existing records are skipped
- Database updates happen in real-time as calls are processed

### Manual Updates
- Use `update_database.bat` to manually update the database
- Use `update_database.bat` to view database statistics
- The manual updater can process all JSON files and add any missing records

## Files Added

### `database_updater.py`
- **Purpose**: Core database update functionality
- **Features**:
  - Connects to existing SQLite database
  - Identifies new JSON files not in database
  - Parses JSON files and inserts structured data
  - Handles entities and transcript segments
  - Provides database statistics

### `update_database.bat`
- **Purpose**: User-friendly interface for database operations
- **Options**:
  - Update database with new JSON files
  - Show database statistics

## Integration with Processor

### Automatic Integration
The `processor_v2.8.py` now includes:
```python
# Auto-update database if enabled
if DATABASE_UPDATER_ENABLED:
    try:
        updater = DatabaseUpdater(str(CENTRAL_JSON_DIR), "call_recordings.db")
        results = updater.update_database()
        if results['processed'] > 0:
            logger.info(f"[Database] Auto-updated database: {results['processed']} new calls added")
    except Exception as e:
        logger.warning(f"[Database] Failed to auto-update database: {e}")
```

### Configuration
- The feature is automatically enabled if `database_updater.py` is present
- No configuration changes required
- Graceful fallback if module is missing

## Usage

### Automatic (Default)
1. Start the processor with `run_processor.bat`
2. New calls are automatically added to database
3. Check logs for database update status

### Manual Update
```bash
# Update database with new files
python database_updater.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES"

# Show database statistics
python database_updater.py "W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES" --stats
```

### Batch File Interface
```bash
# Run update_database.bat and choose option 1 or 2
```

## Benefits

### Real-Time Synchronization
- Database is always up-to-date with latest calls
- No manual intervention required
- Immediate availability of new data for queries

### Performance
- Only processes new files
- Efficient duplicate detection
- Minimal overhead on processing pipeline

### Reliability
- Graceful error handling
- Detailed logging
- Fallback to manual updates if needed

## Database Statistics

Current database contains:
- **1,452 total calls**
- **12,206 entities extracted**
- **50,049 transcript segments**
- **11 unique agents**
- **Date range**: 2025-06-17 to 2025-08-21

## Troubleshooting

### Database Not Updating
1. Check if `database_updater.py` exists in the calls_v2 directory
2. Verify database file `call_recordings.db` exists
3. Check processor logs for database update messages
4. Run manual update to verify functionality

### Manual Update Fails
1. Ensure database was created with `create_database.py`
2. Check JSON file format and accessibility
3. Verify file permissions on database and JSON directories

### Performance Issues
1. Database updates are lightweight and shouldn't impact processing
2. If issues occur, disable auto-updates and use manual updates
3. Consider running manual updates during off-peak hours

## Migration from Manual Updates

### Before (Manual Process)
1. Process calls with `processor_v2.8.py`
2. Manually run `create_database.py` periodically
3. Database could be out of sync with latest calls

### After (Automatic Process)
1. Process calls with `processor_v2.8.py`
2. Database automatically stays synchronized
3. Manual updates available for bulk operations

## Future Enhancements

### Planned Features
- Configuration option to enable/disable auto-updates
- Batch processing for better performance
- Database backup before updates
- Incremental update scheduling

### Monitoring
- Database update metrics in processor logs
- Success/failure rate tracking
- Performance impact monitoring

## Support

For issues with database auto-updates:
1. Check the processor logs for database-related messages
2. Run `update_database.bat` to test manual functionality
3. Verify database integrity with `query_database.py`
4. Review this documentation for troubleshooting steps
