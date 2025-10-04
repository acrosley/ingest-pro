# Feature Test Checklist

This document helps verify all features of the Correction UI are working correctly.

## ✅ Test Procedure

### 1. Launch Test
- [ ] Run `launch.bat` (Windows) or `python launch.py` (Mac/Linux)
- [ ] Server starts without errors
- [ ] Browser opens automatically to http://localhost:8080
- [ ] UI loads with demo data (if available)

### 2. File Loading Test
- [ ] Click "Load Files" button
- [ ] Select a confidence JSON file
- [ ] Select a matching audio file
- [ ] Click "Load Files"
- [ ] Transcript renders in the editor pane
- [ ] File info appears in header

### 3. Audio Waveform Test
- [ ] Waveform displays with blue bars
- [ ] Waveform auto-fits to container width
- [ ] Click on waveform seeks to that position
- [ ] Play/pause button works
- [ ] Time counter updates (0:00 / duration)
- [ ] Waveform progress indicator moves during playback
- [ ] Current word highlights in blue during playback
- [ ] Live confidence updates during playback

### 4. Word Editing Test
- [ ] Flagged words show colored highlights:
  - Red: Critical low confidence
  - Yellow: Low confidence
  - Purple: Names
  - Green: Phone numbers
  - Blue: Numbers
- [ ] Click a flagged word opens edit modal
- [ ] Modal shows:
  - Original word
  - Confidence percentage
  - Context (words before/after)
- [ ] Audio plays the word automatically
- [ ] Type correction in input field
- [ ] Press "Apply" or Enter
- [ ] Word updates in transcript
- [ ] Word shows green "corrected" styling
- [ ] Correction count increases in stats

### 5. Speaker Editing Test
- [ ] Click a speaker name (e.g., "Speaker A:")
- [ ] Speaker edit modal opens
- [ ] Modal shows speaker tag
- [ ] Enter new name
- [ ] Click "Apply to All"
- [ ] All instances of that speaker update
- [ ] Speaker list in sidebar updates

### 6. Search Test
- [ ] Type word in search box
- [ ] Matching words highlight with red outline
- [ ] Result count shows below search box
- [ ] Clear search removes highlights
- [ ] Search is case-insensitive

### 7. Confidence Slider Test
- [ ] Move confidence threshold slider
- [ ] Threshold value updates (e.g., "70%")
- [ ] Word highlighting updates based on threshold
- [ ] More flags appear when slider is higher
- [ ] Fewer flags appear when slider is lower
- [ ] Stats update automatically

### 8. Flag Filter Test
- [ ] Uncheck "Show Low Confidence"
  - Low confidence highlights disappear
- [ ] Uncheck "Show Names"
  - Name highlights disappear
- [ ] Uncheck "Show Numbers"
  - Number highlights disappear
- [ ] Uncheck "Show Phone Numbers"
  - Phone number highlights disappear
- [ ] Uncheck "Show Dates"
  - Date highlights disappear
- [ ] Re-check filters
  - Highlights reappear
- [ ] Flagged word count updates

### 9. Export Test
- [ ] Click "Export Corrected Transcript" button (or Ctrl+S)
- [ ] File download dialog appears
- [ ] `corrected_transcript.txt` downloads
- [ ] Open file and verify:
  - Corrected words are present
  - Speaker names are updated
  - Format is clean and readable
- [ ] `corrections.json` also downloads
- [ ] Open corrections.json and verify:
  - Contains timestamp
  - Lists all corrections
  - Lists speaker name changes
  - Includes statistics

### 10. Keyboard Shortcuts Test
- [ ] Press Space bar → Audio plays/pauses
- [ ] Press Ctrl+S → Export dialog appears
- [ ] Press Esc (in modal) → Modal closes

### 11. Double-Click Word Test
- [ ] Double-click any word
- [ ] Audio seeks to that word's start time
- [ ] Audio plays
- [ ] Word is highlighted

### 12. Performance Test
- [ ] Load large transcript (100+ words)
- [ ] Scrolling is smooth
- [ ] Word editing is responsive (< 100ms)
- [ ] Audio sync has no lag
- [ ] Search is instant
- [ ] Filter updates are fast

### 13. Statistics Test
- [ ] Total Words count is accurate
- [ ] Flagged Words count is accurate
- [ ] Corrections Made increments with each edit
- [ ] Average Confidence displays as percentage
- [ ] Stats update in real-time

### 14. Error Handling Test
- [ ] Try loading invalid JSON file
  - Error message appears
- [ ] Try loading without audio
  - Transcript still loads
  - Waveform shows data visualization
- [ ] Try exporting without loading file
  - "No transcript loaded" alert appears

## 🐛 Known Issues / Bugs Found

Document any issues found during testing:

1. **Issue**: [Description]
   - **Steps to reproduce**: [Steps]
   - **Expected**: [Expected behavior]
   - **Actual**: [Actual behavior]

## ✨ Feature Requests

Document any improvements or features to add:

1. **Feature**: [Description]
   - **Use case**: [Why it would be helpful]
   - **Priority**: [High/Medium/Low]

## 📊 Test Results

**Test Date**: _______________  
**Tester**: _______________  
**Browser**: _______________  
**OS**: _______________  

**Overall Status**: [ ] Pass [ ] Fail [ ] Partial

**Pass Rate**: ___/14 major tests passed

**Notes**:

