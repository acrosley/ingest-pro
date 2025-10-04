/**
 * Transcript Correction Tool
 * Efficient UI for reviewing and correcting AI-transcribed audio
 */

class CorrectionTool {
    constructor() {
        this.confidenceData = null;
        this.audioFile = null;
        this.wordMap = new Map(); // index -> word data
        this.corrections = new Map(); // index -> corrected word
        this.speakerNames = new Map(); // tag -> name
        this.flagFilters = {
            lowConfidence: true,
            names: true,
            numbers: true,
            phones: true,
            dates: true
        };
        this.confidenceThreshold = 0.7;
        this.currentWordIndex = null;
        this.waveformData = null;
        this.playbackTimeout = null; // Track playback timeout for cleanup
        
        this.initElements();
        this.attachListeners();
        this.loadDemoData(); // Auto-load demo
    }
    
    initElements() {
        // File inputs
        this.confidenceFileInput = document.getElementById('confidenceFile');
        this.audioFileInput = document.getElementById('audioFile');
        this.loadBtn = document.getElementById('loadBtn');
        
        // Audio
        this.audioPlayer = document.getElementById('audioPlayer');
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.currentTimeEl = document.getElementById('currentTime');
        this.durationEl = document.getElementById('duration');
        this.liveConfidenceEl = document.getElementById('liveConfidence');
        this.waveformCanvas = document.getElementById('waveform');
        
        // Editor
        this.editor = document.getElementById('editor');
        
        // Controls
        this.searchInput = document.getElementById('searchInput');
        this.confidenceSlider = document.getElementById('confidenceSlider');
        this.thresholdValue = document.getElementById('thresholdValue');
        this.showLowConfidence = document.getElementById('showLowConfidence');
        this.showNames = document.getElementById('showNames');
        this.showNumbers = document.getElementById('showNumbers');
        this.showPhones = document.getElementById('showPhones');
        this.showDates = document.getElementById('showDates');
        
        // Speaker
        this.speakerList = document.getElementById('speakerList');
        
        // Stats
        this.totalWordsEl = document.getElementById('totalWords');
        this.flaggedWordsEl = document.getElementById('flaggedWords');
        this.correctionCountEl = document.getElementById('correctionCount');
        this.avgConfidenceEl = document.getElementById('avgConfidence');
        
        // Export
        this.exportBtn = document.getElementById('exportBtn');
        
        // Modals
        this.editModal = document.getElementById('editModal');
        this.speakerModal = document.getElementById('speakerModal');
        
        // Modal buttons
        this.playWordBtn = document.getElementById('playWordBtn');
        this.addToDictionaryBtn = document.getElementById('addToDictionary');
        this.applyToAllBtn = document.getElementById('applyToAll');
        
        // File info
        this.fileInfo = document.getElementById('fileInfo');
        
        // Dictionary for approved words
        this.dictionary = new Set();
        
        // Speaker overrides for individual lines (lineIndex -> speakerTag)
        this.speakerOverrides = new Map();
    }
    
