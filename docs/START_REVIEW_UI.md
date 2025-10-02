# Start Review UI

## Quick Start

```powershell
# Navigate to project directory
cd "C:\Users\Andrew.CLF\OneDrive - Crosley Law Firm\Desktop\ingest_pro"

# Start the review UI server
python tools/review_tools/launch_review_ui.py
```

Then open in your browser:
- http://localhost:8000/review_ui.html

## What You'll See

### New Features (Just Added)

The UI now shows:

1. **Overall Confidence Score** 
   - 🟢 Green (85%+) = Excellent quality
   - 🟡 Yellow (70-85%) = Fair quality, review recommended
   - 🔴 Red (<70%) = Poor quality, manual review required

2. **Confidence Source**
   - Shows which engine provided the confidence
   - `google_cloud_stt` = Fast, accurate confidence from Google Cloud
   - `whisper` = Fallback alignment confidence

3. **Enhanced Stats**
   - Total words
   - Flagged words
   - Flag rate
   - High priority flags
   - Overall confidence with color coding
   - Corrections made

### How to Use

1. **Click "Load Review File"**
   - Browse to: `output\Review\test copy.review.json`
   - Or any other `.review.json` file

2. **Review Flagged Words**
   - Words are listed with context
   - Color-coded by priority
   - Shows confidence scores
   - Click to make corrections

3. **Filter by Priority or Type**
   - Use dropdown filters
   - Focus on high-priority items first

4. **Export Corrected Transcript**
   - Click "Export Corrected Transcript" when done
   - Download the corrected version

### Your Test File

For `test copy.review.json`:
- **Overall Confidence**: 40% (🔴 Poor)
- **Confidence Source**: google_cloud_stt
- **Total Words**: 80
- **Flagged Words**: 54 (67.5%)

The low confidence suggests the audio quality may be poor or the transcription had issues. Review the flagged words carefully!

## Troubleshooting

### Port Already in Use

If you see "Address already in use":

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with the number shown)
taskkill /PID <PID> /F

# Try starting again
python tools/review_tools/launch_review_ui.py
```

### UI Not Loading

1. Make sure the server is running (check the PowerShell window)
2. Try refreshing the browser (Ctrl+R)
3. Try a different browser
4. Check the URL is exactly: http://localhost:8000/review_ui.html

### Error Loading Review File

Make sure:
- The file is a `.review.json` file
- The file is from the `output/Review/` directory
- The file was generated after the recent updates

## Tips

1. **Start with High Priority**: Use the priority filter to focus on critical issues first
2. **Check Confidence**: Low confidence words (<70%) need manual verification
3. **Listen to Audio**: For uncertain words, listen to the audio file
4. **Save Frequently**: Export your corrections periodically

Enjoy the enhanced review system! 🎉

