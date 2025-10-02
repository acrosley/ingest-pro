#!/usr/bin/env python3
"""
Database for tracking manual corrections to transcripts.
Stores corrections to learn from and improve future transcriptions.
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class CorrectionsDatabase:
    """Manages the corrections database for tracking manual reviews."""
    
    def __init__(self, db_path: str = "tools/review_tools/corrections.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audio_file TEXT NOT NULL,
                    word_index INTEGER NOT NULL,
                    original_word TEXT NOT NULL,
                    corrected_word TEXT NOT NULL,
                    correction_type TEXT NOT NULL,
                    flag_types TEXT,
                    context_before TEXT,
                    context_after TEXT,
                    confidence REAL,
                    whisper_version TEXT,
                    timestamp TEXT NOT NULL,
                    reviewer TEXT,
                    notes TEXT,
                    UNIQUE(audio_file, word_index)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vocabulary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL UNIQUE,
                    category TEXT,
                    frequency INTEGER DEFAULT 1,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_corrections_audio 
                ON corrections(audio_file)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_vocabulary_word 
                ON vocabulary(word)
            """)
            
            conn.commit()
    
    def save_correction(
        self,
        audio_file: str,
        word_index: int,
        original_word: str,
        corrected_word: str,
        correction_type: str,
        flag_types: List[str] = None,
        context_before: str = "",
        context_after: str = "",
        confidence: Optional[float] = None,
        whisper_version: Optional[str] = None,
        reviewer: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Save a manual correction.
        
        Returns:
            The correction ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO corrections 
                (audio_file, word_index, original_word, corrected_word, correction_type,
                 flag_types, context_before, context_after, confidence, whisper_version,
                 timestamp, reviewer, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audio_file,
                word_index,
                original_word,
                corrected_word,
                correction_type,
                json.dumps(flag_types) if flag_types else None,
                context_before,
                context_after,
                confidence,
                whisper_version,
                datetime.now(timezone.utc).isoformat(),
                reviewer,
                notes
            ))
            
            correction_id = cursor.lastrowid
            
            # Update vocabulary if this is a proper noun or important term
            if correction_type in ['proper_noun', 'case_number', 'phone_number']:
                self._update_vocabulary(corrected_word, correction_type)
            
            conn.commit()
            return correction_id
    
    def _update_vocabulary(self, word: str, category: str):
        """Update the learned vocabulary."""
        now = datetime.now(timezone.utc).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Check if word exists
            cursor = conn.execute(
                "SELECT id, frequency FROM vocabulary WHERE word = ?",
                (word,)
            )
            result = cursor.fetchone()
            
            if result:
                # Update frequency
                conn.execute("""
                    UPDATE vocabulary 
                    SET frequency = frequency + 1, last_seen = ?
                    WHERE id = ?
                """, (now, result[0]))
            else:
                # Insert new word
                conn.execute("""
                    INSERT INTO vocabulary (word, category, first_seen, last_seen)
                    VALUES (?, ?, ?, ?)
                """, (word, category, now, now))
            
            conn.commit()
    
    def get_corrections_for_file(self, audio_file: str) -> List[Dict]:
        """Get all corrections for a specific audio file."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM corrections 
                WHERE audio_file = ?
                ORDER BY word_index
            """, (audio_file,))
            
            corrections = []
            for row in cursor.fetchall():
                correction = dict(row)
                if correction['flag_types']:
                    correction['flag_types'] = json.loads(correction['flag_types'])
                corrections.append(correction)
            
            return corrections
    
    def get_learned_vocabulary(self, category: Optional[str] = None, min_frequency: int = 2) -> List[str]:
        """
        Get learned vocabulary that appears frequently.
        Useful for building custom dictionaries.
        """
        with sqlite3.connect(self.db_path) as conn:
            if category:
                cursor = conn.execute("""
                    SELECT word FROM vocabulary 
                    WHERE category = ? AND frequency >= ?
                    ORDER BY frequency DESC
                """, (category, min_frequency))
            else:
                cursor = conn.execute("""
                    SELECT word FROM vocabulary 
                    WHERE frequency >= ?
                    ORDER BY frequency DESC
                """, (min_frequency,))
            
            return [row[0] for row in cursor.fetchall()]
    
    def get_correction_statistics(self) -> Dict:
        """Get statistics about corrections."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total corrections
            cursor = conn.execute("SELECT COUNT(*) FROM corrections")
            stats['total_corrections'] = cursor.fetchone()[0]
            
            # By correction type
            cursor = conn.execute("""
                SELECT correction_type, COUNT(*) as count 
                FROM corrections 
                GROUP BY correction_type
                ORDER BY count DESC
            """)
            stats['by_type'] = dict(cursor.fetchall())
            
            # Vocabulary size
            cursor = conn.execute("SELECT COUNT(*) FROM vocabulary")
            stats['vocabulary_size'] = cursor.fetchone()[0]
            
            # Most common corrections
            cursor = conn.execute("""
                SELECT original_word, corrected_word, COUNT(*) as count
                FROM corrections
                GROUP BY original_word, corrected_word
                HAVING count > 1
                ORDER BY count DESC
                LIMIT 10
            """)
            stats['common_mistakes'] = [
                {"from": row[0], "to": row[1], "count": row[2]}
                for row in cursor.fetchall()
            ]
            
            return stats
    
    def export_corrections_to_review_json(self, review_json_path: Path) -> bool:
        """
        Add saved corrections to a review JSON file.
        """
        try:
            with open(review_json_path, 'r', encoding='utf-8') as f:
                review_data = json.load(f)
            
            audio_file = review_data.get('audio_file')
            corrections = self.get_corrections_for_file(audio_file)
            
            if corrections:
                review_data['corrections'] = corrections
                
                with open(review_json_path, 'w', encoding='utf-8') as f:
                    json.dump(review_data, f, indent=2, ensure_ascii=False)
                
                return True
            
            return False
        
        except Exception as e:
            print(f"Error exporting corrections: {e}")
            return False


# Singleton instance
_db_instance = None

def get_corrections_db(db_path: str = "tools/review_tools/corrections.db") -> CorrectionsDatabase:
    """Get or create the corrections database singleton."""
    global _db_instance
    if _db_instance is None:
        _db_instance = CorrectionsDatabase(db_path)
    return _db_instance




