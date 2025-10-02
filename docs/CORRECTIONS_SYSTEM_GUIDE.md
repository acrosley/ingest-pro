# 📊 Corrections Tracking System - Quick Start Guide

The corrections tracking system helps you finalize your transcription pipeline by analyzing patterns in manual corrections.

## 🎯 What It Does

Tracks every correction and approval you make during review to identify:
- **Words that need to be in the dictionary** (frequently corrected the same way)
- **Words flagged too strictly** (frequently approved without changes)
- **Systematic issues** (patterns that can be automated)
- **Progress over time** (fewer corrections = better setup)

## 📁 Location

All tools are in: `tools\corrections\`

## 🚀 Quick Start (3 Steps)

### Step 1: Review & Save
1. Open the review UI: `tools\review_tools\launch_assemblyai_review.bat`
2. Review your transcript (correct/approve words as usual)
3. Click **"💿 Save Review File"**
4. Save to `output\` folder (e.g., `output\x105_2025-07-10.review.json`)

### Step 2: Log Actions
```batch
cd tools\corrections
log_from_review.bat ..\..\output\x105_2025-07-10.review.json
```

Or drag-and-drop the review file onto `log_from_review.bat`

### Step 3: Analyze (After 5-10 Reviews)
```batch
cd tools\corrections
analyze.bat
```

## 📊 What You'll See

```
📊 CORRECTIONS ANALYSIS REPORT
================================================================================

📈 OVERALL STATISTICS
  Total Corrections:     47
  Total Approvals:       23
  Files Reviewed:        3

📖 DICTIONARY RECOMMENDATIONS
  Terms to add to config/nouns_to_expect.txt:

    • Vasquez (corrected 5 times from 'Vazquez')
    • Methodist (corrected 4 times from 'Methodis')
    • LaFleur (corrected 3 times from 'LaFlower')

✓ FREQUENTLY APPROVED WORDS
  Words that are approved often (may be flagged too strictly):

    • 'the' - Approved 8 times at 45% confidence
    • 'and' - Approved 6 times at 42% confidence

🔄 SYSTEMATIC CORRECTIONS
  Corrections that follow a consistent pattern:

    • 'Vazquez' → 'Vasquez' (5 times)
      Can be automated or added to dictionary
```

## 🎓 Taking Action

### 1. Update Dictionary
Add recommended terms to `config\nouns_to_expect.txt`:
```
Vasquez
Methodist
LaFleur
```

### 2. Adjust Thresholds (If Needed)
If common words are flagged too often, lower the threshold:

**Python Generator** (`tools\review_tools\assemblyai_review_generator.py`):
```python
common_words_confidence_threshold: float = 0.40  # Lower this (e.g., 0.35)
```

**JavaScript UI** (`tools\review_tools\assemblyai_review_ui.html`):
```javascript
commonWords: 0.40,  // Lower this (e.g., 0.35)
```

### 3. Test Improvements
Process a new file and check if fewer corrections are needed!

## 📈 Measuring Success

| Metric | Goal |
|--------|------|
| **Corrections per file** | Decrease over time |
| **Critical flags** | < 5 per file |
| **Approval rate** | 60-80% (shows good flagging) |
| **Dictionary size** | Grows to cover your domain |

## 🔄 Workflow

```
Review → Save → Log → Analyze → Update → Repeat
  └─────────────────────┬─────────────────┘
                 Build up data
                        ↓
              After 5-10 reviews
                        ↓
              Generate report
                        ↓
        Apply recommendations
                        ↓
          Test on new files
                        ↓
        Measure improvement!
```

## 💾 Files Created

- **`tools\corrections\corrections_history.db`** - SQLite database with all actions
- **`tools\corrections\recommendations.json`** - Analysis export (optional)

## 🔧 Advanced

### Export to JSON
```batch
analyze.bat --export
```
Creates `recommendations.json` for custom analysis.

### Query Database Directly
```sql
sqlite3 tools\corrections\corrections_history.db

-- Most corrected words
SELECT original_word, corrected_word, COUNT(*) 
FROM corrections 
GROUP BY original_word, corrected_word 
ORDER BY COUNT(*) DESC 
LIMIT 10;
```

### Python API
```python
from tools.corrections import (
    log_correction, 
    get_correction_statistics
)

# Log a correction
log_correction(
    file_name="x105",
    word_index=42,
    original_word="Vazquez",
    corrected_word="Vasquez",
    confidence=0.68
)

# Get stats
stats = get_correction_statistics()
print(stats['total_corrections'])
```

## 📚 Full Documentation

See `tools\corrections\README.md` for complete documentation.

## 💡 Tips

1. **Review at least 5-10 files** before analyzing (more data = better insights)
2. **Keep backups** of `corrections_history.db`
3. **Track progress** by running analysis after each batch of reviews
4. **Share insights** with your team
5. **Document patterns** you discover

## 🎯 Project Finalization Checklist

- [ ] Review 10+ sample files
- [ ] Log all corrections to database
- [ ] Run analysis and review recommendations
- [ ] Update dictionary with common terms
- [ ] Adjust confidence thresholds if needed
- [ ] Test improvements on new files
- [ ] Document final configuration
- [ ] Create standard operating procedures
- [ ] Train team on review process
- [ ] Set up regular quality audits

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Log corrections | `log_from_review.bat <file.json>` |
| Analyze data | `analyze.bat` |
| Export to JSON | `analyze.bat --export` |
| Initialize DB | `python corrections_database.py` |

**Location:** `tools\corrections\`  
**Database:** `corrections_history.db`  
**Full Docs:** `README.md`

