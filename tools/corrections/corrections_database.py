"""
Corrections Database - Track review actions for analysis

This module tracks all corrections and approvals made during manual review.
Use this data to identify:
- Frequently corrected words (candidates for dictionary or systematic fixes)
- Frequently approved words (may need lower flagging thresholds)
- Common correction patterns
"""

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Database location
DB_PATH = Path(__file__).parent / "corrections_history.db"


@dataclass
class CorrectionRecord:
    """Represents a single correction action."""
    
    # Identification
    timestamp: str
    file_name: str
    word_index: int
    
    # Word details
    original_word: str
    corrected_word: str
    confidence: Optional[float]
    speaker: Optional[str]
    
    # Context
    context_before: str
    context_after: str
    
    # Review metadata
    flag_types: List[str]  # What flags were on this word
    action: str  # "corrected", "approved", "dictionary_added"


@dataclass
class ApprovalRecord:
    """Represents a word approval action."""
    
    # Identification
    timestamp: str
    file_name: str
    word_index: int
    
    # Word details
    word: str
    confidence: Optional[float]
    speaker: Optional[str]
    
    # Context
    context_before: str
    context_after: str
    
    # Review metadata
    flag_types: List[str]


@dataclass
class DictionaryAddition:
    """Represents adding a term to the dictionary."""
    
    timestamp: str
    file_name: str
    term: str
    original_word: str
    confidence: Optional[float]
    was_correction: bool  # True if it was corrected first


def initialize_database():
    """Create the database schema if it doesn't exist."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        
        # Corrections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                file_name TEXT NOT NULL,
                word_index INTEGER NOT NULL,
                original_word TEXT NOT NULL,
                corrected_word TEXT NOT NULL,
                confidence REAL,
                speaker TEXT,
                context_before TEXT,
                context_after TEXT,
                flag_types TEXT NOT NULL,
                action TEXT NOT NULL,
                UNIQUE(file_name, word_index, timestamp)
            )
        """)
        
        # Approvals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                file_name TEXT NOT NULL,
                word_index INTEGER NOT NULL,
                word TEXT NOT NULL,
                confidence REAL,
                speaker TEXT,
                context_before TEXT,
                context_after TEXT,
                flag_types TEXT NOT NULL,
                UNIQUE(file_name, word_index, timestamp)
            )
        """)
        
        # Dictionary additions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dictionary_additions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                file_name TEXT NOT NULL,
                term TEXT NOT NULL,
                original_word TEXT NOT NULL,
                confidence REAL,
                was_correction INTEGER NOT NULL,
                UNIQUE(file_name, term, timestamp)
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_corrections_word 
            ON corrections(original_word, corrected_word)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_approvals_word 
            ON approvals(word)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_dictionary_term 
            ON dictionary_additions(term)
        """)
        
        conn.commit()


