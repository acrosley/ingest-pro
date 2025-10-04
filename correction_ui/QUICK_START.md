# 🚀 Quick Start Guide

Get started with the Transcript Correction Tool in 3 minutes.

## Launch in 10 Seconds

**Windows:**
```
Double-click: launch.bat
```

**Mac/Linux:**
```bash
python launch.py
```

**What happens:**
1. ✅ Server starts on http://localhost:8080
2. ✅ Browser opens automatically
3. ✅ Demo data loads (if available)
4. ✅ Ready to review!

---

## First Correction in 30 Seconds

### Step 1: See the Flagged Words
Look for colored highlights in the transcript:
- 🔴 **Red** = Very low confidence (< 30%) - **FIX THESE FIRST**
- 🟡 **Yellow** = Low confidence
- 🟣 **Purple** = Names (verify spelling)
- 🟢 **Green** = Phone numbers (critical accuracy)
- 🔵 **Blue** = Numbers

### Step 2: Click a Flagged Word
- Click any highlighted word
- A popup shows:
  - Original word
  - Confidence score
  - Context (words before and after)
  - Audio plays automatically

### Step 3: Make Your Correction
- Type the correct word
- Press **Enter** or click **Apply**
- Word turns green ✅
- Move to next flagged word

### Step 4: Export When Done
- Click **"💾 Export"** button (or press **Ctrl+S**)
- Two files download:
  1. `corrected_transcript.txt` - Clean, corrected text
  2. `corrections.json` - Log of all changes

**Done! You've just corrected a transcript. 🎉**

---

## Common Tasks

### Fix Speaker Names
**Problem**: "Speaker A" and "Speaker B" aren't helpful

**Solution**:
1. **Single-click** the speaker name (e.g., "Speaker A:")
2. Type real name: "John Smith"
3. Click **"Apply to All"**
4. All instances update instantly

### Cycle Individual Speaker
**Problem**: One line is attributed to the wrong speaker

**Solution**:
1. **Double-click** the speaker name on that line
2. It cycles to the next speaker (A → B → C → A)
3. Repeat until you find the correct speaker
4. Only that line changes, not all instances

### Add/Remove Speakers
**Problem**: Need more speakers or want to clean up unused ones

**Solution**:
- Click **"➕ Add Speaker"** in the sidebar to create new speakers
- Click the **"✕"** next to a speaker to remove it
- New speakers auto-assigned next letter (A, B, C... AA, AB...)

### Find a Specific Word
**Problem**: Need to find all mentions of "phone" or a name

**Solution**:
1. Type in the Search box (sidebar)
2. All matches highlight with red outline
3. Results counter shows how many found

### Hear a Word Again
**Problem**: Not sure what was actually said

**Solution**:
1. **Double-click** any word
2. Audio jumps to that word
3. Audio plays just that word
4. Helps confirm what you heard

### Adjust What Gets Flagged
**Problem**: Too many or too few highlights

**Solution**:
- Move the **Confidence Slider**:
  - **Left** (lower) = Fewer flags, faster review
  - **Right** (higher) = More flags, thorough review
- Toggle flag types:
  - Uncheck "Show Names" to hide name flags
  - Uncheck "Show Numbers" to hide number flags

---

## Keyboard Shortcuts

| Key | Action | Use When |
|-----|--------|----------|
| **Space** | Play/Pause | Listening to audio |
| **Ctrl+S** | Export | Ready to save |
| **Enter** | Apply correction / Edit selection | In popup or text selected |
| **Esc** | Close popup | Want to cancel |
| **Single-click word** | Play from this word | Listening to audio |
| **Double-click word** | Open editor | Correcting a word |
| **Ctrl+→ / Ctrl+↓** | Next flagged word | Jumping through flags |
| **Ctrl+← / Ctrl+↑** | Previous flagged word | Going back to review |

---

## Visual Guide

### Main Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│ 📝 Transcript Correction        [💾 Export Transcript] │
├─────────────┬───────────────────────────────────────────┤
│             │  🎵 Audio Player + Waveform              │
│  Sidebar    │  ────────────────────────────────────    │
│             │  [▶] 0:28 / 1:01                         │
│  📂 Files   ├───────────────────────────────────────────┤
│  🔍 Search  │                                           │
│  ⚙️ Filters │  [00:01] John Smith: Thank you for       │
│  👥 Speaker │  calling Crosley Law Firm. This is       │
│  📊 Stats   │  Alex. How can I help you? Hi, this      │
│             │  is Arliza with Christus. I'm calling    │
│             │  regarding the client? Lynn Reichert.    │
│             │  ────        ─────────                   │
│             │  ↑ Red       ↑ Purple                    │
│             │  Low conf    Name                        │
└─────────────┴───────────────────────────────────────────┘
```

### Edit Word Popup

```
┌────────────────────────────────────┐
│  Edit Word                         │
├────────────────────────────────────┤
│  Original: "Reichert"              │
│  Confidence: 68%                   │
│  Context: "client? Lynn            │
│            [Reichert].             │
│            Richard Lynn"           │
│                                    │
│  Correction:                       │
│  ┌──────────────────────────────┐  │
│  │ Reichert                     │  │ ← Type here
│  └──────────────────────────────┘  │
│                                    │
│  [🔊 Play Audio] [📖 Dictionary]   │ ← NEW buttons
│                                    │
│  [Cancel] [Apply to All] [Apply]   │ ← Apply to All NEW
└────────────────────────────────────┘