    attachListeners() {
        // File loading
        this.loadBtn.addEventListener('click', () => this.loadFiles());
        
        // Audio
        this.playPauseBtn.addEventListener('click', () => this.togglePlayPause());
        this.audioPlayer.addEventListener('timeupdate', () => this.updateAudioTime());
        this.audioPlayer.addEventListener('loadedmetadata', () => this.updateDuration());
        this.waveformCanvas.addEventListener('click', (e) => this.seekAudio(e));
        
        // Search
        this.searchInput.addEventListener('input', (e) => this.searchWords(e.target.value));
        
        // Filters
        this.confidenceSlider.addEventListener('input', (e) => this.updateThreshold(e.target.value));
        this.showLowConfidence.addEventListener('change', () => this.updateFilters());
        this.showNames.addEventListener('change', () => this.updateFilters());
        this.showNumbers.addEventListener('change', () => this.updateFilters());
        this.showPhones.addEventListener('change', () => this.updateFilters());
        this.showDates.addEventListener('change', () => this.updateFilters());
        
        // Export
        this.exportBtn.addEventListener('click', () => this.exportTranscript());
        
        // Modals
        document.getElementById('cancelEdit').addEventListener('click', () => this.closeEditModal());
        document.getElementById('applyEdit').addEventListener('click', () => this.applyCorrection());
        this.applyToAllBtn.addEventListener('click', () => this.applyToAll());
        this.playWordBtn.addEventListener('click', () => this.playCurrentWord());
        this.addToDictionaryBtn.addEventListener('click', () => this.addToDictionary());
        document.getElementById('cancelSpeaker').addEventListener('click', () => this.closeSpeakerModal());
        document.getElementById('applySpeaker').addEventListener('click', () => this.applySpeakerEdit());
        
        // Speaker management
        document.getElementById('addSpeakerBtn').addEventListener('click', () => this.addSpeaker());
        
        // Close modals on background click
        this.editModal.addEventListener('click', (e) => {
            if (e.target === this.editModal) this.closeEditModal();
        });
        this.speakerModal.addEventListener('click', (e) => {
            if (e.target === this.speakerModal) this.closeSpeakerModal();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeEditModal();
                this.closeSpeakerModal();
            }
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.exportTranscript();
            }
            if (e.key === ' ' && e.target === document.body) {
                e.preventDefault();
                this.togglePlayPause();
            }
            // Enter key on selection opens editor
            if (e.key === 'Enter' && !this.editModal.classList.contains('active')) {
                const selection = window.getSelection();
                if (selection && selection.toString().trim()) {
                    this.editSelection();
                    e.preventDefault();
                }
            }
            // Arrow keys for navigation between flagged words
            if ((e.key === 'ArrowRight' || e.key === 'ArrowDown') && e.ctrlKey) {
                e.preventDefault();
                this.navigateToNextFlagged();
            }
            if ((e.key === 'ArrowLeft' || e.key === 'ArrowUp') && e.ctrlKey) {
                e.preventDefault();
                this.navigateToPreviousFlagged();
            }
        });
    }
    
    async loadDemoData() {
        try {
            // Load demo confidence data
            const response = await fetch('../demo/Transcripts/x541_2025-09-23.11-50.146.confidence.json');
            if (!response.ok) {
                console.log('Demo data not found, waiting for user to load files');
                return;
            }
            
            this.confidenceData = await response.json();
            this.processConfidenceData();
            this.renderTranscript();
            this.updateStats();
            this.createWaveform();
            
            // Try to load demo audio
            try {
                const audioResponse = await fetch('../demo/Audio/Carlos_2025-09-23_11-50_2m22s_Jessica_Progressive.wav');
                if (audioResponse.ok) {
                    const audioBlob = await audioResponse.blob();
                    const audioUrl = URL.createObjectURL(audioBlob);
                    this.audioPlayer.src = audioUrl;
                }
            } catch (err) {
                console.log('Demo audio not found');
            }
            
            this.fileInfo.textContent = '📄 Demo: Carlos_2025-09-23_11-50_2m22s_Jessica_Progressive';
            
        } catch (error) {
            console.log('Could not load demo data:', error);
        }
    }
    
    async loadFiles() {
        const confFile = this.confidenceFileInput.files[0];
        const audioFile = this.audioFileInput.files[0];
        
        if (!confFile) {
            alert('Please select a confidence JSON file');
            return;
        }
        
        try {
            // Load confidence JSON
            const confText = await this.readFileAsText(confFile);
            this.confidenceData = JSON.parse(confText);
            
            this.processConfidenceData();
            this.renderTranscript();
            this.updateStats();
            this.createWaveform();
            
            // Load audio if provided
            if (audioFile) {
                const audioUrl = URL.createObjectURL(audioFile);
                this.audioPlayer.src = audioUrl;
            }
            
            this.fileInfo.textContent = `📄 ${confFile.name}`;
            
        } catch (error) {
            alert('Error loading files: ' + error.message);
            console.error(error);
        }
    }
    
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }
    
    processConfidenceData() {
        if (!this.confidenceData || !this.confidenceData.word_data) {
            throw new Error('Invalid confidence data format');
        }
        
        this.wordMap.clear();
        this.corrections.clear();
        this.speakerNames.clear();
        
        // Build word map
        this.confidenceData.word_data.forEach((wordData, index) => {
            this.wordMap.set(index, {
                word: wordData.word,
                confidence: wordData.confidence,
                startTime: wordData.start_time,
                endTime: wordData.end_time,
                speaker: wordData.speaker_tag,
                flags: this.flagWord(wordData, index)
            });
            
            // Track speakers
            if (wordData.speaker_tag && !this.speakerNames.has(wordData.speaker_tag)) {
                this.speakerNames.set(wordData.speaker_tag, `Speaker ${wordData.speaker_tag}`);
            }
        });
        
        this.renderSpeakerList();
    }
    
    flagWord(wordData, index) {
        const flags = [];
        const word = wordData.word.trim();
        const confidence = wordData.confidence;
        
        // Low confidence
        if (confidence !== null && confidence < this.confidenceThreshold) {
            if (confidence < 0.3) {
                flags.push({ type: 'critical', priority: 'high' });
            } else {
                flags.push({ type: 'low_confidence', priority: 'medium' });
            }
        }
        
        // Phone numbers
        if (/\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b/.test(word)) {
            flags.push({ type: 'phone', priority: 'high' });
        }
        
        // Numbers
        if (/\b\d+\b/.test(word)) {
            flags.push({ type: 'number', priority: 'low' });
        }
        
        // Dates
        if (/\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b/.test(word)) {
            flags.push({ type: 'date', priority: 'medium' });
        }
        
        // Names (capitalized words)
        if (/^[A-Z][a-z]+/.test(word.replace(/[.,!?]/g, ''))) {
            const commonWords = new Set(['I', 'The', 'A', 'Hello', 'Hi', 'Yes', 'No', 'Okay']);
            if (!commonWords.has(word.replace(/[.,!?]/g, ''))) {
                flags.push({ type: 'name', priority: 'medium' });
            }
        }
        
        return flags;
    }
    
    renderTranscript() {
        if (!this.confidenceData || !this.confidenceData.transcript) {
            return;
        }
        
        this.editor.innerHTML = '';
        this.editor.contentEditable = 'true';
        
        const lines = this.confidenceData.transcript.split('\n').filter(l => l.trim());
        let globalWordIndex = 0;
        
        lines.forEach((line, lineIndex) => {
            const match = line.match(/^\[(\d{2}:\d{2})\] Speaker (\w+): (.+)$/);
            if (!match) return;
            
            const [, timestamp, speakerTag, text] = match;
            const lineDiv = document.createElement('div');
            lineDiv.className = 'transcript-line';
            
            // Timestamp
            const timeSpan = document.createElement('span');
            timeSpan.className = 'timestamp';
            timeSpan.textContent = `[${timestamp}]`;
            lineDiv.appendChild(timeSpan);
            lineDiv.appendChild(document.createTextNode(' '));
            
            // Speaker (with override support)
            const effectiveSpeakerTag = this.speakerOverrides.get(lineIndex) || speakerTag;
            const speakerSpan = document.createElement('span');
            speakerSpan.className = 'speaker';
            speakerSpan.textContent = `${this.speakerNames.get(effectiveSpeakerTag) || 'Speaker ' + effectiveSpeakerTag}:`;
            speakerSpan.dataset.speakerTag = effectiveSpeakerTag;
            speakerSpan.dataset.originalTag = speakerTag;
            speakerSpan.dataset.lineIndex = lineIndex;
            
            // Single click to edit name
            speakerSpan.addEventListener('click', (e) => {
                e.stopPropagation();
                this.editSpeaker(effectiveSpeakerTag);
            });
            
            // Double-click to cycle speaker
            speakerSpan.addEventListener('dblclick', (e) => {
                e.stopPropagation();
                e.preventDefault();
                this.cycleSpeaker(lineIndex, effectiveSpeakerTag);
            });
            
            lineDiv.appendChild(speakerSpan);
            lineDiv.appendChild(document.createTextNode(' '));
            
            // Words
            const words = text.split(/\s+/).filter(w => w.trim());
            words.forEach((word) => {
                const wordData = this.wordMap.get(globalWordIndex);
                if (wordData) {
                    const wordSpan = this.createWordElement(word, globalWordIndex, wordData);
                    lineDiv.appendChild(wordSpan);
                    lineDiv.appendChild(document.createTextNode(' '));
                }
                globalWordIndex++;
            });
            
            this.editor.appendChild(lineDiv);
        });
    }
    
    createWordElement(word, index, wordData) {
        const span = document.createElement('span');
        span.className = 'word';
        span.textContent = word;
        span.dataset.index = index;
        span.dataset.confidence = `${Math.round(wordData.confidence * 100)}%`;
        span.dataset.startTime = wordData.startTime;
        span.dataset.endTime = wordData.endTime;
        
        // Apply flags
        if (wordData.flags.length > 0) {
            const highestPriority = wordData.flags[0];
            if (highestPriority.type === 'critical') {
                span.classList.add('flagged-critical');
            } else if (highestPriority.type === 'phone') {
                span.classList.add('flagged-phone');
            } else if (highestPriority.type === 'name') {
                span.classList.add('flagged-name');
            } else if (highestPriority.type === 'number') {
                span.classList.add('flagged-number');
            } else {
                span.classList.add('flagged');
            }
        }
        
        // Check if corrected
        if (this.corrections.has(index)) {
            span.classList.add('corrected');
            span.textContent = this.corrections.get(index);
        }
        
        // Single click to play audio from this point
        span.addEventListener('click', (e) => {
            e.stopPropagation();
            if (wordData.startTime !== null) {
                this.audioPlayer.currentTime = wordData.startTime;
                this.audioPlayer.play();
            }
        });
        
        // Double-click to edit
        span.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            e.preventDefault();
            this.editWord(index, wordData);
        });
        
        return span;
    }
    
    editWord(index, wordData) {
        this.currentWordIndex = index;
        this.currentWordData = wordData; // Store for button access
        
        document.getElementById('originalWord').textContent = wordData.word;
        document.getElementById('wordConfidence').textContent = `${Math.round(wordData.confidence * 100)}%`;
        
        // Build context
        const contextBefore = [];
        const contextAfter = [];
        for (let i = Math.max(0, index - 3); i < index; i++) {
            const w = this.wordMap.get(i);
            if (w) contextBefore.push(w.word);
        }
        for (let i = index + 1; i < Math.min(this.wordMap.size, index + 4); i++) {
            const w = this.wordMap.get(i);
            if (w) contextAfter.push(w.word);
        }
        
        document.getElementById('wordContext').textContent = 
            `${contextBefore.join(' ')} [${wordData.word}] ${contextAfter.join(' ')}`;
        
        const correctionInput = document.getElementById('correctionInput');
        correctionInput.value = this.corrections.get(index) || wordData.word;
        
        // Add Enter key handler for quick apply
        correctionInput.onkeydown = (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.applyCorrection();
            }
        };
        
        this.editModal.classList.add('active');
        setTimeout(() => {
            correctionInput.focus();
            correctionInput.select();
        }, 100);
        
        // Auto-play word audio once with extended context (1 word before, 2 words after)
        this.playWordWithContext(index);
    }
    
    playWordWithContext(index) {
        const wordData = this.wordMap.get(index);
        
        if (!wordData || wordData.startTime === null || wordData.endTime === null) {
            console.warn('Cannot play word: missing timing data');
            return;
        }
        
        try {
            // Find 1 word before (with fallback)
            let startTime = wordData.startTime;
            const beforeIndex = index - 1;
            if (beforeIndex >= 0) {
                const beforeWord = this.wordMap.get(beforeIndex);
                if (beforeWord && beforeWord.startTime !== null) {
                    startTime = beforeWord.startTime;
                }
            }
            
            // Find 2 words after (with fallback)
            let endTime = wordData.endTime;
            const afterIndex = index + 2;
            if (afterIndex < this.wordMap.size) {
                const afterWord = this.wordMap.get(afterIndex);
                if (afterWord && afterWord.endTime !== null) {
                    endTime = afterWord.endTime;
                }
            }
            
            // Validate times
            if (startTime >= endTime) {
                console.warn('Invalid playback range, using word boundaries only');
                startTime = wordData.startTime;
                endTime = wordData.endTime;
            }
            
            // Play audio
            this.audioPlayer.currentTime = startTime;
            this.audioPlayer.play().catch(err => {
                console.error('Audio playback failed:', err);
            });
            
            // Schedule pause
            const duration = (endTime - startTime) * 1000;
            if (this.playbackTimeout) {
                clearTimeout(this.playbackTimeout);
            }
            this.playbackTimeout = setTimeout(() => {
                if (!this.audioPlayer.paused) {
                    this.audioPlayer.pause();
                }
            }, duration);
            
        } catch (error) {
            console.error('Error during word playback:', error);
        }
    }
    
    closeEditModal() {
        this.editModal.classList.remove('active');
        this.currentWordIndex = null;
        
        // Clean up any pending playback
        if (this.playbackTimeout) {
            clearTimeout(this.playbackTimeout);
            this.playbackTimeout = null;
        }
    }
    
    applyCorrection() {
        if (this.currentWordIndex === null) return;
        
        const newValue = document.getElementById('correctionInput').value.trim();
        if (!newValue) return;
        
        this.corrections.set(this.currentWordIndex, newValue);
        this.closeEditModal();
        this.renderTranscript(); // Re-render to show correction
        this.updateStats();
        this.saveCorrections();
    }
    
    applyToAll() {
        if (this.currentWordIndex === null) return;
        
        const originalWord = this.wordMap.get(this.currentWordIndex)?.word;
        const newValue = document.getElementById('correctionInput').value.trim();
        
        if (!newValue || !originalWord) return;
        
        // Find all instances of the original word and apply correction
        let appliedCount = 0;
        this.wordMap.forEach((wordData, index) => {
            if (wordData.word === originalWord) {
                this.corrections.set(index, newValue);
                appliedCount++;
            }
        });
        
        this.closeEditModal();
        this.renderTranscript();
        this.updateStats();
        this.saveCorrections();
        
        alert(`Applied correction to ${appliedCount} instance(s) of "${originalWord}"`);
    }
    
    playCurrentWord() {
        if (this.currentWordIndex === null) {
            console.warn('No word selected for playback');
            return;
        }
        
        // Use the same robust playback method
        this.playWordWithContext(this.currentWordIndex);
    }
    
    addToDictionary() {
        if (this.currentWordIndex === null) return;
        
        const wordData = this.wordMap.get(this.currentWordIndex);
        if (!wordData) return;
        
        const originalWord = wordData.word.toLowerCase().replace(/[.,!?;:]/g, '');
        this.dictionary.add(originalWord);
        
        // Remove flags from this word and similar words
        this.wordMap.forEach((data, index) => {
            const word = data.word.toLowerCase().replace(/[.,!?;:]/g, '');
            if (word === originalWord) {
                data.flags = [];
            }
        });
        
        this.closeEditModal();
        this.renderTranscript();
        this.updateStats();
        
        alert(`"${wordData.word}" added to dictionary. Similar words won't be flagged.`);
    }
    
    editSelection() {
        const selection = window.getSelection();
        if (!selection || !selection.toString().trim()) return;
        
        const range = selection.getRangeAt(0);
        const container = range.commonAncestorContainer;
        
        // Find the word element(s) in the selection
        let wordElement = container.nodeType === Node.ELEMENT_NODE ? container : container.parentElement;
        
        // Find closest word span
        while (wordElement && !wordElement.classList.contains('word')) {
            wordElement = wordElement.parentElement;
        }
        
        if (wordElement && wordElement.dataset.index) {
            const index = parseInt(wordElement.dataset.index);
            const wordData = this.wordMap.get(index);
            if (wordData) {
                this.editWord(index, wordData);
            }
        }
    }
    
    navigateToNextFlagged() {
        const flaggedWords = Array.from(document.querySelectorAll('.word.flagged, .word.flagged-critical, .word.flagged-name, .word.flagged-phone, .word.flagged-number'));
        
        if (flaggedWords.length === 0) return;
        
        // Find current position
        const currentIndex = flaggedWords.findIndex(word => word.classList.contains('current'));
        const nextIndex = currentIndex < flaggedWords.length - 1 ? currentIndex + 1 : 0;
        
        const nextWord = flaggedWords[nextIndex];
        const index = parseInt(nextWord.dataset.index);
        const wordData = this.wordMap.get(index);
        
        if (wordData && wordData.startTime !== null) {
            this.audioPlayer.currentTime = wordData.startTime;
            nextWord.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Highlight current word
            flaggedWords.forEach(w => w.classList.remove('current'));
            nextWord.classList.add('current');
        }
    }
    
    navigateToPreviousFlagged() {
        const flaggedWords = Array.from(document.querySelectorAll('.word.flagged, .word.flagged-critical, .word.flagged-name, .word.flagged-phone, .word.flagged-number'));
        
        if (flaggedWords.length === 0) return;
        
        // Find current position
        const currentIndex = flaggedWords.findIndex(word => word.classList.contains('current'));
        const prevIndex = currentIndex > 0 ? currentIndex - 1 : flaggedWords.length - 1;
        
        const prevWord = flaggedWords[prevIndex];
        const index = parseInt(prevWord.dataset.index);
        const wordData = this.wordMap.get(index);
        
        if (wordData && wordData.startTime !== null) {
            this.audioPlayer.currentTime = wordData.startTime;
            prevWord.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Highlight current word
            flaggedWords.forEach(w => w.classList.remove('current'));
            prevWord.classList.add('current');
        }
    }
    
    editSpeaker(speakerTag) {
        document.getElementById('speakerTag').textContent = speakerTag;
        document.getElementById('speakerNameInput').value = this.speakerNames.get(speakerTag) || '';
        document.getElementById('speakerNameInput').dataset.tag = speakerTag;
        this.speakerModal.classList.add('active');
        setTimeout(() => document.getElementById('speakerNameInput').focus(), 100);
    }
    
    closeSpeakerModal() {
        this.speakerModal.classList.remove('active');
    }
    
    applySpeakerEdit() {
        const input = document.getElementById('speakerNameInput');
        const tag = input.dataset.tag;
        const newName = input.value.trim();
        
        if (newName) {
            this.speakerNames.set(tag, newName);
            this.renderTranscript();
            this.renderSpeakerList();
            this.saveCorrections();
        }
        
        this.closeSpeakerModal();
    }
    
    renderSpeakerList() {
        this.speakerList.innerHTML = '';
        
        // Sort speakers by tag
        const sortedSpeakers = Array.from(this.speakerNames.entries()).sort((a, b) => {
            return a[0].localeCompare(b[0]);
        });
        
        sortedSpeakers.forEach(([tag, name]) => {
            const item = document.createElement('div');
            item.className = 'speaker-item';
            
            const tagSpan = document.createElement('span');
            tagSpan.className = 'speaker-tag';
            tagSpan.textContent = tag;
            tagSpan.addEventListener('click', () => this.editSpeaker(tag));
            
            const nameSpan = document.createElement('span');
            nameSpan.className = 'speaker-name';
            nameSpan.textContent = name;
            nameSpan.addEventListener('click', () => this.editSpeaker(tag));
            
            const removeBtn = document.createElement('button');
            removeBtn.className = 'speaker-remove';
            removeBtn.textContent = '✕';
            removeBtn.title = 'Remove speaker';
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.removeSpeaker(tag);
            });
            
            item.appendChild(tagSpan);
            item.appendChild(nameSpan);
            item.appendChild(removeBtn);
            this.speakerList.appendChild(item);
        });
    }
    
    addSpeaker() {
        // Generate next speaker tag
        const existingTags = Array.from(this.speakerNames.keys());
        let nextTag = 'A';
        
        // Find the next available letter
        for (let i = 0; i < 26; i++) {
            const tag = String.fromCharCode(65 + i); // A-Z
            if (!existingTags.includes(tag)) {
                nextTag = tag;
                break;
            }
        }
        
        // If all letters used, start with AA, AB, etc.
        if (existingTags.includes(nextTag)) {
            nextTag = 'A' + String.fromCharCode(65 + existingTags.length);
        }
        
        // Add new speaker
        this.speakerNames.set(nextTag, `Speaker ${nextTag}`);
        this.renderSpeakerList();
        
        // Immediately open editor for the new speaker
        this.editSpeaker(nextTag);
    }
    
    removeSpeaker(tag) {
        const speakerName = this.speakerNames.get(tag);
        
        if (!confirm(`Remove speaker "${speakerName}" (${tag})?\n\nThis will not delete any transcript lines, but you won't be able to assign this speaker anymore.`)) {
            return;
        }
        
        // Remove from speaker names
        this.speakerNames.delete(tag);
        
        // Remove any overrides using this tag
        this.speakerOverrides.forEach((overrideTag, lineIndex) => {
            if (overrideTag === tag) {
                this.speakerOverrides.delete(lineIndex);
            }
        });
        
        this.renderSpeakerList();
        this.renderTranscript();
        this.saveCorrections();
    }
    
    cycleSpeaker(lineIndex, currentTag) {
        // Get all available speakers
        const speakerTags = Array.from(this.speakerNames.keys()).sort();
        
        if (speakerTags.length < 2) {
            alert('Add more speakers to cycle between them');
            return;
        }
        
        // Find current index
        const currentIndex = speakerTags.indexOf(currentTag);
        
        // Get next speaker (cycle back to start if at end)
        const nextIndex = (currentIndex + 1) % speakerTags.length;
        const nextTag = speakerTags[nextIndex];
        
        // Store override
        this.speakerOverrides.set(lineIndex, nextTag);
        
        // Re-render to show change
        this.renderTranscript();
        this.saveCorrections();
    }
    
    updateThreshold(value) {
        this.confidenceThreshold = value / 100;
        this.thresholdValue.textContent = `${value}%`;
        this.processConfidenceData();
        this.renderTranscript();
        this.updateStats();
    }
    
    updateFilters() {
        this.flagFilters.lowConfidence = this.showLowConfidence.checked;
        this.flagFilters.names = this.showNames.checked;
        this.flagFilters.numbers = this.showNumbers.checked;
        this.flagFilters.phones = this.showPhones.checked;
        this.flagFilters.dates = this.showDates.checked;
        
        // Update visibility based on filters
        document.querySelectorAll('.word').forEach(span => {
            const index = parseInt(span.dataset.index);
            const wordData = this.wordMap.get(index);
            
            if (!wordData || !wordData.flags || wordData.flags.length === 0) {
                return;
            }
            
            let shouldShow = false;
            wordData.flags.forEach(flag => {
                if (flag.type === 'low_confidence' && this.flagFilters.lowConfidence) shouldShow = true;
                if (flag.type === 'critical' && this.flagFilters.lowConfidence) shouldShow = true;
                if (flag.type === 'name' && this.flagFilters.names) shouldShow = true;
                if (flag.type === 'number' && this.flagFilters.numbers) shouldShow = true;
                if (flag.type === 'phone' && this.flagFilters.phones) shouldShow = true;
                if (flag.type === 'date' && this.flagFilters.dates) shouldShow = true;
            });
            
            // Remove all flag classes first
            span.classList.remove('flagged', 'flagged-critical', 'flagged-name', 'flagged-phone', 'flagged-number');
            
            // Re-apply if should show
            if (shouldShow) {
                const highestPriority = wordData.flags[0];
                if (highestPriority.type === 'critical') {
                    span.classList.add('flagged-critical');
                } else if (highestPriority.type === 'phone') {
                    span.classList.add('flagged-phone');
                } else if (highestPriority.type === 'name') {
                    span.classList.add('flagged-name');
                } else if (highestPriority.type === 'number') {
                    span.classList.add('flagged-number');
                } else {
                    span.classList.add('flagged');
                }
            }
        });
        
        this.updateStats();
    }
    
    searchWords(query) {
        if (!query.trim()) {
            // Clear search highlights
            document.querySelectorAll('.word').forEach(span => {
                span.style.outline = '';
            });
            document.getElementById('searchResults').textContent = '';
            return;
        }
        
        const lowerQuery = query.toLowerCase();
        let matchCount = 0;
        
        document.querySelectorAll('.word').forEach(span => {
            const text = span.textContent.toLowerCase();
            if (text.includes(lowerQuery)) {
                span.style.outline = '2px solid #e74c3c';
                matchCount++;
            } else {
                span.style.outline = '';
            }
        });
        
        document.getElementById('searchResults').textContent = 
            matchCount > 0 ? `Found ${matchCount} matches` : 'No matches found';
    }
    
    togglePlayPause() {
        if (this.audioPlayer.paused) {
            this.audioPlayer.play();
            this.playPauseBtn.textContent = '⏸️';
        } else {
            this.audioPlayer.pause();
            this.playPauseBtn.textContent = '▶️';
        }
    }
    
    updateAudioTime() {
        const currentTime = this.audioPlayer.currentTime;
        this.currentTimeEl.textContent = this.formatTime(currentTime);
        
        // Update waveform progress
        this.drawWaveformProgress();
        
        // Highlight current word
        this.highlightCurrentWord(currentTime);
        
        // Update live confidence
        const wordData = Array.from(this.wordMap.values()).find(
            w => currentTime >= w.startTime && currentTime <= w.endTime
        );
        if (wordData) {
            this.liveConfidenceEl.textContent = `Confidence: ${Math.round(wordData.confidence * 100)}%`;
        }
    }
    
    updateDuration() {
        this.durationEl.textContent = this.formatTime(this.audioPlayer.duration);
        this.createWaveform();
    }
    
    highlightCurrentWord(time) {
        document.querySelectorAll('.word.current').forEach(w => w.classList.remove('current'));
        
        const wordSpan = Array.from(document.querySelectorAll('.word')).find(span => {
            const start = parseFloat(span.dataset.startTime);
            const end = parseFloat(span.dataset.endTime);
            return time >= start && time <= end;
        });
        
        if (wordSpan) {
            wordSpan.classList.add('current');
            wordSpan.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    createWaveform() {
        const canvas = this.waveformCanvas;
        const ctx = canvas.getContext('2d');
        
        // Set canvas size
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);
        
        // Clear
        ctx.fillStyle = '#1a252f';
        ctx.fillRect(0, 0, rect.width, rect.height);
        
        if (this.wordMap.size === 0) return;
        
        // Generate waveform from word data
        const maxTime = Math.max(...Array.from(this.wordMap.values()).map(w => w.endTime || 0));
        const waveformPoints = [];
        const numBars = Math.floor(rect.width / 3);
        
        for (let i = 0; i < numBars; i++) {
            const timeStart = (i / numBars) * maxTime;
            const timeEnd = ((i + 1) / numBars) * maxTime;
            
            const wordsInRange = Array.from(this.wordMap.values()).filter(
                w => w.startTime < timeEnd && w.endTime > timeStart
            );
            
            let amplitude = 0;
            if (wordsInRange.length > 0) {
                const avgConf = wordsInRange.reduce((sum, w) => sum + (w.confidence || 0), 0) / wordsInRange.length;
                amplitude = avgConf * 0.8 + Math.min(wordsInRange.length / 3, 0.2);
            }
            
            waveformPoints.push(amplitude);
        }
        
        this.waveformData = { points: waveformPoints, maxTime, width: rect.width, height: rect.height };
        
        // Draw waveform
        this.drawWaveform(ctx, waveformPoints, rect.width, rect.height);
    }
    
    drawWaveform(ctx, points, width, height) {
        const centerY = height / 2;
        const maxBarHeight = (height - 10) / 2;
        const barWidth = width / points.length;
        
        ctx.fillStyle = '#3498db';
        
        points.forEach((amplitude, i) => {
            const x = i * barWidth;
            const barHeight = Math.max(2, amplitude * maxBarHeight);
            ctx.fillRect(x, centerY - barHeight, barWidth * 0.8, barHeight * 2);
        });
    }
    
    drawWaveformProgress() {
        if (!this.waveformData) return;
        
        const canvas = this.waveformCanvas;
        const ctx = canvas.getContext('2d');
        const { points, maxTime, width, height } = this.waveformData;
        
        // Redraw base waveform
        ctx.fillStyle = '#1a252f';
        ctx.fillRect(0, 0, width, height);
        this.drawWaveform(ctx, points, width, height);
        
        // Draw progress
        const progress = this.audioPlayer.currentTime / maxTime;
        const progressX = progress * width;
        
        ctx.fillStyle = 'rgba(52, 152, 219, 0.3)';
        ctx.fillRect(0, 0, progressX, height);
        
        // Draw playhead
        ctx.strokeStyle = '#3498db';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(progressX, 0);
        ctx.lineTo(progressX, height);
        ctx.stroke();
    }
    
    seekAudio(event) {
        if (!this.waveformData) return;
        
        const canvas = this.waveformCanvas;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const progress = x / rect.width;
        
        this.audioPlayer.currentTime = progress * this.waveformData.maxTime;
    }
    
    updateStats() {
        const totalWords = this.wordMap.size;
        const flaggedWords = Array.from(this.wordMap.values()).filter(
            w => w.flags && w.flags.length > 0
        ).length;
        const correctionCount = this.corrections.size;
        
        const confidences = Array.from(this.wordMap.values())
            .map(w => w.confidence)
            .filter(c => c !== null);
        const avgConfidence = confidences.length > 0
            ? Math.round((confidences.reduce((a, b) => a + b, 0) / confidences.length) * 100)
            : 0;
        
        this.totalWordsEl.textContent = totalWords;
        this.flaggedWordsEl.textContent = flaggedWords;
        this.correctionCountEl.textContent = correctionCount;
        this.avgConfidenceEl.textContent = `${avgConfidence}%`;
    }
    
    exportTranscript() {
        if (!this.confidenceData) {
            alert('No transcript loaded');
            return;
        }
        
        // Rebuild transcript from corrected data
        let output = '';
        const lines = this.confidenceData.transcript.split('\n').filter(l => l.trim());
        let globalWordIndex = 0;
        
        lines.forEach((line, lineIndex) => {
            const match = line.match(/^\[(\d{2}:\d{2})\] Speaker (\w+): (.+)$/);
            if (!match) return;
            
            const [, timestamp, speakerTag, text] = match;
            
            // Use override speaker if exists
            const effectiveSpeakerTag = this.speakerOverrides.get(lineIndex) || speakerTag;
            const speakerName = this.speakerNames.get(effectiveSpeakerTag) || `Speaker ${effectiveSpeakerTag}`;
            
            const words = text.split(/\s+/).filter(w => w.trim());
            const correctedWords = words.map((word) => {
                const corrected = this.corrections.get(globalWordIndex);
                globalWordIndex++;
                return corrected || word;
            });
            
            output += `[${timestamp}] ${speakerName}: ${correctedWords.join(' ')}\n`;
        });
        
        // Download
        const blob = new Blob([output], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'corrected_transcript.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // Also save corrections JSON
        this.saveCorrections();
        
        alert('Transcript exported successfully!');
    }
    
    saveCorrections() {
        const data = {
            timestamp: new Date().toISOString(),
            corrections: Object.fromEntries(this.corrections),
            speakerNames: Object.fromEntries(this.speakerNames),
            speakerOverrides: Object.fromEntries(this.speakerOverrides),
            stats: {
                totalWords: this.wordMap.size,
                correctionCount: this.corrections.size,
                speakerOverrideCount: this.speakerOverrides.size
            }
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'corrections.json';
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('Corrections saved:', data);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.correctionTool = new CorrectionTool();
});

