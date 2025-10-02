#!/usr/bin/env python3
"""
Agent Name Utilities
Provides functions for normalizing and managing agent names
"""

import sqlite3
from collections import defaultdict

def get_agent_normalization_mapping():
    """
    Get the standard mapping for agent name normalization
    This can be used to normalize agent names during data import
    """
    return {
        'Alex': 'Alex Alvarez',
        'Andrew': 'Andrew Crosley', 
        'Carlos': 'Carlos Oliva',
        'Ashley': 'Ashley Casanova',
        'Jeff': 'Jeff Greene'
    }

def normalize_agent_name(agent_name):
    """
    Normalize a single agent name using the standard mapping
    """
    if not agent_name:
        return agent_name
    
    mapping = get_agent_normalization_mapping()
    return mapping.get(agent_name, agent_name)

def normalize_agent_names_in_database(db_path="../database_tools/call_recordings.db"):
    """
    Apply agent name normalization to the database
    Returns the number of records updated
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        mapping = get_agent_normalization_mapping()
        total_updates = 0
        
        for old_name, new_name in mapping.items():
            cursor.execute("SELECT COUNT(*) FROM calls WHERE agent = ?", (old_name,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                cursor.execute("UPDATE calls SET agent = ? WHERE agent = ?", (new_name, old_name))
                total_updates += cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return total_updates
        
    except Exception as e:
        print(f"Error normalizing agent names: {e}")
        return 0

def get_unique_agents(db_path="../call_recordings.db"):
    """
    Get list of unique agent names from database
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT agent FROM calls WHERE agent IS NOT NULL ORDER BY agent")
        agents = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return agents
        
    except Exception as e:
        print(f"Error getting unique agents: {e}")
        return []

if __name__ == "__main__":
    # Test the functions
    print("Agent normalization mapping:")
    mapping = get_agent_normalization_mapping()
    for old, new in mapping.items():
        print(f"  '{old}' -> '{new}'")
    
    print(f"\nUnique agents in database: {get_unique_agents()}")
