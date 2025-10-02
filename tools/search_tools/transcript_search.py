#!/usr/bin/env python3
"""
Transcript Search Tool
Searches for specific words/phrases across all call transcripts
"""

import sqlite3
import re
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

class TranscriptSearcher:
    def __init__(self, db_path: str = "call_recordings.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def search_transcripts(self, search_terms: List[str], case_sensitive: bool = False, 
                          agent_filter: str = None, date_from: str = None, date_to: str = None,
                          context_lines: int = 2) -> List[Dict[str, Any]]:
        """
        Search for terms across all transcripts
        
        Args:
            search_terms: List of words/phrases to search for
            case_sensitive: Whether search should be case sensitive
            agent_filter: Filter by specific agent
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            context_lines: Number of lines before/after match to include
        """
        
        # Build the base query
        query = """
        SELECT 
            c.file_id,
            c.agent,
            c.call_date,
            c.call_time,
            c.call_duration,
            c.overall_sentiment,
            ts.segment_order,
            ts.timestamp,
            ts.speaker,
            ts.text
        FROM calls c
        JOIN transcript_segments ts ON c.id = ts.call_id
        WHERE 1=1
        """
        
        params = []
        
        # Add filters
        if agent_filter:
            query += " AND c.agent LIKE ?"
            params.append(f"%{agent_filter}%")
        
        if date_from:
            query += " AND c.call_date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND c.call_date <= ?"
            params.append(date_to)
        
        query += " ORDER BY c.call_date DESC, c.call_time DESC, ts.segment_order"
        
        # Execute query
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Process results and find matches
        matches = []
        current_call = None
        current_segments = []
        
        for row in results:
            file_id, agent, call_date, call_time, duration, sentiment, segment_order, timestamp, speaker, text = row
            
            # Check if this is a new call
            if current_call != file_id:
                # Process previous call's segments
                if current_segments:
                    call_matches = self._find_matches_in_call(current_segments, search_terms, case_sensitive, context_lines)
                    matches.extend(call_matches)
                
                # Start new call
                current_call = file_id
                current_segments = []
            
            current_segments.append({
                'file_id': file_id,
                'agent': agent,
                'call_date': call_date,
                'call_time': call_time,
                'duration': duration,
                'sentiment': sentiment,
                'segment_order': segment_order,
                'timestamp': timestamp,
                'speaker': speaker,
                'text': text
            })
        
        # Process the last call
        if current_segments:
            call_matches = self._find_matches_in_call(current_segments, search_terms, case_sensitive, context_lines)
            matches.extend(call_matches)
        
        return matches
    
    def _find_matches_in_call(self, segments: List[Dict], search_terms: List[str], 
                             case_sensitive: bool, context_lines: int) -> List[Dict]:
        """Find matches within a single call's segments"""
        matches = []
        
        for i, segment in enumerate(segments):
            text = segment['text']
            if not case_sensitive:
                text = text.lower()
            
            # Check if any search term is found
            found_terms = []
            for term in search_terms:
                search_term = term if case_sensitive else term.lower()
                if search_term in text:
                    found_terms.append(term)
            
            if found_terms:
                # Get context (segments before and after)
                start_idx = max(0, i - context_lines)
                end_idx = min(len(segments), i + context_lines + 1)
                context_segments = segments[start_idx:end_idx]
                
                # Highlight the matching terms in the text
                highlighted_text = self._highlight_terms(segment['text'], found_terms, case_sensitive)
                
                match = {
                    'file_id': segment['file_id'],
                    'agent': segment['agent'],
                    'call_date': segment['call_date'],
                    'call_time': segment['call_time'],
                    'duration': segment['duration'],
                    'sentiment': segment['sentiment'],
                    'timestamp': segment['timestamp'],
                    'speaker': segment['speaker'],
                    'matched_terms': found_terms,
                    'highlighted_text': highlighted_text,
                    'context_segments': context_segments
                }
                matches.append(match)
        
        return matches
    
    def _highlight_terms(self, text: str, terms: List[str], case_sensitive: bool) -> str:
        """Highlight matching terms in text with ** markers"""
        highlighted = text
        for term in terms:
            if case_sensitive:
                highlighted = highlighted.replace(term, f"**{term}**")
            else:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted = pattern.sub(f"**{term}**", highlighted)
        return highlighted
    
    def search_and_display(self, search_terms: List[str], case_sensitive: bool = False,
                          agent_filter: str = None, date_from: str = None, date_to: str = None,
                          context_lines: int = 2):
        """Search and display results in a formatted way"""
        
        print(f"\nSearching for: {', '.join(search_terms)}")
        if agent_filter:
            print(f"Agent filter: {agent_filter}")
        if date_from or date_to:
            print(f"Date range: {date_from or 'any'} to {date_to or 'any'}")
        print("=" * 80)
        
        matches = self.search_transcripts(search_terms, case_sensitive, agent_filter, date_from, date_to, context_lines)
        
        if not matches:
            print("No matches found.")
            return
        
        print(f"Found {len(matches)} matches across {len(set(m['file_id'] for m in matches))} calls:\n")
        
        for i, match in enumerate(matches, 1):
            print(f"Match {i}:")
            print(f"  Call ID: {match['file_id']}")
            print(f"  Agent: {match['agent']}")
            print(f"  Date/Time: {match['call_date']} {match['call_time']}")
            print(f"  Duration: {match['duration']}")
            print(f"  Sentiment: {match['sentiment']}")
            print(f"  Matched Terms: {', '.join(match['matched_terms'])}")
            print(f"  Speaker: {match['speaker']}")
            print(f"  Timestamp: {match['timestamp']}")
            print(f"  Text: {match['highlighted_text']}")
            
            # Show context if available
            if len(match['context_segments']) > 1:
                print("  Context:")
                for ctx_seg in match['context_segments']:
                    if ctx_seg['segment_order'] != match['context_segments'][context_lines]['segment_order']:
                        print(f"    [{ctx_seg['timestamp']}] {ctx_seg['speaker']}: {ctx_seg['text']}")
            
            print("-" * 80)
    
    def get_search_statistics(self, search_terms: List[str], case_sensitive: bool = False) -> Dict[str, Any]:
        """Get statistics about search term usage"""
        stats = {
            'total_calls': 0,
            'calls_with_matches': 0,
            'total_matches': 0,
            'matches_by_agent': {},
            'matches_by_term': {term: 0 for term in search_terms},
            'matches_by_sentiment': {}
        }
        
        matches = self.search_transcripts(search_terms, case_sensitive)
        
        if not matches:
            return stats
        
        # Count total calls
        all_calls_query = "SELECT COUNT(DISTINCT file_id) FROM calls"
        cursor = self.conn.cursor()
        cursor.execute(all_calls_query)
        stats['total_calls'] = cursor.fetchone()[0]
        
        # Process matches
        calls_with_matches = set()
        for match in matches:
            calls_with_matches.add(match['file_id'])
            stats['total_matches'] += 1
            
            # By agent
            agent = match['agent'] or 'Unknown'
            stats['matches_by_agent'][agent] = stats['matches_by_agent'].get(agent, 0) + 1
            
            # By term
            for term in match['matched_terms']:
                stats['matches_by_term'][term] += 1
            
            # By sentiment
            sentiment = match['sentiment'] or 'Unknown'
            stats['matches_by_sentiment'][sentiment] = stats['matches_by_sentiment'].get(sentiment, 0) + 1
        
        stats['calls_with_matches'] = len(calls_with_matches)
        
        return stats
    
    def interactive_search(self):
        """Interactive search interface"""
        while True:
            print("\n" + "="*50)
            print("TRANSCRIPT SEARCH TOOL")
            print("="*50)
            print("1. Search for specific terms")
            print("2. Search with filters (agent, date)")
            print("3. Get search statistics")
            print("4. Case-sensitive search")
            print("0. Exit")
            print("-"*50)
            
            choice = input("Enter your choice (0-4): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                terms_input = input("Enter search terms (comma-separated): ").strip()
                if terms_input:
                    search_terms = [term.strip() for term in terms_input.split(',')]
                    self.search_and_display(search_terms)
            elif choice == "2":
                terms_input = input("Enter search terms (comma-separated): ").strip()
                agent_filter = input("Agent filter (or press Enter to skip): ").strip()
                date_from = input("Date from (YYYY-MM-DD, or press Enter to skip): ").strip()
                date_to = input("Date to (YYYY-MM-DD, or press Enter to skip): ").strip()
                
                if terms_input:
                    search_terms = [term.strip() for term in terms_input.split(',')]
                    agent_filter = agent_filter if agent_filter else None
                    date_from = date_from if date_from else None
                    date_to = date_to if date_to else None
                    
                    self.search_and_display(search_terms, agent_filter=agent_filter, 
                                          date_from=date_from, date_to=date_to)
            elif choice == "3":
                terms_input = input("Enter search terms (comma-separated): ").strip()
                if terms_input:
                    search_terms = [term.strip() for term in terms_input.split(',')]
                    stats = self.get_search_statistics(search_terms)
                    
                    print(f"\nSearch Statistics for: {', '.join(search_terms)}")
                    print("=" * 50)
                    print(f"Total calls in database: {stats['total_calls']}")
                    print(f"Calls with matches: {stats['calls_with_matches']}")
                    print(f"Total matches found: {stats['total_matches']}")
                    
                    print(f"\nMatches by term:")
                    for term, count in stats['matches_by_term'].items():
                        print(f"  {term}: {count}")
                    
                    print(f"\nMatches by agent:")
                    for agent, count in sorted(stats['matches_by_agent'].items(), key=lambda x: x[1], reverse=True):
                        print(f"  {agent}: {count}")
                    
                    print(f"\nMatches by sentiment:")
                    for sentiment, count in stats['matches_by_sentiment'].items():
                        print(f"  {sentiment}: {count}")
            elif choice == "4":
                terms_input = input("Enter search terms (comma-separated): ").strip()
                if terms_input:
                    search_terms = [term.strip() for term in terms_input.split(',')]
                    self.search_and_display(search_terms, case_sensitive=True)
            else:
                print("Invalid choice. Please try again.")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    db_path = "call_recordings.db"
    
    if not Path(db_path).exists():
        print(f"Database not found: {db_path}")
        print("Please run create_database.py first to create the database.")
        return
    
    searcher = TranscriptSearcher(db_path)
    
    if searcher.connect():
        searcher.interactive_search()
    
    searcher.close()

if __name__ == "__main__":
    main()
