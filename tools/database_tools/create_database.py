#!/usr/bin/env python3
"""
Database Creator for Call Recordings JSON Files
Converts all JSON files from ALL_JSON_FILES into a SQLite database
"""

import os
import json
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CallDatabaseCreator:
    def __init__(self, json_folder_path: str, db_path: str = "call_recordings.db"):
        self.json_folder_path = Path(json_folder_path)
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def create_database_schema(self):
        """Create the database schema with proper normalization"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create tables
        self.cursor.executescript("""
            -- Main calls table
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT UNIQUE NOT NULL,
                wav_file TEXT,
                renamed_to TEXT,
                agent TEXT,
                call_date TEXT,
                call_time TEXT,
                call_duration TEXT,
                summary TEXT,
                overall_sentiment TEXT,
                sentiment_drivers TEXT,
                topics TEXT,
                action_items TEXT,
                transcript_file TEXT,
                transcript_path TEXT,
                analysis_timestamp TEXT,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Entities table (normalized)
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id INTEGER NOT NULL,
                entity_type TEXT NOT NULL,
                entity_value TEXT NOT NULL,
                FOREIGN KEY (call_id) REFERENCES calls (id) ON DELETE CASCADE
            );
            
            -- Transcript segments table
            CREATE TABLE IF NOT EXISTS transcript_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id INTEGER NOT NULL,
                segment_order INTEGER NOT NULL,
                timestamp TEXT,
                speaker TEXT,
                text TEXT,
                FOREIGN KEY (call_id) REFERENCES calls (id) ON DELETE CASCADE
            );
            
            -- Create indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_calls_file_id ON calls(file_id);
            CREATE INDEX IF NOT EXISTS idx_calls_agent ON calls(agent);
            CREATE INDEX IF NOT EXISTS idx_calls_date ON calls(call_date);
            CREATE INDEX IF NOT EXISTS idx_entities_call_id ON entities(call_id);
            CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
            CREATE INDEX IF NOT EXISTS idx_transcript_call_id ON transcript_segments(call_id);
        """)
        
        self.conn.commit()
        logger.info("Database schema created successfully")
    
    def extract_file_id(self, filename: str) -> str:
        """Extract file ID from filename"""
        return Path(filename).stem
    
    def parse_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a single JSON file and return structured data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract file ID from filename
            file_id = self.extract_file_id(file_path.name)
            
            # Extract call details
            call_details = data.get('call_details', {})
            analysis = data.get('analysis', {})
            processing_details = data.get('processing_details', {})
            transcript = data.get('transcript', [])
            
            # Prepare call record
            call_record = {
                'file_id': file_id,
                'wav_file': call_details.get('wav_file'),
                'renamed_to': call_details.get('renamed to'),
                'agent': call_details.get('Agent'),
                'call_date': call_details.get('call_date'),
                'call_time': call_details.get('call_time'),
                'call_duration': call_details.get('call_duration'),
                'summary': analysis.get('summary'),
                'overall_sentiment': analysis.get('sentiment', {}).get('overall'),
                'sentiment_drivers': json.dumps(analysis.get('sentiment', {}).get('drivers', [])),
                'topics': json.dumps(analysis.get('topics', [])),
                'action_items': json.dumps(analysis.get('action_items', [])),
                'transcript_file': processing_details.get('transcript_file'),
                'transcript_path': processing_details.get('transcript_path'),
                'analysis_timestamp': processing_details.get('analysis_timestamp_utc'),
                'model_used': processing_details.get('model_used')
            }
            
            # Extract entities
            entities = analysis.get('entities', {})
            entity_records = []
            for entity_type, entity_list in entities.items():
                if isinstance(entity_list, list):
                    for entity_value in entity_list:
                        if entity_value:  # Skip empty values
                            entity_records.append({
                                'entity_type': entity_type,
                                'entity_value': entity_value
                            })
            
            # Extract transcript segments
            transcript_records = []
            for i, segment in enumerate(transcript):
                transcript_records.append({
                    'segment_order': i,
                    'timestamp': segment.get('timestamp'),
                    'speaker': segment.get('speaker'),
                    'text': segment.get('text')
                })
            
            return {
                'call_record': call_record,
                'entities': entity_records,
                'transcript_segments': transcript_records
            }
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    def insert_call_data(self, call_data: Dict[str, Any]) -> bool:
        """Insert call data into database"""
        try:
            # Insert call record
            call_record = call_data['call_record']
            self.cursor.execute("""
                INSERT OR REPLACE INTO calls (
                    file_id, wav_file, renamed_to, agent, call_date, call_time, 
                    call_duration, summary, overall_sentiment, sentiment_drivers, 
                    topics, action_items, transcript_file, transcript_path, 
                    analysis_timestamp, model_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                call_record['file_id'], call_record['wav_file'], call_record['renamed_to'],
                call_record['agent'], call_record['call_date'], call_record['call_time'],
                call_record['call_duration'], call_record['summary'], call_record['overall_sentiment'],
                call_record['sentiment_drivers'], call_record['topics'], call_record['action_items'],
                call_record['transcript_file'], call_record['transcript_path'],
                call_record['analysis_timestamp'], call_record['model_used']
            ))
            
            call_id = self.cursor.lastrowid
            
            # Insert entities
            for entity in call_data['entities']:
                self.cursor.execute("""
                    INSERT INTO entities (call_id, entity_type, entity_value)
                    VALUES (?, ?, ?)
                """, (call_id, entity['entity_type'], entity['entity_value']))
            
            # Insert transcript segments
            for segment in call_data['transcript_segments']:
                self.cursor.execute("""
                    INSERT INTO transcript_segments (call_id, segment_order, timestamp, speaker, text)
                    VALUES (?, ?, ?, ?, ?)
                """, (call_id, segment['segment_order'], segment['timestamp'], 
                     segment['speaker'], segment['text']))
            
            return True
            
        except Exception as e:
            logger.error(f"Error inserting call data: {e}")
            return False
    
    def process_all_files(self):
        """Process all JSON files in the folder"""
        if not self.json_folder_path.exists():
            logger.error(f"JSON folder not found: {self.json_folder_path}")
            return
        
        json_files = list(self.json_folder_path.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        successful = 0
        failed = 0
        
        for json_file in json_files:
            logger.info(f"Processing: {json_file.name}")
            
            call_data = self.parse_json_file(json_file)
            if call_data:
                if self.insert_call_data(call_data):
                    successful += 1
                    self.conn.commit()
                else:
                    failed += 1
            else:
                failed += 1
        
        logger.info(f"Processing complete: {successful} successful, {failed} failed")
    
    def create_views(self):
        """Create useful database views for common queries"""
        self.cursor.executescript("""
            -- View for calls with entity counts
            CREATE VIEW IF NOT EXISTS calls_with_entity_counts AS
            SELECT 
                c.*,
                COUNT(DISTINCT e.entity_type) as entity_types_count,
                COUNT(e.id) as total_entities
            FROM calls c
            LEFT JOIN entities e ON c.id = e.call_id
            GROUP BY c.id;
            
            -- View for sentiment analysis
            CREATE VIEW IF NOT EXISTS sentiment_analysis AS
            SELECT 
                overall_sentiment,
                COUNT(*) as call_count,
                AVG(LENGTH(summary)) as avg_summary_length
            FROM calls
            WHERE overall_sentiment IS NOT NULL
            GROUP BY overall_sentiment
            ORDER BY call_count DESC;
            
            -- View for agent performance
            CREATE VIEW IF NOT EXISTS agent_performance AS
            SELECT 
                agent,
                COUNT(*) as total_calls,
                AVG(LENGTH(summary)) as avg_summary_length,
                COUNT(CASE WHEN overall_sentiment = 'Positive' THEN 1 END) as positive_calls,
                COUNT(CASE WHEN overall_sentiment = 'Negative' THEN 1 END) as negative_calls,
                COUNT(CASE WHEN overall_sentiment = 'Neutral' THEN 1 END) as neutral_calls
            FROM calls
            WHERE agent IS NOT NULL
            GROUP BY agent
            ORDER BY total_calls DESC;
        """)
        
        self.conn.commit()
        logger.info("Database views created successfully")
    
    def generate_report(self):
        """Generate a summary report of the database"""
        report_queries = [
            ("Total calls", "SELECT COUNT(*) FROM calls"),
            ("Calls with agents", "SELECT COUNT(*) FROM calls WHERE agent IS NOT NULL"),
            ("Unique agents", "SELECT COUNT(DISTINCT agent) FROM calls WHERE agent IS NOT NULL"),
            ("Date range", "SELECT MIN(call_date), MAX(call_date) FROM calls WHERE call_date IS NOT NULL"),
            ("Total entities", "SELECT COUNT(*) FROM entities"),
            ("Entity types", "SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type ORDER BY COUNT(*) DESC"),
            ("Sentiment distribution", "SELECT overall_sentiment, COUNT(*) FROM calls WHERE overall_sentiment IS NOT NULL GROUP BY overall_sentiment"),
            ("Average call duration", "SELECT AVG(CAST(REPLACE(REPLACE(call_duration, ':', ''), 'm', '') AS INTEGER)) FROM calls WHERE call_duration IS NOT NULL")
        ]
        
        print("\n" + "="*50)
        print("DATABASE SUMMARY REPORT")
        print("="*50)
        
        for title, query in report_queries:
            try:
                self.cursor.execute(query)
                result = self.cursor.fetchone()
                print(f"{title}: {result[0] if result else 'N/A'}")
            except Exception as e:
                print(f"{title}: Error - {e}")
        
        print("="*50)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

def main():
    # Configuration
    json_folder = r"W:\Staff_Call_Recordings\_Pipeline_Output\ALL_JSON_FILES"
    db_path = "call_recordings.db"
    
    # Create database
    creator = CallDatabaseCreator(json_folder, db_path)
    
    try:
        # Create schema
        creator.create_database_schema()
        
        # Process all files
        creator.process_all_files()
        
        # Create views
        creator.create_views()
        
        # Generate report
        creator.generate_report()
        
        print(f"\nDatabase created successfully: {db_path}")
        print("You can now query the database using SQLite tools or Python.")
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
    finally:
        creator.close()

if __name__ == "__main__":
    main()