🔊 Play Audio - Replay word with context (1 word before + 2 after)
📖 Add to Dictionary - Stop flagging this word
Apply to All - Fix all instances at once

💡 Extended playback helps you hear the word in natural speech flow!
```

### Statistics Panel

```
┌─────────────────────┐
│ 📊 Statistics       │
├─────────────────────┤
│ Total Words:    247 │
│ Flagged Words:   31 │
│ Corrections:     12 │ ← You're making progress!
│ Avg Confidence: 85% │
└─────────────────────┘
```

---

## Advanced Features

### Apply to All Instances
**Problem**: The same name is misspelled multiple times

**Solution**:
1. Double-click the first misspelled word
2. Type the correct spelling
3. Click **"Apply to All"** instead of "Apply"
4. All instances of that exact word are fixed at once!

### Add to Dictionary
**Problem**: A correctly spelled word keeps getting flagged

**Solution**:
1. Double-click the word
2. Click **"📖 Add to Dictionary"**
3. That word and similar ones won't be flagged anymore
4. Useful for company names, technical terms, etc.

### Navigate Between Flags
**Problem**: Want to review only flagged words, skip the rest

**Solution**:
1. Press **Ctrl+→** (or Ctrl+↓) to jump to next flagged word
2. Press **Ctrl+←** (or Ctrl+↑) to go back
3. Audio follows you automatically
4. Much faster than scrolling!

### Edit Selected Text
**Problem**: Want to edit multiple words or a phrase

**Solution**:
1. Click and drag to select text (can be multiple words)
2. Press **Enter**
3. Editor opens for that selection
4. Type correction and apply

---

## Workflow Tips

### For Fast Review (Speed Priority)
1. Set confidence slider to **50%** (fewer flags)
2. Only check **"Show Phone Numbers"** and **"Show Low Confidence"**
3. Skip names if not critical
4. Export when critical items are fixed

### For Thorough Review (Quality Priority)
1. Set confidence slider to **85%** (more flags)
2. Check all flag types
3. Fix speakers names first
4. Review every flagged word
5. Use search to verify consistency

### For Phone Call Transcripts
1. Fix speaker names immediately (makes reading easier)
2. Focus on phone numbers (high priority)
3. Verify company/insurance names
4. Dates and times are often important
5. Common words usually don't need correction

---

## Troubleshooting

### "Can't load my files"
- Make sure you selected **both** files:
  1. Confidence JSON file
  2. Audio file (optional but helpful)
- Click **"Load Files"** button after selecting

### "Audio won't play"
- Check audio format: WAV, MP3, or M4A
- Try playing the file in Windows Media Player first
- Some formats may not be supported by browser

### "Too many words are highlighted"
- Lower the **confidence slider** (move left)
- Uncheck some flag types you don't need
- This is normal for lower-quality recordings

### "Port 8080 already in use"
- Close other applications
- Or edit `launch.py` and change `PORT = 8080` to `PORT = 8081`

---

## What's Next?

Once you're comfortable with basic corrections:

1. **Read**: [INTEGRATION.md](INTEGRATION.md) - Connect to your pipeline
2. **Test**: [test_features.md](test_features.md) - Full feature checklist
3. **Learn**: [README.md](README.md) - Detailed documentation

---

## 💡 Pro Tips

1. **Start with speaker names** - Makes the whole transcript easier to read
2. **Trust high confidence** - Words with 95%+ confidence are usually correct
3. **Use context** - The words before/after help confirm if correction is needed
4. **Double-click to verify** - When in doubt, listen to the audio
5. **Export frequently** - Save your work every 10-15 corrections
6. **Use search for patterns** - If one name is wrong, find all instances

---

## Support

**Questions?** Check the [README.md](README.md) for detailed answers.

**Found a bug?** Document it in [test_features.md](test_features.md).

**Need help integrating?** See [INTEGRATION.md](INTEGRATION.md).

---

**Now go correct some transcripts! You've got this. 🎯**

