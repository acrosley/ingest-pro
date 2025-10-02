#!/usr/bin/env python3
"""
Query Tool for Call Recordings Database
Provides an interactive interface to explore the database
"""

import sqlite3
import pandas as pd
from pathlib import Path
import sys

class CallDatabaseQuery:
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
    
    def execute_query(self, query: str, return_df: bool = True):
        """Execute a SQL query and return results"""
        try:
            if return_df:
                df = pd.read_sql_query(query, self.conn)
                return df
            else:
                cursor = self.conn.cursor()
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"Query error: {e}")
            return None
    
    def show_tables(self):
        """Show available tables and views"""
        query = """
        SELECT name, type 
        FROM sqlite_master 
        WHERE type IN ('table', 'view') 
        ORDER BY type, name
        """
        df = self.execute_query(query)
        if df is not None:
            print("\nAvailable Tables and Views:")
            print("=" * 40)
            for _, row in df.iterrows():
                print(f"{row['type'].upper()}: {row['name']}")
    
    def get_database_stats(self):
        """Get database statistics"""
        stats_queries = [
            ("Total calls", "SELECT COUNT(*) FROM calls"),
            ("Calls with agents", "SELECT COUNT(*) FROM calls WHERE agent IS NOT NULL"),
            ("Unique agents", "SELECT COUNT(DISTINCT agent) FROM calls WHERE agent IS NOT NULL"),
            ("Total entities", "SELECT COUNT(*) FROM entities"),
            ("Total transcript segments", "SELECT COUNT(*) FROM transcript_segments"),
            ("Date range", "SELECT MIN(call_date), MAX(call_date) FROM calls WHERE call_date IS NOT NULL"),
            ("Sentiment distribution", """
                SELECT overall_sentiment, COUNT(*) 
                FROM calls 
                WHERE overall_sentiment IS NOT NULL 
                GROUP BY overall_sentiment 
                ORDER BY COUNT(*) DESC
            """)
        ]
        
        print("\nDatabase Statistics:")
        print("=" * 50)
        
        for title, query in stats_queries:
            try:
                if "distribution" in title.lower():
                    df = self.execute_query(query)
                    if df is not None and not df.empty:
                        print(f"\n{title}:")
                        for _, row in df.iterrows():
                            print(f"  {row.iloc[0]}: {row.iloc[1]}")
                else:
                    result = self.execute_query(query, return_df=False)
                    if result:
                        print(f"{title}: {result[0][0]}")
            except Exception as e:
                print(f"{title}: Error - {e}")
    
    def search_calls(self, search_term: str = None, agent: str = None, date_from: str = None, date_to: str = None):
        """Search calls with various filters"""
        query = """
        SELECT 
            file_id,
            agent,
            call_date,
            call_time,
            call_duration,
            overall_sentiment,
            summary
        FROM calls
        WHERE 1=1
        """
        params = []
        
        if search_term:
            query += " AND (summary LIKE ? OR file_id LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if agent:
            query += " AND agent LIKE ?"
            params.append(f"%{agent}%")
        
        if date_from:
            query += " AND call_date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND call_date <= ?"
            params.append(date_to)
        
        query += " ORDER BY call_date DESC, call_time DESC LIMIT 50"
        
        df = self.execute_query(query)
        if df is not None and not df.empty:
            print(f"\nFound {len(df)} calls:")
            print("=" * 100)
            for _, row in df.iterrows():
                print(f"ID: {row['file_id']}")
                print(f"Agent: {row['agent']}")
                print(f"Date/Time: {row['call_date']} {row['call_time']}")
                print(f"Duration: {row['call_duration']}")
                print(f"Sentiment: {row['overall_sentiment']}")
                print(f"Summary: {row['summary'][:100]}...")
                print("-" * 100)
        else:
            print("No calls found matching criteria.")
    
    def get_agent_performance(self):
        """Get agent performance statistics"""
        query = """
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
        ORDER BY total_calls DESC
        """
        
        df = self.execute_query(query)
        if df is not None and not df.empty:
            print("\nAgent Performance:")
            print("=" * 80)
            print(f"{'Agent':<15} {'Total':<6} {'Positive':<9} {'Negative':<9} {'Neutral':<8} {'Avg Summary':<12}")
            print("-" * 80)
            for _, row in df.iterrows():
                print(f"{row['agent']:<15} {row['total_calls']:<6} {row['positive_calls']:<9} {row['negative_calls']:<9} {row['neutral_calls']:<8} {int(row['avg_summary_length']):<12}")
    
    def get_entity_analysis(self, entity_type: str = None):
        """Get entity analysis"""
        if entity_type:
            query = f"""
            SELECT entity_value, COUNT(*) as frequency
            FROM entities
            WHERE entity_type = ?
            GROUP BY entity_value
            ORDER BY frequency DESC
            LIMIT 20
            """
            df = self.execute_query(query)
            if df is not None and not df.empty:
                print(f"\nTop {entity_type} entities:")
                print("=" * 50)
                for _, row in df.iterrows():
                    print(f"{row['entity_value']}: {row['frequency']}")
        else:
            query = """
            SELECT entity_type, COUNT(*) as total_entities
            FROM entities
            GROUP BY entity_type
            ORDER BY total_entities DESC
            """
            df = self.execute_query(query)
            if df is not None and not df.empty:
                print("\nEntity types:")
                print("=" * 30)
                for _, row in df.iterrows():
                    print(f"{row['entity_type']}: {row['total_entities']}")
    
    def get_call_details(self, file_id: str):
        """Get detailed information about a specific call"""
        # Get call details
        call_query = "SELECT * FROM calls WHERE file_id = ?"
        call_df = self.execute_query(call_query, return_df=False)
        
        if not call_df:
            print(f"Call not found: {file_id}")
            return
        
        call_data = call_df[0]
        
        # Get entities
        entities_query = """
        SELECT entity_type, entity_value
        FROM entities e
        JOIN calls c ON e.call_id = c.id
        WHERE c.file_id = ?
        ORDER BY entity_type, entity_value
        """
        entities_df = self.execute_query(entities_query)
        
        # Get transcript
        transcript_query = """
        SELECT timestamp, speaker, text
        FROM transcript_segments ts
        JOIN calls c ON ts.call_id = c.id
        WHERE c.file_id = ?
        ORDER BY segment_order
        """
        transcript_df = self.execute_query(transcript_query)
        
        # Display results
        print(f"\nCall Details for: {file_id}")
        print("=" * 60)
        print(f"Agent: {call_data[4]}")
        print(f"Date/Time: {call_data[5]} {call_data[6]}")
        print(f"Duration: {call_data[7]}")
        print(f"Sentiment: {call_data[9]}")
        print(f"Summary: {call_data[8]}")
        
        if entities_df is not None and not entities_df.empty:
            print(f"\nEntities:")
            print("-" * 30)
            for _, row in entities_df.iterrows():
                print(f"{row['entity_type']}: {row['entity_value']}")
        
        if transcript_df is not None and not transcript_df.empty:
            print(f"\nTranscript:")
            print("-" * 30)
            for _, row in transcript_df.iterrows():
                timestamp = f"[{row['timestamp']}]" if row['timestamp'] else ""
                speaker = f"{row['speaker']}:" if row['speaker'] else ""
                print(f"{timestamp} {speaker} {row['text']}")
    
    def interactive_menu(self):
        """Interactive menu for database exploration"""
        while True:
            print("\n" + "="*50)
            print("CALL RECORDINGS DATABASE QUERY TOOL")
            print("="*50)
            print("1. Show database statistics")
            print("2. Show available tables/views")
            print("3. Search calls")
            print("4. Agent performance analysis")
            print("5. Entity analysis")
            print("6. Get call details")
            print("7. Custom SQL query")
            print("0. Exit")
            print("-"*50)
            
            choice = input("Enter your choice (0-7): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.get_database_stats()
            elif choice == "2":
                self.show_tables()
            elif choice == "3":
                search_term = input("Search term (or press Enter to skip): ").strip()
                agent = input("Agent name (or press Enter to skip): ").strip()
                date_from = input("Date from (YYYY-MM-DD, or press Enter to skip): ").strip()
                date_to = input("Date to (YYYY-MM-DD, or press Enter to skip): ").strip()
                
                search_term = search_term if search_term else None
                agent = agent if agent else None
                date_from = date_from if date_from else None
                date_to = date_to if date_to else None
                
                self.search_calls(search_term, agent, date_from, date_to)
            elif choice == "4":
                self.get_agent_performance()
            elif choice == "5":
                entity_type = input("Entity type (or press Enter for all types): ").strip()
                entity_type = entity_type if entity_type else None
                self.get_entity_analysis(entity_type)
            elif choice == "6":
                file_id = input("Enter file ID: ").strip()
                if file_id:
                    self.get_call_details(file_id)
            elif choice == "7":
                sql_query = input("Enter SQL query: ").strip()
                if sql_query:
                    df = self.execute_query(sql_query)
                    if df is not None:
                        print(df)
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
    
    query_tool = CallDatabaseQuery(db_path)
    
    if query_tool.connect():
        query_tool.interactive_menu()
    
    query_tool.close()

if __name__ == "__main__":
    main()
