#!/usr/bin/env python3
"""
Analyze agent names in the database to identify normalization needs
"""

import sqlite3
from pathlib import Path
from collections import defaultdict

def analyze_agent_names():
    """Analyze agent names to identify duplicates and normalization patterns"""
    
    db_path = "../database_tools/call_recordings.db"
    
    if not Path(db_path).exists():
        print(f"ERROR: Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all agent names and their call counts
        cursor.execute("""
            SELECT agent, COUNT(*) as call_count
            FROM calls 
            WHERE agent IS NOT NULL 
            GROUP BY agent 
            ORDER BY call_count DESC
        """)
        
        agents = cursor.fetchall()
        
        print("=== CURRENT AGENT NAMES ===")
        print(f"{'Agent Name':<30} {'Call Count':<10}")
        print("-" * 40)
        
        for agent, count in agents:
            print(f"{agent:<30} {count:<10}")
        
        print(f"\nTotal unique agents: {len(agents)}")
        
        # Analyze for potential duplicates
        print("\n=== POTENTIAL DUPLICATES ANALYSIS ===")
        
        # Group by first name
        first_name_groups = defaultdict(list)
        for agent, count in agents:
            if agent and ' ' in agent:
                first_name = agent.split()[0]
                first_name_groups[first_name].append((agent, count))
        
        duplicates_found = False
        for first_name, entries in first_name_groups.items():
            if len(entries) > 1:
                duplicates_found = True
                print(f"\nPotential duplicates for '{first_name}':")
                for agent, count in entries:
                    print(f"  - {agent} ({count} calls)")
        
        if not duplicates_found:
            print("No obvious duplicates found based on first name matching.")
        
        # Show single name vs full name patterns
        print("\n=== NAME PATTERN ANALYSIS ===")
        single_names = [agent for agent, _ in agents if agent and ' ' not in agent]
        full_names = [agent for agent, _ in agents if agent and ' ' in agent]
        
        print(f"Single names ({len(single_names)}): {single_names}")
        print(f"Full names ({len(full_names)}): {full_names}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error analyzing agent names: {e}")

if __name__ == "__main__":
    analyze_agent_names()
    input("\nPress Enter to continue...")
