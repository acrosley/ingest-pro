"""
View Approved Words - Show what words are being approved frequently

This helps identify:
- Words that should be in the dictionary
- Confidence thresholds that are too strict
- Patterns in what gets flagged unnecessarily
"""

import sys
from pathlib import Path
from collections import Counter

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.corrections.corrections_database import initialize_database, _get_connection


def get_approved_words_detail(min_count=1):
    """Get detailed list of approved words."""
    initialize_database()
    
    with _get_connection() as conn:
        cursor = conn.cursor()
        
        # Get all approvals with details
        cursor.execute("""
            SELECT 
                word,
                confidence,
                flag_types,
                file_name,
                context_before,
                context_after
            FROM approvals
            ORDER BY word, confidence
        """)
        
        approvals = []
        for row in cursor.fetchall():
            approvals.append({
                'word': row['word'],
                'confidence': row['confidence'],
                'flag_types': row['flag_types'],
                'file_name': row['file_name'],
                'context_before': row['context_before'],
                'context_after': row['context_after']
            })
        
        return approvals


def analyze_approvals():
    """Analyze and display approved words."""
    approvals = get_approved_words_detail()
    
    if not approvals:
        print("[WARN] No approvals found in database yet.")
        return
    
    print("=" * 80)
    print("[APPROVED WORDS ANALYSIS]")
    print("=" * 80)
    print(f"Total approvals: {len(approvals)}\n")
    
    # Group by word
    word_data = {}
    for approval in approvals:
        word = approval['word']
        if word not in word_data:
            word_data[word] = []
        word_data[word].append(approval)
    
    # Sort by frequency
    sorted_words = sorted(word_data.items(), key=lambda x: len(x[1]), reverse=True)
    
    print("[FREQUENTLY APPROVED WORDS]")
    print("-" * 80)
    print(f"{'Word':<20} {'Count':<8} {'Avg Conf':<12} {'Flags'}")
    print("-" * 80)
    
    for word, instances in sorted_words[:30]:  # Top 30
        count = len(instances)
        
        # Calculate average confidence
        confidences = [inst['confidence'] for inst in instances if inst['confidence'] is not None]
        avg_conf = sum(confidences) / len(confidences) if confidences else None
        conf_str = f"{avg_conf:.1%}" if avg_conf is not None else "N/A"
        
        # Get unique flag types
        all_flags = []
        for inst in instances:
            import json
            flags = json.loads(inst['flag_types'])
            all_flags.extend(flags)
        
        unique_flags = list(set(all_flags))
        flags_str = ", ".join(unique_flags[:3])  # First 3 flags
        if len(unique_flags) > 3:
            flags_str += "..."
        
        print(f"{word:<20} {count:<8} {conf_str:<12} {flags_str}")
    
    print()
    
    # Recommendations
    print("[RECOMMENDATIONS]")
    print("-" * 80)
    
    recommendations = []
    
    for word, instances in sorted_words:
        count = len(instances)
        
        # Calculate average confidence
        confidences = [inst['confidence'] for inst in instances if inst['confidence'] is not None]
        avg_conf = sum(confidences) / len(confidences) if confidences else None
        
        # Get flag types
        all_flags = []
        for inst in instances:
            import json
            flags = json.loads(inst['flag_types'])
            all_flags.extend(flags)
        
        flag_counter = Counter(all_flags)
        
        # Recommendation logic
        if count >= 3:
            # Frequently approved - probably shouldn't be flagged
            if 'low_confidence' in flag_counter and avg_conf and avg_conf > 0.50:
                recommendations.append({
                    'word': word,
                    'count': count,
                    'avg_conf': avg_conf,
                    'action': f'Lower confidence threshold (currently flagged at {avg_conf:.1%})',
                    'priority': 'high'
                })
            elif 'name' in flag_counter:
                recommendations.append({
                    'word': word,
                    'count': count,
                    'avg_conf': avg_conf,
                    'action': 'Add to common words list (not a name)',
                    'priority': 'medium'
                })
    
    # Sort by priority and count
    recommendations.sort(key=lambda x: (x['priority'], -x['count']))
    
    if recommendations:
        print("\nActions to take:\n")
        for i, rec in enumerate(recommendations[:15], 1):
            conf_str = f"{rec['avg_conf']:.1%}" if rec['avg_conf'] else "N/A"
            print(f"{i:2d}. '{rec['word']}' (approved {rec['count']}x, avg: {conf_str})")
            print(f"    => {rec['action']}\n")
    else:
        print("No specific recommendations yet. Continue reviewing to build more data.\n")
    
    # Show context for most common
    if len(sorted_words) > 0:
        most_common_word, instances = sorted_words[0]
        print("[CONTEXT EXAMPLES]")
        print("-" * 80)
        print(f"Examples of '{most_common_word}' being approved:\n")
        
        for i, inst in enumerate(instances[:3], 1):
            context_before = inst['context_before'].strip()[-50:] if inst['context_before'] else ""
            context_after = inst['context_after'].strip()[:50] if inst['context_after'] else ""
            
            print(f"{i}. ...{context_before} [{most_common_word}] {context_after}...")
            
            import json
            flags = json.loads(inst['flag_types'])
            if flags:
                print(f"   Flags: {', '.join(flags)}")
            print()


if __name__ == "__main__":
    initialize_database()
    analyze_approvals()
    
    print("=" * 80)
    print()

