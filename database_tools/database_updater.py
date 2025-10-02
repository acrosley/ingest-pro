#!/usr/bin/env python3
"""
Database Updater for Call Recordings
Automatically adds new JSON files to the existing SQLite database
"""

import os
import json
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import logging

# Import agent name utilities
try:
    import sys
    import os
    # Add parent directory to path to find agent_tools
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agent_tools'))
    from agent_name_utils import normalize_agent_name
    AGENT_NORMALIZATION_ENABLED = True
except ImportError:
    AGENT_NORMALIZATION_ENABLED = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseUpdater:
    def __init__(self, json_folder_path: str, db_path: str = "call_recordings.db"):
        self.json_folder_path = Path(json_folder_path)
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect_database(self):
        """Connect to existing database"""
        if not os.path.exists(self.db_path):
            logger.error(f"Database not found: {self.db_path}")
            logger.info("Run create_database.py first to create the database")
            return False
            
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        logger.info(f"Connected to database: {self.db_path}")
        return True
    
    def get_existing_file_ids(self) -> Set[str]:
        """Get list of file IDs already in the database"""
        self.cursor.execute("SELECT file_id FROM calls")
        existing_ids = {row[0] for row in self.cursor.fetchall()}
        logger.info(f"Found {len(existing_ids)} existing records in database")
        return existing_ids
    
    def extract_file_id(self, filename: str) -> str:
        """Extract file ID from filename"""
        return Path(filename).stem
    
    def parse_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a single JSON file and return structured data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract call details
            call_details = data.get('call_details', {})
            analysis = data.get('analysis', {})
            processing_details = data.get('processing_details', {})
            transcript = data.get('transcript', [])
            
            # Handle the actual field names from the processor
            # Convert "renamed to" to "renamed_to" and "Agent" to "agent"
            if 'renamed to' in call_details:
                call_details['renamed_to'] = call_details.pop('renamed to')
            if 'Agent' in call_details:
                call_details['agent'] = call_details.pop('Agent')
            
            # Handle nested sentiment structure
            sentiment = analysis.get('sentiment', {})
            overall_sentiment = sentiment.get('overall', '') if isinstance(sentiment, dict) else ''
            sentiment_drivers = sentiment.get('drivers', []) if isinstance(sentiment, dict) else []
            
            # Convert sentiment_drivers list to string if it's a list
            if isinstance(sentiment_drivers, list):
                sentiment_drivers = '; '.join(sentiment_drivers)
            
            # Handle entities structure - convert from categorized dict to flat list
            entities = []
            entities_data = analysis.get('entities', {})
            if isinstance(entities_data, dict):
                for category, values in entities_data.items():
                    if isinstance(values, list):
                        for value in values:
                            entities.append({
                                'type': category,
                                'value': str(value)
                            })
            
            # Handle processing_details field name differences
            if 'analysis_timestamp_utc' in processing_details:
                processing_details['analysis_timestamp'] = processing_details.pop('analysis_timestamp_utc')
            
            # Convert topics and action_items lists to strings
            topics = analysis.get('topics', [])
            if isinstance(topics, list):
                topics = '; '.join(topics)
            
            action_items = analysis.get('action_items', [])
            if isinstance(action_items, list):
                action_items = '; '.join(action_items)
            
            return {
                'call_details': call_details,
                'analysis': {
                    'summary': analysis.get('summary', ''),
                    'overall_sentiment': overall_sentiment,
                    'sentiment_drivers': sentiment_drivers,
                    'topics': topics,
                    'action_items': action_items
                },
                'processing_details': processing_details,
                'transcript': transcript,
                'entities': entities
            }
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    def insert_call_record(self, file_id: str, file_path: Path, parsed_data: Dict[str, Any]):
        """Insert a single call record into the database"""
        try:
            call_details = parsed_data['call_details']
            analysis = parsed_data['analysis']
            processing_details = parsed_data['processing_details']
            
            # Normalize agent name if enabled
            agent_name = call_details.get('agent', '')
            if AGENT_NORMALIZATION_ENABLED and agent_name:
                normalized_agent = normalize_agent_name(agent_name)
                if normalized_agent != agent_name:
                    logger.info(f"Normalized agent name: '{agent_name}' -> '{normalized_agent}'")
                    agent_name = normalized_agent
            
            # Insert main call record
            self.cursor.execute("""
                INSERT INTO calls (
                    file_id, wav_file, renamed_to, agent, call_date, call_time,
                    call_duration, summary, overall_sentiment, sentiment_drivers,
                    topics, action_items, transcript_file, transcript_path,
                    analysis_timestamp, model_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_id,
                call_details.get('wav_file', ''),
                call_details.get('renamed_to', ''),
                agent_name,  # Use normalized agent name
                call_details.get('call_date', ''),
                call_details.get('call_time', ''),
                call_details.get('call_duration', ''),
                analysis.get('summary', ''),
                analysis.get('overall_sentiment', ''),
                analysis.get('sentiment_drivers', ''),
                analysis.get('topics', ''),
                analysis.get('action_items', ''),
                call_details.get('transcript_file', ''),
                call_details.get('transcript_path', ''),
                processing_details.get('analysis_timestamp', ''),
                processing_details.get('model_used', '')
            ))
            
            call_id = self.cursor.lastrowid
            
            # Insert entities
            for entity in parsed_data['entities']:
                self.cursor.execute("""
                    INSERT INTO entities (call_id, entity_type, entity_value)
                    VALUES (?, ?, ?)
                """, (call_id, entity['type'], entity['value']))
            
            # Insert transcript segments
            for i, segment in enumerate(parsed_data['transcript']):
                self.cursor.execute("""
                    INSERT INTO transcript_segments (call_id, segment_order, timestamp, speaker, text)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    call_id,
                    i + 1,
                    segment.get('timestamp', ''),
                    segment.get('speaker', ''),
                    segment.get('text', '')
                ))
            
            logger.debug(f"Inserted call record: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting {file_id}: {e}")
            return False
    
    def update_database(self) -> Dict[str, int]:
        """Update database with new JSON files"""
        if not self.connect_database():
            return {'processed': 0, 'skipped': 0, 'failed': 0}
        
        try:
            # Get existing file IDs
            existing_ids = self.get_existing_file_ids()
            
            # Find all JSON files
            json_files = list(self.json_folder_path.glob('*.json'))
            logger.info(f"Found {len(json_files)} JSON files in {self.json_folder_path}")
            
            processed = 0
            skipped = 0
            failed = 0
            
            for json_file in json_files:
                file_id = self.extract_file_id(json_file.name)
                
                if file_id in existing_ids:
                    logger.debug(f"Skipping existing file: {file_id}")
                    skipped += 1
                    continue
                
                # Parse and insert new file
                parsed_data = self.parse_json_file(json_file)
                if parsed_data:
                    if self.insert_call_record(file_id, json_file, parsed_data):
                        processed += 1
                        logger.info(f"Added new call: {file_id}")
                    else:
                        failed += 1
                else:
                    failed += 1
            
            # Commit all changes
            self.conn.commit()
            
            logger.info(f"Database update complete: {processed} new, {skipped} existing, {failed} failed")
            return {'processed': processed, 'skipped': skipped, 'failed': failed}
            
        except Exception as e:
            logger.error(f"Error updating database: {e}")
            return {'processed': 0, 'skipped': 0, 'failed': 0}
        finally:
            if self.conn:
                self.conn.close()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.connect_database():
            return {}
        
        try:
            # Get counts
            self.cursor.execute("SELECT COUNT(*) FROM calls")
            total_calls = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM entities")
            total_entities = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM transcript_segments")
            total_segments = self.cursor.fetchone()[0]
            
            # Get date range
            self.cursor.execute("SELECT MIN(call_date), MAX(call_date) FROM calls WHERE call_date != ''")
            date_range = self.cursor.fetchone()
            
            # Get unique agents
            self.cursor.execute("SELECT COUNT(DISTINCT agent) FROM calls WHERE agent != ''")
            unique_agents = self.cursor.fetchone()[0]
            
            return {
                'total_calls': total_calls,
                'total_entities': total_entities,
                'total_segments': total_segments,
                'date_range': date_range,
                'unique_agents': unique_agents
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
        finally:
            if self.conn:
                self.conn.close()

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update call recordings database with new JSON files')
    parser.add_argument('json_folder', help='Path to folder containing JSON files')
    parser.add_argument('--db', default='call_recordings.db', help='Database file path')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    
    args = parser.parse_args()
    
    updater = DatabaseUpdater(args.json_folder, args.db)
    
    if args.stats:
        stats = updater.get_database_stats()
        if stats:
            print("\n=== DATABASE STATISTICS ===")
            print(f"Total calls: {stats['total_calls']}")
            print(f"Total entities: {stats['total_entities']}")
            print(f"Total transcript segments: {stats['total_segments']}")
            print(f"Unique agents: {stats['unique_agents']}")
            if stats['date_range'][0]:
                print(f"Date range: {stats['date_range'][0]} to {stats['date_range'][1]}")
    else:
        results = updater.update_database()
        print(f"\n=== UPDATE RESULTS ===")
        print(f"New calls added: {results['processed']}")
        print(f"Existing calls skipped: {results['skipped']}")
        print(f"Failed to process: {results['failed']}")

if __name__ == "__main__":
    main()
