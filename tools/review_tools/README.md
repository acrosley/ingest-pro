# Call Transcript Review System - Quick Start

## 🎯 What is This?

A production-ready system for reviewing and correcting call transcripts with intelligent flagging of high-value information.

## 🚀 Quick Start (3 Steps)

### 1. Generate a Review File
Your pipeline automatically creates `.review.json` files when processing calls.
They're saved to: `output/Review/`

### 2. Launch the Review UI
**Windows:**
```batch
cd tools\review_tools
launch_review.bat
```

**Mac/Linux:**
```bash
python tools/review_tools/launch_review_ui.py
```

### 3. Review & Export
1. Click "📁 Load Review File"
2. Select a `.review.json` file
3. Review flagged words
4. Make corrections
5. Export corrected transcript

## 📋 What Gets Flagged?

### High Priority (Red)
- 📞 **Phone Numbers** - Critical for callbacks
- 📋 **Case Numbers** - Essential for tracking
- 🔤 **Spelled Words** - Names like "H-O-U-A-I-S"
- ⚠️ **Mismatches** - Gemini vs Whisper disagree

### Medium Priority (Yellow)
- 👤 **Proper Nouns** - Names and companies
- 💰 **Money Amounts** - Settlements, fees
- 📅 **Dates** - Appointments, deadlines
- 🕐 **Times** - Scheduling

### Low Priority (Blue)
- ℹ️ **Alignment Issues** - Minor concerns

## 💡 Key Features

- **Smart Pattern Recognition**: Flags information that actually matters
- **Differential Analysis**: Shows both Gemini and Whisper versions
- **Context Display**: See 3 words before/after each flagged word
- **One-Click Corrections**: Click Whisper's suggestion to apply it
- **Export**: Download clean corrected transcript

## 📊 Performance

- **Before**: 92% of words flagged (frustrating!)
- **After**: 15-25% of words flagged (focused!)
- **Review Time**: 2-5 minutes per call (vs 15-20 minutes)

## 🔧 Files in This Directory

- `review_generator.py` - Core review logic with pattern recognition
- `corrections_db.py` - Database for tracking corrections
- `review_ui.html` - Web interface for reviewing
- `launch_review_ui.py` - Python server to launch UI
- `launch_review.bat` - Windows shortcut to launch UI

## 📚 Full Documentation

See `docs/COMMERCIAL_REVIEW_SYSTEM.md` for complete documentation.

## 🆘 Troubleshooting

**UI won't open?**
- Check that port 8000 is available
- Try: `python launch_review_ui.py --port 9000`

**No words flagged?**
- Check `config/call_pipeline.ini` - Review.Enabled should be `true`
- Verify the audio file exists

**Too many flags?**
- Focus on High Priority first
- Use the filter dropdowns
- Common terms will be learned over time

## 💾 Where Data is Stored

- **Review Files**: `output/Review/*.review.json`
- **Corrections Database**: `tools/review_tools/corrections.db`
- **Corrected Transcripts**: Downloaded as `*_corrected.txt`

## 🎓 Tips for Best Results

1. **Start with High Priority**: Focus on phone numbers and case numbers first
2. **Use Whisper Suggestions**: When available, they're usually accurate
3. **Add to Vocabulary**: Common names get added to the database automatically
4. **Export Regularly**: Download corrected transcripts to Word/PDF as needed

---

**Need Help?** Check the full documentation in `docs/COMMERCIAL_REVIEW_SYSTEM.md`