@contextmanager
def _get_connection():
    """Get a database connection with proper cleanup."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def log_correction(
    file_name: str,
    word_index: int,
    original_word: str,
    corrected_word: str,
    confidence: Optional[float] = None,
    speaker: Optional[str] = None,
    context_before: str = "",
    context_after: str = "",
    flag_types: Optional[List[str]] = None,
    action: str = "corrected"
) -> int:
    """
    Log a correction to the database.
    
    Returns:
        The ID of the inserted record
    """
    initialize_database()
    
    record = CorrectionRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        file_name=file_name,
        word_index=word_index,
        original_word=original_word,
        corrected_word=corrected_word,
        confidence=confidence,
        speaker=speaker,
        context_before=context_before,
        context_after=context_after,
        flag_types=flag_types or [],
        action=action
    )
    
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO corrections 
            (timestamp, file_name, word_index, original_word, corrected_word, 
             confidence, speaker, context_before, context_after, flag_types, action)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.timestamp,
            record.file_name,
            record.word_index,
            record.original_word,
            record.corrected_word,
            record.confidence,
            record.speaker,
            record.context_before,
            record.context_after,
            json.dumps(record.flag_types),
            record.action
        ))
        conn.commit()
        return cursor.lastrowid


def log_approval(
    file_name: str,
    word_index: int,
    word: str,
    confidence: Optional[float] = None,
    speaker: Optional[str] = None,
    context_before: str = "",
    context_after: str = "",
    flag_types: Optional[List[str]] = None
) -> int:
    """
    Log an approval to the database.
    
    Returns:
        The ID of the inserted record
    """
    initialize_database()
    
    record = ApprovalRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        file_name=file_name,
        word_index=word_index,
        word=word,
        confidence=confidence,
        speaker=speaker,
        context_before=context_before,
        context_after=context_after,
        flag_types=flag_types or []
    )
    
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO approvals 
            (timestamp, file_name, word_index, word, confidence, speaker, 
             context_before, context_after, flag_types)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.timestamp,
            record.file_name,
            record.word_index,
            record.word,
            record.confidence,
            record.speaker,
            record.context_before,
            record.context_after,
            json.dumps(record.flag_types)
        ))
        conn.commit()
        return cursor.lastrowid


def log_dictionary_addition(
    file_name: str,
    term: str,
    original_word: str,
    confidence: Optional[float] = None,
    was_correction: bool = False
) -> int:
    """
    Log a dictionary addition.
    
    Returns:
        The ID of the inserted record
    """
    initialize_database()
    
    record = DictionaryAddition(
        timestamp=datetime.now(timezone.utc).isoformat(),
        file_name=file_name,
        term=term,
        original_word=original_word,
        confidence=confidence,
        was_correction=was_correction
    )
    
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO dictionary_additions 
            (timestamp, file_name, term, original_word, confidence, was_correction)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            record.timestamp,
            record.file_name,
            record.term,
            record.original_word,
            record.confidence,
            1 if record.was_correction else 0
        ))
        conn.commit()
        return cursor.lastrowid


def get_correction_statistics() -> Dict:
    """
    Get statistics about corrections.
    
    Returns:
        Dictionary with correction statistics
    """
    initialize_database()
    
    with _get_connection() as conn:
        cursor = conn.cursor()
        
        # Most frequently corrected words
        cursor.execute("""
            SELECT original_word, corrected_word, COUNT(*) as count,
                   AVG(confidence) as avg_confidence
            FROM corrections
            GROUP BY original_word, corrected_word
            ORDER BY count DESC
            LIMIT 50
        """)
        frequent_corrections = [
            {
                "original": row["original_word"],
                "corrected": row["corrected_word"],
                "count": row["count"],
                "avg_confidence": row["avg_confidence"]
            }
            for row in cursor.fetchall()
        ]
        
        # Total statistics
        cursor.execute("SELECT COUNT(*) as total FROM corrections")
        total_corrections = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(*) as total FROM approvals")
        total_approvals = cursor.fetchone()["total"]
        
        cursor.execute("SELECT COUNT(DISTINCT file_name) as total FROM corrections")
        files_corrected = cursor.fetchone()["total"]
        
        return {
            "total_corrections": total_corrections,
            "total_approvals": total_approvals,
            "files_corrected": files_corrected,
            "frequent_corrections": frequent_corrections
        }


def get_approval_statistics() -> Dict:
    """
    Get statistics about approvals.
    
    Returns:
        Dictionary with approval statistics
    """
    initialize_database()
    
    with _get_connection() as conn:
        cursor = conn.cursor()
        
        # Most frequently approved words
        cursor.execute("""
            SELECT word, COUNT(*) as count,
                   AVG(confidence) as avg_confidence
            FROM approvals
            GROUP BY word
            ORDER BY count DESC
            LIMIT 50
        """)
        frequent_approvals = [
            {
                "word": row["word"],
                "count": row["count"],
                "avg_confidence": row["avg_confidence"]
            }
            for row in cursor.fetchall()
        ]
        
        return {
            "frequent_approvals": frequent_approvals
        }


def get_dictionary_statistics() -> Dict:
    """
    Get statistics about dictionary additions.
    
    Returns:
        Dictionary with dictionary addition statistics
    """
    initialize_database()
    
    with _get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT term, original_word, COUNT(*) as count,
                   AVG(confidence) as avg_confidence,
                   SUM(was_correction) as correction_count
            FROM dictionary_additions
            GROUP BY term
            ORDER BY count DESC
        """)
        dictionary_terms = [
            {
                "term": row["term"],
                "original_word": row["original_word"],
                "count": row["count"],
                "avg_confidence": row["avg_confidence"],
                "was_correction": row["correction_count"] > 0
            }
            for row in cursor.fetchall()
        ]
        
        return {
            "dictionary_terms": dictionary_terms,
            "total_terms": len(dictionary_terms)
        }


if __name__ == "__main__":
    # Initialize database and show statistics
    initialize_database()
    print(f"[OK] Database initialized: {DB_PATH}")
    
    stats = get_correction_statistics()
    print(f"\n[STATS] Statistics:")
    print(f"  Total corrections: {stats['total_corrections']}")
    print(f"  Total approvals: {stats['total_approvals']}")
    print(f"  Files corrected: {stats['files_corrected']}")

