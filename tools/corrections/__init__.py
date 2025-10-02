"""
Corrections Tracking System

Track and analyze manual review corrections to improve transcription quality.
"""

from .corrections_database import (
    initialize_database,
    log_correction,
    log_approval,
    log_dictionary_addition,
    get_correction_statistics,
    get_approval_statistics,
    get_dictionary_statistics,
)

__all__ = [
    "initialize_database",
    "log_correction",
    "log_approval",
    "log_dictionary_addition",
    "get_correction_statistics",
    "get_approval_statistics",
    "get_dictionary_statistics",
]

