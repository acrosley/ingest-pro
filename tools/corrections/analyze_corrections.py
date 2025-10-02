"""
Corrections Analysis Tool

Analyzes the corrections database and generates actionable insights:
- Which words should be added to the dictionary
- Which corrections are systematic (can be automated)
- Which words are frequently approved (threshold too strict)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.corrections.corrections_database import (
    get_correction_statistics,
    get_approval_statistics,
    get_dictionary_statistics,
    initialize_database,
    DB_PATH
)


def generate_dictionary_recommendations(min_count: int = 3) -> List[Dict]:
    """
    Generate recommendations for terms to add to nouns_to_expect.txt
    
    Args:
        min_count: Minimum number of occurrences to recommend
        
    Returns:
        List of recommended terms with metadata
    """
    stats = get_correction_statistics()
    recommendations = []
    
    for correction in stats["frequent_corrections"]:
        if correction["count"] >= min_count:
            # If same correction applied multiple times, recommend adding it
            recommendations.append({
                "term": correction["corrected"],
                "frequency": correction["count"],
                "reason": f"Corrected from '{correction['original']}' {correction['count']} times",
                "avg_confidence": correction["avg_confidence"],
                "action": "Add to dictionary"
            })
    
    return recommendations


def generate_approval_recommendations(min_count: int = 5) -> List[Dict]:
    """
    Generate recommendations for words that are approved frequently
    (may indicate threshold is too strict)
    
    Args:
        min_count: Minimum number of approvals to recommend
        
    Returns:
        List of recommendations
    """
    stats = get_approval_statistics()
    recommendations = []
    
    for approval in stats["frequent_approvals"]:
        if approval["count"] >= min_count:
            # If approved many times, might be flagged unnecessarily
            recommendations.append({
                "word": approval["word"],
                "frequency": approval["count"],
                "avg_confidence": approval["avg_confidence"],
                "reason": f"Approved {approval['count']} times - consider adding to dictionary or adjusting threshold",
                "action": "Review flagging rules"
            })
    
    return recommendations


def generate_systematic_corrections() -> List[Dict]:
    """
    Identify corrections that are always the same (can be automated).
    
    Returns:
        List of systematic corrections
    """
    stats = get_correction_statistics()
    systematic = []
    
    # Track corrections by original word
    corrections_by_word = {}
    for correction in stats["frequent_corrections"]:
        original = correction["original"]
        if original not in corrections_by_word:
            corrections_by_word[original] = []
        corrections_by_word[original].append(correction)
    
    # Find words that are always corrected the same way
    for original, corrections_list in corrections_by_word.items():
        if len(corrections_list) == 1 and corrections_list[0]["count"] >= 3:
            # Single correction pattern with 3+ instances
            correction = corrections_list[0]
            systematic.append({
                "original": original,
                "correction": correction["corrected"],
                "frequency": correction["count"],
                "avg_confidence": correction["avg_confidence"],
                "action": "Can be automated with find/replace or custom rule"
            })
    
    return systematic


def print_report():
    """Generate and print a comprehensive analysis report."""
    print("=" * 80)
    print("[REPORT] CORRECTIONS ANALYSIS")
    print("=" * 80)
    print(f"Database: {DB_PATH}\n")
    
    # Overall statistics
    correction_stats = get_correction_statistics()
    approval_stats = get_approval_statistics()
    dict_stats = get_dictionary_statistics()
    
    print("[STATS] OVERALL STATISTICS")
    print("-" * 80)
    print(f"  Total Corrections:     {correction_stats['total_corrections']}")
    print(f"  Total Approvals:       {correction_stats['total_approvals']}")
    print(f"  Files Reviewed:        {correction_stats['files_corrected']}")
    print(f"  Dictionary Terms:      {dict_stats['total_terms']}")
    print()
    
    # Dictionary recommendations
    dict_recommendations = generate_dictionary_recommendations(min_count=2)
    if dict_recommendations:
        print("[DICT] DICTIONARY RECOMMENDATIONS")
        print("-" * 80)
        print(f"  Terms to add to config/nouns_to_expect.txt ({len(dict_recommendations)} recommended):\n")
        
        for rec in dict_recommendations[:20]:  # Top 20
            conf_str = f"{rec['avg_confidence']:.1%}" if rec['avg_confidence'] else "N/A"
            print(f"    • {rec['term']}")
            print(f"      └─ {rec['reason']} (avg confidence: {conf_str})")
        
        if len(dict_recommendations) > 20:
            print(f"\n    ... and {len(dict_recommendations) - 20} more")
        print()
    
    # Approval recommendations
    approval_recommendations = generate_approval_recommendations(min_count=3)
    if approval_recommendations:
        print("[APPROVED] FREQUENTLY APPROVED WORDS")
        print("-" * 80)
        print(f"  Words approved often ({len(approval_recommendations)} found):\n")
        
        for rec in approval_recommendations[:15]:  # Top 15
            conf_str = f"{rec['avg_confidence']:.1%}" if rec['avg_confidence'] else "N/A"
            print(f"    • '{rec['word']}' - Approved {rec['frequency']} times (avg: {conf_str})")
            print(f"      └─ {rec['reason']}")
        
        if len(approval_recommendations) > 15:
            print(f"\n    ... and {len(approval_recommendations) - 15} more")
        print()
    
    # Systematic corrections
    systematic = generate_systematic_corrections()
    if systematic:
        print("[SYSTEMATIC] CORRECTIONS")
        print("-" * 80)
        print(f"  Corrections that follow a consistent pattern ({len(systematic)} found):\n")
        
        for corr in systematic[:15]:  # Top 15
            conf_str = f"{corr['avg_confidence']:.1%}" if corr['avg_confidence'] else "N/A"
            print(f"    • '{corr['original']}' → '{corr['correction']}'")
            print(f"      └─ {corr['frequency']} times (avg: {conf_str}) - {corr['action']}")
        
        if len(systematic) > 15:
            print(f"\n    ... and {len(systematic) - 15} more")
        print()
    
    # Most frequent corrections
    if correction_stats['frequent_corrections']:
        print("[TOP] MOST FREQUENT CORRECTIONS")
        print("-" * 80)
        print("  Most frequently corrected words:\n")
        
        for i, corr in enumerate(correction_stats['frequent_corrections'][:10], 1):
            conf_str = f"{corr['avg_confidence']:.1%}" if corr['avg_confidence'] else "N/A"
            print(f"    {i:2d}. '{corr['original']}' → '{corr['corrected']}'")
            print(f"        ({corr['count']} times, avg confidence: {conf_str})")
        print()
    
    print("=" * 80)
    print("[NEXT STEPS]")
    print("=" * 80)
    print("  1. Review dictionary recommendations and add to config/nouns_to_expect.txt")
    print("  2. Consider adjusting confidence thresholds for frequently approved words")
    print("  3. Implement systematic corrections as automated rules if appropriate")
    print("  4. Continue reviewing transcripts to build more data")
    print()


def export_recommendations_to_file(output_path: Path = None):
    """Export recommendations to a JSON file for easy processing."""
    if output_path is None:
        output_path = Path(__file__).parent / "recommendations.json"
    
    recommendations = {
        "generated_at": str(Path(DB_PATH).stat().st_mtime),
        "dictionary_recommendations": generate_dictionary_recommendations(min_count=2),
        "approval_recommendations": generate_approval_recommendations(min_count=3),
        "systematic_corrections": generate_systematic_corrections(),
        "statistics": {
            **get_correction_statistics(),
            **get_approval_statistics(),
            **get_dictionary_statistics()
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Recommendations exported to: {output_path}")
    return output_path


if __name__ == "__main__":
    initialize_database()
    
    # Check if database has data
    stats = get_correction_statistics()
    if stats['total_corrections'] == 0 and stats['total_approvals'] == 0:
        print("[WARN] No corrections or approvals found in database yet.")
        print("       Start reviewing transcripts to build up data.")
        print(f"       Database: {DB_PATH}")
    else:
        print_report()
        
        # Optionally export to JSON
        if len(sys.argv) > 1 and sys.argv[1] == "--export":
            export_recommendations_to_file()

