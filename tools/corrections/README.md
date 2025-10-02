# Corrections Tracking System

This system tracks all corrections and approvals made during manual review to help identify patterns and finalize the transcription pipeline.

## 📁 Files

- **`corrections_database.py`** - Core database module for storing corrections/approvals
- **`analyze_corrections.py`** - Analysis tool that generates reports and recommendations
- **`log_review_actions.py`** - Bridge script for logging actions from the review UI
- **`corrections_history.db`** - SQLite database (created automatically)
- **`analyze.bat`** - Quick launcher for analysis report
- **`log_from_review.bat`** - Quick launcher for logging from saved review files

## 🎯 Purpose

### What It Tracks:
1. **Corrections** - When words are manually corrected
   - Original word → Corrected word
   - Confidence scores
   - Context
   - Frequency

2. **Approvals** - When flagged words are approved as correct
   - Word text
   - Why it was flagged
   - How often it's approved

3. **Dictionary Additions** - Terms added to the dictionary queue
   - Terms
   - Frequency
   - Whether they were corrections first

### Why It Matters:
- **Identify systematic issues** - Words that are always corrected the same way
- **Refine dictionary** - Frequently corrected words should be in `nouns_to_expect.txt`
- **Adjust thresholds** - Words approved often may indicate flagging rules are too strict
- **Measure progress** - Track how many corrections are needed over time

## 🚀 Quick Start

### 1. Automatic Logging (When Saving Reviews)

When you save a review file in the UI, it will be automatically logged. Or manually log it:

```batch
log_from_review.bat output\x105_2025-07-10.11-33.review.json
```

### 2. Generate Analysis Report

```batch
analyze.bat
```

This shows:
- **Dictionary Recommendations** - Terms to add to `nouns_to_expect.txt`
- **Frequently Approved Words** - May need threshold adjustments
- **Systematic Corrections** - Patterns that could be automated
- **Top Corrections** - Most common corrections overall

### 3. Export Recommendations to JSON

```batch
analyze.bat --export
```

Creates `recommendations.json` with all insights.

## 📊 Example Report

```
📊 CORRECTIONS ANALYSIS REPORT
================================================================================

📈 OVERALL STATISTICS
--------------------------------------------------------------------------------
  Total Corrections:     47
  Total Approvals:       23
  Files Reviewed:        3
  Dictionary Terms:      5

📖 DICTIONARY RECOMMENDATIONS
--------------------------------------------------------------------------------
  Terms to add to config/nouns_to_expect.txt (8 recommended):

    • Vasquez
      └─ Corrected from 'Vazquez' 5 times (avg confidence: 68.2%)
    
    • LaFleur
      └─ Corrected from 'LaFlower' 3 times (avg confidence: 72.1%)

✓ FREQUENTLY APPROVED WORDS
--------------------------------------------------------------------------------
  Words approved often (4 found):

    • 'the' - Approved 8 times (avg: 45.3%)
      └─ Approved 8 times - consider adjusting threshold

🔄 SYSTEMATIC CORRECTIONS
--------------------------------------------------------------------------------
  Corrections that follow a consistent pattern (3 found):

    • 'Vazquez' → 'Vasquez'
      └─ 5 times (avg: 68.2%) - Can be automated with find/replace
```

## 🔧 Advanced Usage

### Direct Python Usage

```python
from tools.corrections.corrections_database import (
    log_correction,
    log_approval,
    get_correction_statistics
)

# Log a correction
log_correction(
    file_name="x105_2025-07-10",
    word_index=42,
    original_word="Vazquez",
    corrected_word="Vasquez",
    confidence=0.68,
    flag_types=["low_confidence", "name"]
)

# Get statistics
stats = get_correction_statistics()
print(f"Total corrections: {stats['total_corrections']}")
```

### Query the Database Directly

```bash
sqlite3 tools/corrections/corrections_history.db

# Most corrected words
SELECT original_word, corrected_word, COUNT(*) as count 
FROM corrections 
GROUP BY original_word, corrected_word 
ORDER BY count DESC 
LIMIT 10;

# Most approved words
SELECT word, COUNT(*) as count 
FROM approvals 
GROUP BY word 
ORDER BY count DESC 
LIMIT 10;
```

## 🎓 Workflow

### Step 1: Review Transcripts
Use the review UI to correct and approve words as usual.

### Step 2: Save Review File
Click "💿 Save Review File" in the UI.

### Step 3: Log Actions
```batch
log_from_review.bat output\your_file.review.json
```

### Step 4: Analyze (After Several Reviews)
```batch
analyze.bat
```

### Step 5: Apply Recommendations
1. Add recommended terms to `config/nouns_to_expect.txt`
2. Adjust confidence thresholds if needed in:
   - `tools/review_tools/assemblyai_review_generator.py` (lines 34-36)
   - `tools/review_tools/assemblyai_review_ui.html` (lines 547-550)
3. Add systematic corrections to the dictionary

### Step 6: Re-test
Process new files and see if fewer corrections are needed!

## 📈 Measuring Success

Track these metrics over time:
- **Corrections per file** - Should decrease as dictionary improves
- **Approval rate** - High approval rate means flagging is working
- **Systematic corrections** - Should approach zero after fixing patterns

## 🔗 Integration with Review UI

The review UI automatically saves corrections and approvals in the review file format. The logging system reads these files and extracts:

- All corrections made (original → corrected)
- All approved words
- All dictionary additions

This means **you don't need to do anything special** - just save your review files and run the analyzer!

## 💡 Tips

1. **Review at least 5-10 files** before analyzing - more data = better insights
2. **Export to JSON** for custom analysis or reporting
3. **Run analysis regularly** to track improvement over time
4. **Back up the database** periodically: `corrections_history.db`

## 🎯 Final Project Goals

Use this system to:
1. **Build comprehensive dictionary** - All common proper nouns
2. **Optimize confidence thresholds** - Balance false positives vs. false negatives
3. **Identify systematic issues** - Fix at the source (transcription settings, audio quality, etc.)
4. **Measure quality** - Track corrections needed over time
5. **Document patterns** - Share insights with team

---

**Database Location:** `tools/corrections/corrections_history.db`  
**Recommendations:** `tools/corrections/recommendations.json` (after export)

