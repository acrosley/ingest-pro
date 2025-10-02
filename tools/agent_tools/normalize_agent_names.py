#!/usr/bin/env python3
"""
Agent Name Normalization Script
Consolidates duplicate agent entries and standardizes name format
"""

import sqlite3
from pathlib import Path
from collections import defaultdict
import re

class AgentNameNormalizer:
    def __init__(self, db_path="../database_tools/call_recordings.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect_database(self):
        """Connect to the database"""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close_database(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def get_current_agents(self):
        """Get current agent names and their call counts"""
        self.cursor.execute("""
            SELECT agent, COUNT(*) as call_count
            FROM calls 
            WHERE agent IS NOT NULL 
            GROUP BY agent 
            ORDER BY call_count DESC
        """)
        return self.cursor.fetchall()
    
    def analyze_duplicates(self):
        """Analyze and identify duplicate agent entries"""
        agents = self.get_current_agents()
        
        # Group by first name (extract first name from all agents)
        first_name_groups = defaultdict(list)
        for agent, count in agents:
            if agent:
                first_name = agent.split()[0]  # Get first name from any agent
                first_name_groups[first_name].append((agent, count))
        
        # Find potential duplicates (groups with more than one entry)
        duplicates = {}
        for first_name, entries in first_name_groups.items():
            if len(entries) > 1:
                # Sort by call count (prefer the one with more calls)
                entries.sort(key=lambda x: x[1], reverse=True)
                duplicates[first_name] = entries
        
        return duplicates
    
    def create_normalization_mapping(self):
        """Create mapping from old names to normalized names"""
        duplicates = self.analyze_duplicates()
        mapping = {}
        
        print("=== NORMALIZATION MAPPING ===")
        for first_name, entries in duplicates.items():
            # Use the full name with the most calls as the normalized version
            normalized_name = entries[0][0]  # First entry (most calls)
            
            print(f"\n{first_name}:")
            for agent, count in entries:
                mapping[agent] = normalized_name
                print(f"  '{agent}' ({count} calls) -> '{normalized_name}'")
        
        return mapping
    
    def backup_database(self, backup_path=None):
        """Create a backup of the database before making changes"""
        if backup_path is None:
            backup_path = f"{self.db_path}.backup"
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        print(f"Database backed up to: {backup_path}")
        return backup_path
    
    def normalize_agent_names(self, mapping, dry_run=True):
        """Normalize agent names in the database"""
        if dry_run:
            print("\n=== DRY RUN - NO CHANGES WILL BE MADE ===")
        else:
            print("\n=== APPLYING NORMALIZATION CHANGES ===")
        
        # Show what would be changed
        total_updates = 0
        for old_name, new_name in mapping.items():
            if old_name != new_name:
                # Count records that would be updated
                self.cursor.execute("SELECT COUNT(*) FROM calls WHERE agent = ?", (old_name,))
                count = self.cursor.fetchone()[0]
                total_updates += count
                
                print(f"Would update {count} records: '{old_name}' -> '{new_name}'")
        
        if not dry_run:
            # Apply the changes
            for old_name, new_name in mapping.items():
                if old_name != new_name:
                    self.cursor.execute(
                        "UPDATE calls SET agent = ? WHERE agent = ?", 
                        (new_name, old_name)
                    )
                    print(f"Updated {self.cursor.rowcount} records: '{old_name}' -> '{new_name}'")
            
            # Commit changes
            self.conn.commit()
            print(f"\n✅ Successfully normalized {total_updates} agent name records")
        else:
            print(f"\n📋 Dry run complete - would update {total_updates} records")
        
        return total_updates
    
    def verify_normalization(self):
        """Verify the normalization was successful"""
        print("\n=== VERIFICATION ===")
        
        agents = self.get_current_agents()
        
        print("Updated agent names:")
        print(f"{'Agent Name':<30} {'Call Count':<10}")
        print("-" * 40)
        
        for agent, count in agents:
            print(f"{agent:<30} {count:<10}")
        
        # Check for any remaining duplicates
        duplicates = self.analyze_duplicates()
        if duplicates:
            print(f"\n⚠️  Warning: {len(duplicates)} potential duplicates still found")
            for first_name, entries in duplicates.items():
                print(f"  {first_name}: {[agent for agent, _ in entries]}")
        else:
            print(f"\n✅ No duplicates found - normalization successful!")
        
        return len(duplicates) == 0

def main():
    """Main function to run the normalization process"""
    normalizer = AgentNameNormalizer()
    
    try:
        # Connect to database
        normalizer.connect_database()
        
        # Analyze current state
        print("=== CURRENT AGENT NAMES ===")
        agents = normalizer.get_current_agents()
        for agent, count in agents:
            print(f"{agent:<30} {count:<10}")
        
        # Create normalization mapping
        mapping = normalizer.create_normalization_mapping()
        
        if not mapping:
            print("\n✅ No duplicates found - no normalization needed!")
            return
        
        # Ask user for confirmation
        print(f"\nFound {len(mapping)} agent names to normalize.")
        response = input("\nDo you want to proceed with normalization? (y/N): ").strip().lower()
        
        if response not in ['y', 'yes']:
            print("Normalization cancelled.")
            return
        
        # Create backup
        backup_path = normalizer.backup_database()
        
        # Run dry run first
        normalizer.normalize_agent_names(mapping, dry_run=True)
        
        # Ask for final confirmation
        response = input("\nProceed with actual changes? (y/N): ").strip().lower()
        
        if response not in ['y', 'yes']:
            print("Changes cancelled. Database backup available at:", backup_path)
            return
        
        # Apply changes
        normalizer.normalize_agent_names(mapping, dry_run=False)
        
        # Verify results
        normalizer.verify_normalization()
        
        print(f"\n✅ Agent name normalization completed successfully!")
        print(f"Backup available at: {backup_path}")
        
    except Exception as e:
        print(f"❌ Error during normalization: {e}")
    finally:
        normalizer.close_database()

if __name__ == "__main__":
    main()
    input("\nPress Enter to continue...")
