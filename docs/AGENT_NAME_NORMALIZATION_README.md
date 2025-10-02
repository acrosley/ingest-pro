# Agent Name Normalization

## Overview

The agent name normalization system consolidates duplicate agent entries in the database to ensure consistent reporting and analysis. This addresses the issue where some agents had both first-name-only entries (e.g., "Alex") and full-name entries (e.g., "Alex Alvarez").

## Problem Solved

Before normalization, the database contained duplicate agent entries:
- **Alex** (50 calls) and **Alex Alvarez** (307 calls)
- **Andrew** (92 calls) and **Andrew Crosley** (218 calls)
- **Carlos** (83 calls) and **Carlos Oliva** (214 calls)
- **Ashley** (50 calls) and **Ashley Casanova** (232 calls)
- **Jeff** (39 calls) and **Jeff Greene** (82 calls)

This caused:
- Inflated agent counts in reports
- Split analytics across duplicate entries
- Confusion in search and filtering

## Solution

The normalization system:
1. **Consolidates duplicates** by merging first-name entries into full-name entries
2. **Preserves data integrity** by maintaining all call records
3. **Standardizes format** using full names as the standard
4. **Prevents future duplicates** by normalizing new entries during import

## Files

### Core Scripts
- `normalize_agent_names.py` - Main normalization script with interactive prompts
- `normalize_agents.bat` - Batch script for easy execution
- `agent_name_utils.py` - Utility functions for agent name management

### Analysis Tools
- `analyze_agent_names.py` - Analyzes current agent names and identifies duplicates

### Integration
- `database_updater.py` - Updated to normalize agent names during new data import

## Usage

### One-Time Normalization

Run the normalization script to fix existing duplicates:

```bash
# Interactive mode with prompts
python normalize_agent_names.py

# Or use the batch script
normalize_agents.bat
```

The script will:
1. Analyze current agent names
2. Show proposed changes
3. Create a database backup
4. Apply normalization after confirmation
5. Verify results

### Automatic Normalization

New agent names are automatically normalized when:
- New JSON files are processed by `processor_v2.8.py`
- Database is updated via `database_updater.py`

## Results

After normalization:
- **Before**: 11 unique agents (with duplicates)
- **After**: 6 unique agents (consolidated)

### Final Agent List
1. **Alex Alvarez** - 357 calls (consolidated from "Alex" + "Alex Alvarez")
2. **Andrew Crosley** - 310 calls (consolidated from "Andrew" + "Andrew Crosley")
3. **Carlos Oliva** - 297 calls (consolidated from "Carlos" + "Carlos Oliva")
4. **Ashley Casanova** - 282 calls (consolidated from "Ashley" + "Ashley Casanova")
5. **Jeff Greene** - 121 calls (consolidated from "Jeff" + "Jeff Greene")
6. **Denise Strauss** - 5 calls (no duplicates)

## Normalization Rules

The system uses these rules to determine the standard name:
1. **Prefer full names** over first names only
2. **Use the entry with more calls** when multiple full names exist
3. **Maintain consistency** across all records

### Standard Mapping
```python
{
    'Alex': 'Alex Alvarez',
    'Andrew': 'Andrew Crosley',
    'Carlos': 'Carlos Oliva', 
    'Ashley': 'Ashley Casanova',
    'Jeff': 'Jeff Greene'
}
```

## Safety Features

- **Database backup** created before any changes
- **Dry run mode** shows proposed changes without applying them
- **Interactive confirmation** required before making changes
- **Verification step** confirms successful normalization

## Benefits

1. **Accurate Reporting** - Single entry per agent for consistent analytics
2. **Better Search** - Unified agent filtering and search results
3. **Cleaner Data** - Eliminates confusion from duplicate entries
4. **Future-Proof** - Prevents new duplicates from being created

## Maintenance

### Adding New Agents

To add new agents to the normalization mapping, edit `agent_name_utils.py`:

```python
def get_agent_normalization_mapping():
    return {
        'Alex': 'Alex Alvarez',
        'Andrew': 'Andrew Crosley',
        # Add new mappings here
        'NewAgent': 'New Agent Full Name'
    }
```

### Checking for New Duplicates

Run the analysis script periodically:

```bash
python analyze_agent_names.py
```

This will identify any new duplicate patterns that need normalization.

## Troubleshooting

### Restore from Backup

If needed, restore the database from backup:

```bash
# Stop any running processes
# Copy backup to main database
copy call_recordings.db.backup call_recordings.db
```

### Manual Verification

Check agent names in the database:

```sql
SELECT agent, COUNT(*) as call_count
FROM calls 
WHERE agent IS NOT NULL 
GROUP BY agent 
ORDER BY call_count DESC;
```

## Integration with GUI

The GUI automatically benefits from normalized agent names:
- **Agent filter dropdown** shows consolidated list
- **Search results** group by unified agent names
- **Analytics charts** display accurate agent performance
- **Export functions** use normalized names

## Future Enhancements

Potential improvements:
1. **Fuzzy matching** for similar names (e.g., "Alex" vs "Alexander")
2. **Automatic detection** of new duplicate patterns
3. **Historical tracking** of name changes
4. **Bulk import** of agent name mappings
