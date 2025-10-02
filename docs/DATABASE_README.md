# Call Recordings Database Tools

This directory contains tools to convert your JSON call recording files into a SQLite database for easy querying and analysis.

## Files

- `create_database.py` - Main script to create the database from JSON files
- `create_database.bat` - Windows batch file to run the database creator
- `query_database.py` - Interactive tool to explore and query the database
- `query_database.bat` - Windows batch file to run the query tool
- `database_requirements.txt` - Python dependencies
- `DATABASE_README.md` - This file

## Quick Start

### 1. Install Dependencies
```bash
pip install -r database_requirements.txt
```

### 2. Create the Database
Double-click `create_database.bat` or run:
```bash
python create_database.py
```

This will:
- Read all JSON files from `W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES`
- Create a SQLite database called `call_recordings.db`
- Generate a summary report

### 3. Explore the Database
Double-click `query_database.bat` or run:
```bash
python query_database.py
```

## Database Schema

The database contains three main tables:

### 1. `calls` table
Main call information:
- `id` - Primary key
- `file_id` - Original JSON filename (without extension)
- `wav_file` - Original audio filename
- `renamed_to` - New filename after processing
- `agent` - Agent name
- `call_date` - Call date
- `call_time` - Call time
- `call_duration` - Call duration
- `summary` - AI-generated summary
- `overall_sentiment` - Sentiment analysis
- `sentiment_drivers` - JSON array of sentiment drivers
- `topics` - JSON array of topics
- `action_items` - JSON array of action items
- `transcript_file` - Transcript filename
- `transcript_path` - Full transcript path
- `analysis_timestamp` - When analysis was performed
- `model_used` - AI model used for analysis

### 2. `entities` table
Named entities extracted from calls:
- `id` - Primary key
- `call_id` - Foreign key to calls table
- `entity_type` - Type of entity (persons, organizations, locations, etc.)
- `entity_value` - The actual entity value

### 3. `transcript_segments` table
Individual transcript segments:
- `id` - Primary key
- `call_id` - Foreign key to calls table
- `segment_order` - Order in transcript
- `timestamp` - Time in call
- `speaker` - Who spoke (Agent/Caller)
- `text` - What was said

## Database Views

The system creates several useful views:

- `calls_with_entity_counts` - Calls with entity statistics
- `sentiment_analysis` - Sentiment distribution analysis
- `agent_performance` - Agent performance metrics

## Example Queries

### Find all calls by a specific agent
```sql
SELECT * FROM calls WHERE agent = 'Jeff' ORDER BY call_date DESC;
```

### Find calls with specific entities
```sql
SELECT c.* FROM calls c
JOIN entities e ON c.id = e.call_id
WHERE e.entity_type = 'organizations' AND e.entity_value LIKE '%Uber%';
```

### Get agent performance
```sql
SELECT 
    agent,
    COUNT(*) as total_calls,
    COUNT(CASE WHEN overall_sentiment = 'Positive' THEN 1 END) as positive_calls
FROM calls 
WHERE agent IS NOT NULL
GROUP BY agent
ORDER BY total_calls DESC;
```

### Find calls with specific topics
```sql
SELECT * FROM calls 
WHERE topics LIKE '%Uber%' OR topics LIKE '%transportation%';
```

## Query Tool Features

The interactive query tool provides:

1. **Database Statistics** - Overview of data
2. **Table/View Explorer** - See available data structures
3. **Call Search** - Search by terms, agent, date range
4. **Agent Performance** - Performance metrics by agent
5. **Entity Analysis** - Most common entities
6. **Call Details** - Full details for specific calls
7. **Custom SQL** - Run your own queries

## Tips

- The database uses SQLite, so you can open `call_recordings.db` with any SQLite browser
- Use the views for common analysis tasks
- The `entities` table is normalized for efficient querying
- All JSON arrays are stored as JSON strings for compatibility
- Use `LIKE` queries for text search in JSON fields

## Troubleshooting

### Database not found
Make sure you've run `create_database.py` first.

### Permission errors
Ensure you have write permissions in the current directory.

### Missing dependencies
Run `pip install pandas` to install required packages.

### Large database
The database can grow large with many calls. Consider archiving old data or using database compression.
