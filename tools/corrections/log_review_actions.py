"""
Bridge script for logging review actions from the UI

This script is called by the review UI to log corrections and approvals
to the database for later analysis.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.corrections.corrections_database import (
    log_correction,
    log_approval,
    log_dictionary_addition,
    initialize_database
)


def log_actions_from_file(review_file_path: str) -> dict:
    """
    Log all corrections and approvals from a saved review file.
    
    Args:
        review_file_path: Path to the .review.json file
        
    Returns:
        Dictionary with counts of logged actions
    """
    initialize_database()
    
    review_path = Path(review_file_path)
    if not review_path.exists():
        return {"error": f"File not found: {review_file_path}"}
    
    with open(review_path, 'r', encoding='utf-8') as f:
        review_data = json.load(f)
    
    file_name = review_path.stem  # Use filename without extension
    words = review_data.get("words", [])
    corrections_list = review_data.get("corrections", [])
    approved_words = set(review_data.get("approved_words", []))
    dictionary_terms = review_data.get("dictionary_terms", [])
    
    # Log corrections
    corrections_logged = 0
    for corr in corrections_list:
        word_idx = corr.get("word_index")
        if word_idx is not None and word_idx < len(words):
            word_data = words[word_idx]
            
            log_correction(
                file_name=file_name,
                word_index=word_idx,
                original_word=corr.get("original_word", word_data.get("word", "")),
                corrected_word=corr.get("corrected_word", ""),
                confidence=word_data.get("confidence"),
                speaker=word_data.get("speaker"),
                context_before=word_data.get("context_before", ""),
                context_after=word_data.get("context_after", ""),
                flag_types=[f.get("type") for f in word_data.get("flags", [])],
                action="corrected"
            )
            corrections_logged += 1
    
    # Log approvals
    approvals_logged = 0
    for word_idx in approved_words:
        if word_idx < len(words):
            word_data = words[word_idx]
            
            log_approval(
                file_name=file_name,
                word_index=word_idx,
                word=word_data.get("word", ""),
                confidence=word_data.get("confidence"),
                speaker=word_data.get("speaker"),
                context_before=word_data.get("context_before", ""),
                context_after=word_data.get("context_after", ""),
                flag_types=[f.get("type") for f in word_data.get("flags", [])]
            )
            approvals_logged += 1
    
    # Log dictionary additions
    dictionary_logged = 0
    for term in dictionary_terms:
        if isinstance(term, dict):
            term_str = term.get("term", "")
            original = term.get("original_word", "")
        else:
            term_str = term
            original = term
        
        if term_str:
            log_dictionary_addition(
                file_name=file_name,
                term=term_str,
                original_word=original,
                confidence=None,
                was_correction=False
            )
            dictionary_logged += 1
    
    return {
        "success": True,
        "file_name": file_name,
        "corrections_logged": corrections_logged,
        "approvals_logged": approvals_logged,
        "dictionary_terms_logged": dictionary_logged
    }


def log_single_action(action_data: dict) -> dict:
    """
    Log a single action from the UI.
    
    Args:
        action_data: Dictionary with action details
        
    Returns:
        Result dictionary
    """
    initialize_database()
    
    action_type = action_data.get("type")
    
    try:
        if action_type == "correction":
            log_correction(
                file_name=action_data.get("file_name", "unknown"),
                word_index=action_data.get("word_index", 0),
                original_word=action_data.get("original_word", ""),
                corrected_word=action_data.get("corrected_word", ""),
                confidence=action_data.get("confidence"),
                speaker=action_data.get("speaker"),
                context_before=action_data.get("context_before", ""),
                context_after=action_data.get("context_after", ""),
                flag_types=action_data.get("flag_types", []),
                action="corrected"
            )
            return {"success": True, "action": "correction"}
            
        elif action_type == "approval":
            log_approval(
                file_name=action_data.get("file_name", "unknown"),
                word_index=action_data.get("word_index", 0),
                word=action_data.get("word", ""),
                confidence=action_data.get("confidence"),
                speaker=action_data.get("speaker"),
                context_before=action_data.get("context_before", ""),
                context_after=action_data.get("context_after", ""),
                flag_types=action_data.get("flag_types", [])
            )
            return {"success": True, "action": "approval"}
            
        elif action_type == "dictionary":
            log_dictionary_addition(
                file_name=action_data.get("file_name", "unknown"),
                term=action_data.get("term", ""),
                original_word=action_data.get("original_word", ""),
                confidence=action_data.get("confidence"),
                was_correction=action_data.get("was_correction", False)
            )
            return {"success": True, "action": "dictionary"}
            
        else:
            return {"error": f"Unknown action type: {action_type}"}
            
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python log_review_actions.py <review_file.json>")
        print("  python log_review_actions.py --action '<json_action_data>'")
        sys.exit(1)
    
    if sys.argv[1] == "--action":
        # Log single action from JSON
        action_data = json.loads(sys.argv[2])
        result = log_single_action(action_data)
        print(json.dumps(result))
    else:
        # Log from review file
        result = log_actions_from_file(sys.argv[1])
        if result.get("success"):
            print(f"[OK] Logged actions from: {result['file_name']}")
            print(f"     Corrections: {result['corrections_logged']}")
            print(f"     Approvals: {result['approvals_logged']}")
            print(f"     Dictionary: {result['dictionary_terms_logged']}")
        else:
            print(f"[ERROR] {result.get('error')}")
            sys.exit(1)

