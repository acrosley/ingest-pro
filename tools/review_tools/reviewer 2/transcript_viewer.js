class TranscriptViewer {
    constructor() {
        this.confidenceData = null;
        this.audioFile = null;
        this.wordMap = new Map();
        this.audioContext = null;
        this.analyser = null;
        this.animationId = null;
        this.speakerNames = new Map(); // Map speaker tags to names
        this.correctedWords = new Map(); // Store word corrections
        this.speakerChanges = new Map(); // Store speaker corrections
        this.greenHighlightEnabled = true; // Toggle for green highlighting
        this.waveformData = null;
        this.audioBuffer = null;
        this.isHoveringWaveform = false;
        this.hoverPosition = 0;
        
        this.initializeElements();
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.confidenceFileInput = document.getElementById('confidenceFile');
        this.audioFileInput = document.getElementById('audioFile');
        this.loadFilesBtn = document.getElementById('loadFiles');
        this.audioPlayer = document.getElementById('audioPlayer');
        this.transcriptContent = document.getElementById('transcriptContent');
        this.confidenceThreshold = document.getElementById('confidenceThreshold');
        this.thresholdValue = document.getElementById('thresholdValue');
        this.exportBtn = document.getElementById('exportTranscript');
        this.fileInputs = document.getElementById('fileInputs');
        this.toggleGreenHighlightBtn = document.getElementById('toggleGreenHighlight');
        this.editSpeakerNamesBtn = document.getElementById('editSpeakerNames');
        this.saveChangesBtn = document.getElementById('saveChanges');
        
        // Status elements
        this.totalWordsEl = document.getElementById('totalWords');
        this.lowConfidenceWordsEl = document.getElementById('lowConfidenceWords');
        this.currentWordEl = document.getElementById('currentWord');
        this.confidenceScore = document.getElementById('confidenceScore');
        this.waveformCanvas = document.getElementById('waveformCanvas');
    }
    
    setupEventListeners() {
        this.loadFilesBtn.addEventListener('click', () => this.showFileInputs());
        this.confidenceFileInput.addEventListener('change', () => this.handleFileLoad());
        this.audioFileInput.addEventListener('change', () => this.handleFileLoad());
        
        this.confidenceThreshold.addEventListener('input', (e) => {
            this.thresholdValue.textContent = Math.round(e.target.value * 100) + '%';
            this.updateWordHighlighting();
        });
        
        this.exportBtn.addEventListener('click', () => this.exportTranscript());
        this.toggleGreenHighlightBtn.addEventListener('click', () => this.toggleGreenHighlight());
        this.editSpeakerNamesBtn.addEventListener('click', () => this.showSpeakerEditor());
        this.saveChangesBtn.addEventListener('click', () => this.saveAllChanges());
        
        // Audio events
        this.audioPlayer.addEventListener('timeupdate', () => this.updateAudioTime());
        this.audioPlayer.addEventListener('loadedmetadata', () => this.updateAudioDuration());
        this.audioPlayer.addEventListener('play', () => this.startVisualization());
        this.audioPlayer.addEventListener('pause', () => this.stopVisualization());
        this.audioPlayer.addEventListener('ended', () => this.stopVisualization());
        
        // Canvas click for seeking
        this.waveformCanvas.addEventListener('click', (e) => this.seekToPosition(e));
        
        // Canvas hover for time preview
        this.waveformCanvas.addEventListener('mousemove', (e) => this.showTimePreview(e));
        this.waveformCanvas.addEventListener('mouseleave', () => this.hideTimePreview());
        
        // Handle window resize for responsive waveform
        window.addEventListener('resize', () => {
            if (this.resizeTimeout) clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                if (this.waveformData) {
                    this.createWaveform();
                }
            }, 250);
        });
        
        // Show loading state initially
        this.showWaveformLoading();
        
        // Load demo data on startup
        this.loadDemoData();
    }
    
    showFileInputs() {
        this.fileInputs.style.display = 'flex';
        this.loadFilesBtn.textContent = 'Files Selected';
        this.loadFilesBtn.disabled = true;
    }
    
    async loadDemoData() {
        try {
            // Use the full confidence data from the provided file
            const confidenceData = {
                "transcript": "[00:00] Speaker A: Yes, sir.\n[00:01] Speaker B: Hi, Carlos. I have Progressive on the phone, the adjuster for the case of Anissa Roy Hampton regarding negotiations.\n[00:09] Speaker A: Oh, that would be nice.\n[00:10] Speaker B: Okay, let me drop her.\n[00:16] Speaker A: Hello. Hi, this is Carlos.\n[00:19] Speaker B: Hi, Carlos. This is Jessica with Progressive. How are you?\n[00:22] Speaker A: Hi, Jessica. How are you? Good, good.\n[00:24] Speaker B: Hi, I'm good. I was reaching out to follow up on Anissa Hampton.\n[00:28] Speaker A: Uh-huh. Was what the new. There is a new offer or a new proposal?\n[00:34] Speaker B: No, I haven't heard from you guys. Oh, last I spoke with y'all, y'all were going to reach out to the client that y'all haven't spoken with her since I extended my offer. So I was calling to follow up.\n[00:43] Speaker A: I thought that the. The attorney was talking to you already, but let me check pretty quick. Okay? Hold on. Hold on. Let me check pretty quick right here. Usually the attorney who negotiate with you, but. I was thinking maybe she already talked to you. Let me hold on. Hello, sir. Hold on a second. Yeah, the last office was for 56,530, correct? That's the last one, I guess, I have here.\n[01:52] Speaker B: Give me just a second, hold on.\n[01:55] Speaker A: Am I sure?\n[02:12] Speaker B: Yeah, it looks like that was the first offer extended.\n[02:15] Speaker A: Okay, hold on.\n[02:16] Speaker B: I haven't gotten anything from you guys yet.\n[02:17] Speaker A: Yeah, I understand. Hold on a second, Jessica. Hold on, hold on.",
                "overall_confidence": 0.85689646,
                "word_data": [
                    {"word": "Yes,", "confidence": 0.28042424, "start_time": 0.64, "end_time": 0.96, "speaker_tag": "A"},
                    {"word": "sir.", "confidence": 0.41281936, "start_time": 1.04, "end_time": 1.28, "speaker_tag": "A"},
                    {"word": "Hi,", "confidence": 0.83599085, "start_time": 1.6, "end_time": 1.68, "speaker_tag": "B"},
                    {"word": "Carlos.", "confidence": 0.75797355, "start_time": 1.92, "end_time": 2.4, "speaker_tag": "B"},
                    {"word": "I", "confidence": 0.99817514, "start_time": 2.56, "end_time": 2.64, "speaker_tag": "B"},
                    {"word": "have", "confidence": 0.99652255, "start_time": 2.72, "end_time": 2.8, "speaker_tag": "B"},
                    {"word": "Progressive", "confidence": 0.9281673, "start_time": 2.96, "end_time": 3.68, "speaker_tag": "B"},
                    {"word": "on", "confidence": 0.99623823, "start_time": 3.76, "end_time": 3.84, "speaker_tag": "B"},
                    {"word": "the", "confidence": 0.9972102, "start_time": 3.84, "end_time": 3.92, "speaker_tag": "B"},
                    {"word": "phone,", "confidence": 0.62287825, "start_time": 4.0, "end_time": 4.24, "speaker_tag": "B"},
                    {"word": "the", "confidence": 0.97015417, "start_time": 4.4, "end_time": 4.48, "speaker_tag": "B"},
                    {"word": "adjuster", "confidence": 0.9626147, "start_time": 4.48, "end_time": 5.12, "speaker_tag": "B"},
                    {"word": "for", "confidence": 0.94744885, "start_time": 5.2, "end_time": 5.28, "speaker_tag": "B"},
                    {"word": "the", "confidence": 0.98917246, "start_time": 5.52, "end_time": 5.6, "speaker_tag": "B"},
                    {"word": "case", "confidence": 0.99279094, "start_time": 5.68, "end_time": 5.76, "speaker_tag": "B"},
                    {"word": "of", "confidence": 0.9943889, "start_time": 5.92, "end_time": 6.0, "speaker_tag": "B"},
                    {"word": "Anissa", "confidence": 0.5390008, "start_time": 6.08, "end_time": 6.72, "speaker_tag": "B"},
                    {"word": "Roy", "confidence": 0.95802337, "start_time": 6.72, "end_time": 7.04, "speaker_tag": "B"},
                    {"word": "Hampton", "confidence": 0.8973384, "start_time": 7.04, "end_time": 7.52, "speaker_tag": "B"},
                    {"word": "regarding", "confidence": 0.774557, "start_time": 7.68, "end_time": 7.92, "speaker_tag": "B"},
                    {"word": "negotiations.", "confidence": 0.712541, "start_time": 8.16, "end_time": 8.72, "speaker_tag": "B"},
                    {"word": "Oh,", "confidence": 0.5287351, "start_time": 9.04, "end_time": 9.12, "speaker_tag": "A"},
                    {"word": "that", "confidence": 0.9797223, "start_time": 9.6, "end_time": 9.68, "speaker_tag": "A"},
                    {"word": "would", "confidence": 0.9931585, "start_time": 9.76, "end_time": 9.84, "speaker_tag": "A"},
                    {"word": "be", "confidence": 0.998211, "start_time": 9.92, "end_time": 10.0, "speaker_tag": "A"},
                    {"word": "nice.", "confidence": 0.9904693, "start_time": 10.08, "end_time": 10.4, "speaker_tag": "A"},
                    {"word": "Okay,", "confidence": 0.5205239, "start_time": 10.96, "end_time": 11.28, "speaker_tag": "B"},
                    {"word": "let", "confidence": 0.9836625, "start_time": 11.44, "end_time": 11.52, "speaker_tag": "B"},
                    {"word": "me", "confidence": 0.9937995, "start_time": 11.6, "end_time": 11.76, "speaker_tag": "B"},
                    {"word": "drop", "confidence": 0.17118393, "start_time": 11.76, "end_time": 12.08, "speaker_tag": "B"},
                    {"word": "her.", "confidence": 0.48563534, "start_time": 12.24, "end_time": 12.32, "speaker_tag": "B"},
                    {"word": "Hello.", "confidence": 0.50460744, "start_time": 16.48, "end_time": 16.96, "speaker_tag": "A"},
                    {"word": "Hi,", "confidence": 0.80476016, "start_time": 17.12, "end_time": 17.2, "speaker_tag": "A"},
                    {"word": "this", "confidence": 0.99278957, "start_time": 17.36, "end_time": 17.44, "speaker_tag": "A"},
                    {"word": "is", "confidence": 0.9976826, "start_time": 17.6, "end_time": 17.68, "speaker_tag": "A"},
                    {"word": "Carlos.", "confidence": 0.9874265, "start_time": 17.76, "end_time": 18.32, "speaker_tag": "A"},
                    {"word": "Hi,", "confidence": 0.9132618, "start_time": 19.6, "end_time": 19.68, "speaker_tag": "B"},
                    {"word": "Carlos.", "confidence": 0.8311021, "start_time": 20.0, "end_time": 20.48, "speaker_tag": "B"},
                    {"word": "This", "confidence": 0.9942046, "start_time": 20.56, "end_time": 20.64, "speaker_tag": "B"},
                    {"word": "is", "confidence": 0.994531, "start_time": 20.64, "end_time": 20.72, "speaker_tag": "B"},
                    {"word": "Jessica", "confidence": 0.9828157, "start_time": 20.72, "end_time": 21.2, "speaker_tag": "B"},
                    {"word": "with", "confidence": 0.97171515, "start_time": 21.2, "end_time": 21.28, "speaker_tag": "B"},
                    {"word": "Progressive.", "confidence": 0.912935, "start_time": 21.28, "end_time": 21.92, "speaker_tag": "B"},
                    {"word": "How", "confidence": 0.9919483, "start_time": 22.0, "end_time": 22.16, "speaker_tag": "B"},
                    {"word": "are", "confidence": 0.9973283, "start_time": 22.16, "end_time": 22.24, "speaker_tag": "B"},
                    {"word": "you?", "confidence": 0.9913304, "start_time": 22.24, "end_time": 22.32, "speaker_tag": "B"},
                    {"word": "Hi,", "confidence": 0.93527544, "start_time": 22.4, "end_time": 22.48, "speaker_tag": "A"},
                    {"word": "Jessica.", "confidence": 0.843932, "start_time": 22.56, "end_time": 23.04, "speaker_tag": "A"},
                    {"word": "How", "confidence": 0.99378335, "start_time": 23.12, "end_time": 23.28, "speaker_tag": "A"},
                    {"word": "are", "confidence": 0.9984427, "start_time": 23.28, "end_time": 23.36, "speaker_tag": "A"},
                    {"word": "you?", "confidence": 0.9919589, "start_time": 23.36, "end_time": 23.44, "speaker_tag": "A"},
                    {"word": "Good,", "confidence": 0.6674165, "start_time": 23.68, "end_time": 23.92, "speaker_tag": "A"},
                    {"word": "good.", "confidence": 0.98903054, "start_time": 24.08, "end_time": 24.16, "speaker_tag": "A"},
                    {"word": "Hi,", "confidence": 0.8658087, "start_time": 24.48, "end_time": 24.56, "speaker_tag": "B"},
                    {"word": "I'm", "confidence": 0.90594643, "start_time": 24.72, "end_time": 25.12, "speaker_tag": "B"},
                    {"word": "good.", "confidence": 0.99546325, "start_time": 25.2, "end_time": 25.28, "speaker_tag": "B"},
                    {"word": "I", "confidence": 0.99614644, "start_time": 25.52, "end_time": 25.6, "speaker_tag": "B"},
                    {"word": "was", "confidence": 0.99734855, "start_time": 25.68, "end_time": 25.76, "speaker_tag": "B"},
                    {"word": "reaching", "confidence": 0.98186696, "start_time": 25.84, "end_time": 26.16, "speaker_tag": "B"},
                    {"word": "out", "confidence": 0.99734575, "start_time": 26.16, "end_time": 26.24, "speaker_tag": "B"},
                    {"word": "to", "confidence": 0.99613106, "start_time": 26.24, "end_time": 26.32, "speaker_tag": "B"},
                    {"word": "follow", "confidence": 0.99482477, "start_time": 26.4, "end_time": 26.48, "speaker_tag": "B"},
                    {"word": "up", "confidence": 0.75335073, "start_time": 26.64, "end_time": 26.72, "speaker_tag": "B"},
                    {"word": "on", "confidence": 0.9931498, "start_time": 26.8, "end_time": 26.88, "speaker_tag": "B"},
                    {"word": "Anissa", "confidence": 0.9238936, "start_time": 26.88, "end_time": 27.44, "speaker_tag": "B"},
                    {"word": "Hampton.", "confidence": 0.8625894, "start_time": 27.44, "end_time": 27.84, "speaker_tag": "B"},
                    {"word": "Uh-huh.", "confidence": 0.06350587, "start_time": 28.21, "end_time": 28.77, "speaker_tag": "A"},
                    {"word": "Was", "confidence": 0.46628898, "start_time": 29.01, "end_time": 29.41, "speaker_tag": "A"},
                    {"word": "what", "confidence": 0.6143482, "start_time": 29.49, "end_time": 29.57, "speaker_tag": "A"},
                    {"word": "the", "confidence": 0.83121544, "start_time": 29.73, "end_time": 29.81, "speaker_tag": "A"},
                    {"word": "new.", "confidence": 0.57092124, "start_time": 29.89, "end_time": 29.97, "speaker_tag": "A"},
                    {"word": "There", "confidence": 0.8115967, "start_time": 30.85, "end_time": 30.93, "speaker_tag": "A"},
                    {"word": "is", "confidence": 0.93920636, "start_time": 31.09, "end_time": 31.17, "speaker_tag": "A"},
                    {"word": "a", "confidence": 0.99275714, "start_time": 31.25, "end_time": 31.33, "speaker_tag": "A"},
                    {"word": "new", "confidence": 0.9983413, "start_time": 31.41, "end_time": 31.49, "speaker_tag": "A"},
                    {"word": "offer", "confidence": 0.98410946, "start_time": 31.57, "end_time": 31.89, "speaker_tag": "A"},
                    {"word": "or", "confidence": 0.5687803, "start_time": 31.97, "end_time": 32.05, "speaker_tag": "A"},
                    {"word": "a", "confidence": 0.51622087, "start_time": 32.05, "end_time": 32.13, "speaker_tag": "A"},
                    {"word": "new", "confidence": 0.99324954, "start_time": 32.21, "end_time": 32.29, "speaker_tag": "A"},
                    {"word": "proposal?", "confidence": 0.32232508, "start_time": 32.37, "end_time": 32.45, "speaker_tag": "A"}
                ]
            };
            
            this.confidenceData = confidenceData;
            this.initializeSpeakerNames();
            this.buildWordMap();
            this.renderTranscript();
            this.updateStats();
            this.createWaveform();
            
            // Try to load the audio file if it exists
            this.loadAudioFile('x541_2025-09-23.11-50.146.wav');
            
            console.log('Demo data loaded successfully!');
            
        } catch (error) {
            console.error('Error loading demo data:', error);
        }
    }
    
    async handleFileLoad() {
        const confidenceFile = this.confidenceFileInput.files[0];
        const audioFile = this.audioFileInput.files[0];
        
        if (confidenceFile) {
            try {
                const text = await this.readFileAsText(confidenceFile);
                this.confidenceData = JSON.parse(text);
                this.initializeSpeakerNames();
                this.buildWordMap();
                this.renderTranscript();
                this.updateStats();
                this.createWaveform();
            } catch (error) {
                console.error('Error loading confidence file:', error);
                alert('Error loading confidence file. Please check file format.');
            }
        }
        
        if (audioFile) {
            this.audioFile = URL.createObjectURL(audioFile);
            this.audioPlayer.src = this.audioFile;
            console.log('Audio file loaded:', this.audioFile);
        }
    }
    
    async loadAudioFile(filename) {
        try {
            const response = await fetch(filename);
            if (response.ok) {
                const audioBlob = await response.blob();
                this.audioFile = URL.createObjectURL(audioBlob);
                this.audioPlayer.src = this.audioFile;
                console.log('Audio file loaded successfully:', filename);
            } else {
                console.log('Audio file not found:', filename);
            }
        } catch (error) {
            console.log('Could not load audio file:', filename, error);
        }
    }
    
    initializeSpeakerNames() {
        if (!this.confidenceData || !this.confidenceData.word_data) return;
        
        // Extract unique speaker tags
        const speakerTags = new Set();
        this.confidenceData.word_data.forEach(wordData => {
            speakerTags.add(wordData.speaker_tag);
        });
        
        // Initialize default names
        speakerTags.forEach(tag => {
            if (!this.speakerNames.has(tag)) {
                this.speakerNames.set(tag, `Speaker ${tag}`);
            }
        });
    }
    
    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }
    
    buildWordMap() {
        if (!this.confidenceData || !this.confidenceData.word_data) return;
        
        this.wordMap.clear();
        this.confidenceData.word_data.forEach((wordData, index) => {
            this.wordMap.set(index, {
                word: wordData.word,
                confidence: wordData.confidence,
                startTime: wordData.start_time,
                endTime: wordData.end_time,
                speakerTag: wordData.speaker_tag
            });
        });
    }
    
    parseTranscript() {
        if (!this.confidenceData || !this.confidenceData.transcript) return [];
        
        const lines = this.confidenceData.transcript.trim().split('\n');
        const parsedLines = lines.map((line, index) => {
            const match = line.match(/^\[(\d{2}:\d{2})\] Speaker (\w+): (.+)$/);
            if (match) {
                return {
                    timestamp: match[1],
                    speaker: match[2],
                    text: match[3]
                };
            }
            return null;
        }).filter(line => line !== null);
        
        return parsedLines;
    }
    
    renderTranscript() {
        if (!this.confidenceData) return;
        
        this.transcriptContent.innerHTML = '';
        
        const transcriptLines = this.parseTranscript();
        this.renderLineView(transcriptLines);
    }
    
    renderLineView(transcriptLines) {
        const transcriptContainer = document.createElement('div');
        transcriptContainer.className = 'transcript-container';
        
        let globalWordIndex = 0;
        
        transcriptLines.forEach((line, lineIndex) => {
            const lineDiv = document.createElement('div');
            lineDiv.className = 'transcript-line';
            
            // Add timestamp and speaker
            const timestampSpan = document.createElement('span');
            timestampSpan.className = 'timestamp';
            timestampSpan.textContent = `[${line.timestamp}]`;
            
            const speakerSpan = document.createElement('span');
            speakerSpan.className = 'speaker editable-speaker';
            speakerSpan.textContent = `${this.speakerNames.get(line.speaker) || `Speaker ${line.speaker}`}:`;
            speakerSpan.dataset.speakerTag = line.speaker;
            speakerSpan.addEventListener('click', (e) => this.editSpeakerName(e));
            
            lineDiv.appendChild(timestampSpan);
            lineDiv.appendChild(speakerSpan);
            lineDiv.appendChild(document.createTextNode(' '));
            
            // Split text into words and create word elements
            const words = line.text.split(/\s+/).filter(word => word.trim());
            
            words.forEach((word, wordIndexInLine) => {
                const wordSpan = this.createWordElement(word.trim(), globalWordIndex);
                lineDiv.appendChild(wordSpan);
                lineDiv.appendChild(document.createTextNode(' '));
                globalWordIndex++;
            });
            
            transcriptContainer.appendChild(lineDiv);
        });
        
        this.transcriptContent.appendChild(transcriptContainer);
    }
    
    toggleGreenHighlight() {
        this.greenHighlightEnabled = !this.greenHighlightEnabled;
        this.updateWordHighlighting();
        this.toggleGreenHighlightBtn.textContent = this.greenHighlightEnabled ? 
            'Toggle Green Highlight' : 'Enable Green Highlight';
    }
    
    createWordElement(word, index) {
        const wordSpan = document.createElement('span');
        wordSpan.className = 'word';
        wordSpan.textContent = word;
        wordSpan.dataset.wordIndex = index;
        
        // Get confidence data for this word
        const wordData = this.wordMap.get(index);
        if (wordData) {
            const confidence = wordData.confidence;
            wordSpan.dataset.confidence = confidence;
            wordSpan.dataset.startTime = wordData.startTime;
            wordSpan.dataset.endTime = wordData.endTime;
            
            // Add confidence class
            if (confidence < 0.5) {
                wordSpan.classList.add('low-confidence');
            } else if (confidence < 0.8) {
                wordSpan.classList.add('medium-confidence');
            } else {
                wordSpan.classList.add('high-confidence');
            }
            
            // Create tooltip
            const tooltip = document.createElement('div');
            tooltip.className = 'word-tooltip';
            tooltip.textContent = `Confidence: ${Math.round(confidence * 100)}%`;
            wordSpan.appendChild(tooltip);
        } else {
            wordSpan.classList.add('high-confidence');
        }
        
        // Add click event for audio sync
        wordSpan.addEventListener('click', (e) => this.syncAudioToWord(e));
        
        // Add right-click or double-click for word editing
        wordSpan.addEventListener('dblclick', (e) => this.editWord(e));
        wordSpan.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.editWord(e);
        });
        
        return wordSpan;
    }
    
    syncAudioToWord(event) {
        const wordElement = event.currentTarget;
        const startTime = parseFloat(wordElement.dataset.startTime);
        
        if (startTime !== undefined && this.audioPlayer.src) {
            this.audioPlayer.currentTime = startTime;
            this.audioPlayer.play();
            
            // Highlight the current word
            this.highlightCurrentWord(wordElement);
        }
    }
    
    highlightCurrentWord(wordElement) {
        // Remove previous highlighting
        document.querySelectorAll('.word.current').forEach(w => w.classList.remove('current'));
        
        // Add highlighting to current word
        wordElement.classList.add('current');
        
        // Scroll to word if needed
        wordElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    async createWaveform() {
        const canvas = this.waveformCanvas;
        const ctx = canvas.getContext('2d');
        
        // Set high DPI for crisp rendering
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);
        canvas.style.width = rect.width + 'px';
        canvas.style.height = rect.height + 'px';
        
        // Clear canvas with dark background
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(0, 0, rect.width, rect.height);
        
        if (this.wordMap.size === 0) return;
        
        // Calculate total duration
        const maxTime = Math.max(...Array.from(this.wordMap.values()).map(w => w.endTime));
        const totalDuration = maxTime;
        
        // Generate high-resolution waveform data
        const waveformPoints = this.generateWaveformData(totalDuration, rect.width);
        
        // Draw the waveform with smooth rendering
        this.drawProductionWaveform(ctx, waveformPoints, rect.width, rect.height);
        
        // Add time markers
        this.drawTimeMarkers(ctx, canvas, totalDuration, rect.width, rect.height);
        
        // Store waveform data for interactions
        this.waveformData = {
            totalDuration: totalDuration,
            canvasWidth: rect.width,
            canvasHeight: rect.height,
            waveformPoints: waveformPoints
        };
    }
    
    generateWaveformData(duration, width) {
        // Create high-resolution waveform data points
        const points = [];
        const samplesPerPixel = Math.ceil(duration / width * 50); // 50 samples per pixel for smoothness
        
        for (let x = 0; x < width; x++) {
            const time = (x / width) * duration;
            const timeEnd = ((x + 1) / width) * duration;
            
            // Collect all words in this time range
            const wordsInRange = [];
            this.wordMap.forEach((wordData) => {
                if (wordData.startTime < timeEnd && wordData.endTime > time) {
                    wordsInRange.push(wordData);
                }
            });
            
            // Calculate amplitude based on confidence and word density
            let amplitude = 0;
            if (wordsInRange.length > 0) {
                const avgConfidence = wordsInRange.reduce((sum, w) => sum + w.confidence, 0) / wordsInRange.length;
                const density = Math.min(wordsInRange.length / 3, 1); // Normalize density
                amplitude = avgConfidence * 0.7 + density * 0.3; // Weighted combination
            }
            
            points.push(amplitude);
        }
        
        // Apply smoothing for professional appearance
        return this.smoothWaveform(points);
    }
    
    smoothWaveform(points) {
        // Apply Gaussian smoothing for smooth transitions
        const smoothed = [];
        const kernel = [0.06, 0.24, 0.4, 0.24, 0.06]; // Gaussian kernel
        const halfKernel = Math.floor(kernel.length / 2);
        
        for (let i = 0; i < points.length; i++) {
            let sum = 0;
            let weight = 0;
            
            for (let j = 0; j < kernel.length; j++) {
                const idx = i - halfKernel + j;
                if (idx >= 0 && idx < points.length) {
                    sum += points[idx] * kernel[j];
                    weight += kernel[j];
                }
            }
            
            smoothed.push(sum / weight);
        }
        
        return smoothed;
    }
    
    drawProductionWaveform(ctx, waveformPoints, width, height) {
        const centerY = height / 2;
        const maxBarHeight = (height - 30) / 2; // Leave space for time markers
        
        // Draw waveform with gradient and smooth curves
        ctx.save();
        
        // Create gradient for bars
        const gradient = ctx.createLinearGradient(0, centerY - maxBarHeight, 0, centerY + maxBarHeight);
        gradient.addColorStop(0, '#60a5fa'); // Lighter blue at top
        gradient.addColorStop(0.5, '#3b82f6'); // Main blue
        gradient.addColorStop(1, '#2563eb'); // Darker blue at bottom
        
        ctx.fillStyle = gradient;
        
        // Draw bars with smooth rendering
        const barWidth = Math.max(1, width / waveformPoints.length);
        
        for (let i = 0; i < waveformPoints.length; i++) {
            const x = i * barWidth;
            const amplitude = waveformPoints[i];
            const barHeight = Math.max(2, amplitude * maxBarHeight);
            
            // Draw symmetric bars
            ctx.fillRect(x, centerY - barHeight, barWidth * 0.8, barHeight * 2);
        }
        
        // Add subtle glow effect
        ctx.shadowColor = '#3b82f6';
        ctx.shadowBlur = 2;
        ctx.fillStyle = 'rgba(59, 130, 246, 0.3)';
        
        for (let i = 0; i < waveformPoints.length; i++) {
            const x = i * barWidth;
            const amplitude = waveformPoints[i];
            const barHeight = Math.max(2, amplitude * maxBarHeight);
            ctx.fillRect(x, centerY - barHeight, barWidth * 0.8, barHeight * 2);
        }
        
        ctx.restore();
    }
    
    drawTimeMarkers(ctx, canvas, totalDuration, width, height) {
        const markerInterval = Math.ceil(totalDuration / 8); // 8 markers max for cleaner look
        
        ctx.save();
        ctx.fillStyle = '#94a3b8'; // Light gray for dark background
        ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.textAlign = 'center';
        
        // Draw time markers
        for (let i = 0; i <= totalDuration; i += markerInterval) {
            if (i === 0) continue; // Skip 0, we'll draw it separately
            
            const x = (i / totalDuration) * width;
            
            // Draw vertical line
            ctx.strokeStyle = 'rgba(71, 85, 105, 0.5)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(x, height - 22);
            ctx.lineTo(x, height - 10);
            ctx.stroke();
            
            // Draw time label
            ctx.fillStyle = '#94a3b8';
            ctx.fillText(this.formatTime(i), x, height - 2);
        }
        
        // Add start and end labels with emphasis
        ctx.fillStyle = '#cbd5e1';
        ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText('0:00', 5, height - 2);
        
        ctx.textAlign = 'right';
        ctx.fillText(this.formatTime(totalDuration), width - 5, height - 2);
        
        ctx.restore();
    }
    
    updateWaveformProgress() {
        if (!this.waveformData || !this.audioPlayer.duration) return;
        
        // Redraw the waveform
        this.createWaveform();
        
        const canvas = this.waveformCanvas;
        const ctx = canvas.getContext('2d');
        const rect = canvas.getBoundingClientRect();
        
        // Calculate progress
        const progress = this.audioPlayer.currentTime / this.audioPlayer.duration;
        const progressX = progress * rect.width;
        
        ctx.save();
        
        // Draw progress overlay with fade effect
        const progressGradient = ctx.createLinearGradient(0, 0, progressX, 0);
        progressGradient.addColorStop(0, 'rgba(59, 130, 246, 0.15)');
        progressGradient.addColorStop(0.9, 'rgba(59, 130, 246, 0.25)');
        progressGradient.addColorStop(1, 'rgba(59, 130, 246, 0.35)');
        
        ctx.fillStyle = progressGradient;
        ctx.fillRect(0, 0, progressX, rect.height - 20);
        
        // Draw playhead line with glow
        ctx.shadowColor = '#60a5fa';
        ctx.shadowBlur = 8;
        ctx.strokeStyle = '#60a5fa';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(progressX, 0);
        ctx.lineTo(progressX, rect.height - 20);
        ctx.stroke();
        
        // Draw playhead handle at top
        ctx.shadowBlur = 6;
        ctx.fillStyle = '#60a5fa';
        ctx.beginPath();
        ctx.arc(progressX, 8, 5, 0, 2 * Math.PI);
        ctx.fill();
        
        // Add white center for handle
        ctx.shadowBlur = 0;
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(progressX, 8, 3, 0, 2 * Math.PI);
        ctx.fill();
        
        // Draw current time label
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.textAlign = progressX > rect.width - 50 ? 'right' : 'left';
        const timeText = this.formatTime(this.audioPlayer.currentTime);
        const textX = progressX > rect.width - 50 ? progressX - 10 : progressX + 10;
        
        // Draw background for time label
        const metrics = ctx.measureText(timeText);
        ctx.fillStyle = 'rgba(30, 41, 59, 0.9)';
        ctx.fillRect(textX - 4, 18, metrics.width + 8, 16);
        
        ctx.fillStyle = '#60a5fa';
        ctx.fillText(timeText, textX, 28);
        
        ctx.restore();
    }
    
    seekToPosition(event) {
        if (!this.waveformData || !this.audioPlayer.duration) return;
        
        const canvas = this.waveformCanvas;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        
        // Use rect.width (not canvas.width) to account for high-DPI scaling
        const progress = Math.max(0, Math.min(1, x / rect.width));
        
        // Seek to the clicked position
        this.audioPlayer.currentTime = progress * this.audioPlayer.duration;
        
        // Add visual feedback
        this.showSeekFeedback(x, progress * this.audioPlayer.duration);
    }
    
    showSeekFeedback(x, time) {
        const canvas = this.waveformCanvas;
        const ctx = canvas.getContext('2d');
        
        // Draw a temporary highlight at the click position
        ctx.fillStyle = 'rgba(59, 130, 246, 0.3)';
        ctx.fillRect(x - 10, 0, 20, canvas.height);
        
        // Clear the highlight after a short delay
        setTimeout(() => {
            this.updateWaveformProgress();
        }, 200);
    }
    
    showTimePreview(event) {
        if (!this.waveformData || !this.audioPlayer.duration) return;
        
        const canvas = this.waveformCanvas;
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const progress = Math.max(0, Math.min(1, x / rect.width));
        const time = progress * this.audioPlayer.duration;
        
        this.isHoveringWaveform = true;
        this.hoverPosition = x;
        
        // Draw hover indicator on canvas
        this.drawHoverIndicator(x, rect.width, rect.height);
        
        // Create tooltip if it doesn't exist
        if (!this.timeTooltip) {
            this.timeTooltip = document.createElement('div');
            this.timeTooltip.className = 'time-tooltip';
            this.timeTooltip.style.cssText = `
                position: fixed;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                pointer-events: none;
                z-index: 1000;
                opacity: 0;
                transition: opacity 0.15s ease;
                border: 1px solid #475569;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            `;
            document.body.appendChild(this.timeTooltip);
        }
        
        // Update tooltip content and position
        this.timeTooltip.textContent = this.formatTime(time);
        this.timeTooltip.style.left = event.clientX - this.timeTooltip.offsetWidth / 2 + 'px';
        this.timeTooltip.style.top = event.clientY - 35 + 'px';
        this.timeTooltip.style.opacity = '1';
    }
    
    drawHoverIndicator(x, width, height) {
        if (!this.waveformData) return;
        
        const canvas = this.waveformCanvas;
        const ctx = canvas.getContext('2d');
        
        // Redraw progress first (if audio is playing)
        if (this.audioPlayer && !this.audioPlayer.paused) {
            this.updateWaveformProgress();
        } else {
            this.createWaveform();
        }
        
        ctx.save();
        
        // Draw hover line
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.6)';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height - 20);
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Draw small circle at hover position
        ctx.fillStyle = 'rgba(148, 163, 184, 0.8)';
        ctx.beginPath();
        ctx.arc(x, height / 2, 3, 0, 2 * Math.PI);
        ctx.fill();
        
        ctx.restore();
    }
    
    hideTimePreview() {
        this.isHoveringWaveform = false;
        
        if (this.timeTooltip) {
            this.timeTooltip.style.opacity = '0';
        }
        
        // Redraw waveform without hover indicator
        if (this.audioPlayer && !this.audioPlayer.paused) {
            this.updateWaveformProgress();
        } else if (this.waveformData) {
            this.createWaveform();
        }
    }
    
    updateWordHighlighting() {
        const threshold = parseFloat(this.confidenceThreshold.value);
        const wordElements = document.querySelectorAll('.word');
        
        wordElements.forEach(wordElement => {
            const confidence = parseFloat(wordElement.dataset.confidence);
            
            // Remove existing confidence classes
            wordElement.classList.remove('low-confidence', 'medium-confidence', 'high-confidence');
            
            // Add appropriate class based on threshold and green highlight setting
            if (confidence < threshold) {
                wordElement.classList.add('low-confidence');
            } else if (confidence < 0.8) {
                wordElement.classList.add('medium-confidence');
            } else if (this.greenHighlightEnabled) {
                wordElement.classList.add('high-confidence');
            }
            // If green highlight is disabled, high confidence words get no special styling
        });
    }
    
    updateAudioTime() {
        const currentTime = this.audioPlayer.currentTime;
        const duration = this.audioPlayer.duration;
        
        if (!isNaN(currentTime) && !isNaN(duration)) {
            document.getElementById('currentTime').textContent = this.formatTime(currentTime);
            
            // Update confidence score for current time
            this.updateCurrentConfidenceScore(currentTime);
            
            // Highlight current word
            this.highlightCurrentWordAtTime(currentTime);
            
            // Update waveform progress
            this.updateWaveformProgress();
        }
    }
    
    updateAudioDuration() {
        const duration = this.audioPlayer.duration;
        if (!isNaN(duration)) {
            document.getElementById('duration').textContent = this.formatTime(duration);
        }
    }
    
    updateCurrentConfidenceScore(currentTime) {
        // Find words around current time
        const wordsAtTime = Array.from(this.wordMap.values()).filter(wordData => 
            currentTime >= wordData.startTime && currentTime <= wordData.endTime
        );
        
        if (wordsAtTime.length > 0) {
            const avgConfidence = wordsAtTime.reduce((sum, word) => sum + word.confidence, 0) / wordsAtTime.length;
            this.confidenceScore.textContent = `Confidence: ${Math.round(avgConfidence * 100)}%`;
        }
    }
    
    highlightCurrentWordAtTime(currentTime) {
        // Find the word at current time
        for (let [index, wordData] of this.wordMap.entries()) {
            if (currentTime >= wordData.startTime && currentTime <= wordData.endTime) {
                const wordElement = document.querySelector(`[data-word-index="${index}"]`);
                if (wordElement) {
                    this.highlightCurrentWord(wordElement);
                    this.currentWordEl.textContent = `Current: "${wordData.word}"`;
                }
                break;
            }
        }
    }
    
    updateStats() {
        const totalWords = this.wordMap.size;
        const lowConfidenceCount = Array.from(this.wordMap.values()).filter(word => 
            word.confidence < parseFloat(this.confidenceThreshold.value)
        ).length;
        
        this.totalWordsEl.textContent = `Words: ${totalWords}`;
        this.lowConfidenceWordsEl.textContent = `Low Confidence: ${lowConfidenceCount}`;
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    
    editWord(event) {
        const wordElement = event.currentTarget;
        const wordIndex = parseInt(wordElement.dataset.wordIndex);
        const originalWord = wordElement.textContent;
        const confidence = parseFloat(wordElement.dataset.confidence);
        
        this.showWordEditModal(wordIndex, originalWord, confidence, wordElement);
    }
    
    showWordEditModal(wordIndex, originalWord, confidence, wordElement) {
        // Create modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Edit Word</h3>
                <p>Original: "${originalWord}" (${Math.round(confidence * 100)}% confidence)</p>
                <input type="text" id="editedWord" value="${originalWord}" />
                <div class="modal-buttons">
                    <button class="btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button class="btn-primary" onclick="window.transcriptViewer.applyWordEdit(${wordIndex}, this)">Apply</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Focus input
        setTimeout(() => {
            const input = modal.querySelector('#editedWord');
            input.focus();
            input.select();
        }, 100);
    }
    
    applyWordEdit(wordIndex, button) {
        const modal = button.closest('.modal');
        const editedText = modal.querySelector('#editedWord').value.trim();
        
        if (editedText) {
            this.correctedWords.set(wordIndex, editedText);
            
            // Update word element
            const wordElement = document.querySelector(`[data-word-index="${wordIndex}"]`);
            if (wordElement) {
                wordElement.textContent = editedText;
                wordElement.classList.add('corrected');
            }
            
            this.updateStats();
        }
        
        modal.remove();
    }
    
    editSpeakerName(event) {
        const speakerElement = event.currentTarget;
        const speakerTag = speakerElement.dataset.speakerTag;
        const currentName = this.speakerNames.get(speakerTag);
        
        this.showSpeakerEditModal(speakerTag, currentName, speakerElement);
    }
    
    showSpeakerEditModal(speakerTag, currentName, speakerElement) {
        // Create modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Edit Speaker Name</h3>
                <p>Speaker Tag: ${speakerTag}</p>
                <input type="text" id="editedSpeakerName" value="${currentName}" placeholder="Enter speaker name" />
                <div class="modal-buttons">
                    <button class="btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button class="btn-primary" onclick="window.transcriptViewer.applySpeakerEdit('${speakerTag}', this)">Apply</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Focus input
        setTimeout(() => {
            const input = modal.querySelector('#editedSpeakerName');
            input.focus();
            input.select();
        }, 100);
    }
    
    applySpeakerEdit(speakerTag, button) {
        const modal = button.closest('.modal');
        const editedName = modal.querySelector('#editedSpeakerName').value.trim();
        
        if (editedName) {
            this.speakerNames.set(speakerTag, editedName);
            
            // Update all speaker elements with this tag
            const speakerElements = document.querySelectorAll(`[data-speaker-tag="${speakerTag}"]`);
            speakerElements.forEach(element => {
                if (element.classList.contains('speaker')) {
                    element.textContent = `${editedName}:`;
                } else if (element.classList.contains('speaker-change')) {
                    const timestamp = element.innerHTML.match(/\[([^\]]+)\]/);
                    if (timestamp) {
                        element.innerHTML = `<strong>${editedName} [${timestamp[1]}]:</strong>`;
                    }
                }
            });
        }
        
        modal.remove();
    }
    
    showSpeakerEditor() {
        // Create modal to edit all speakers at once
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        
        let speakerInputs = '';
        this.speakerNames.forEach((name, tag) => {
            speakerInputs += `
                <div class="speaker-input-group">
                    <label>Speaker ${tag}:</label>
                    <input type="text" id="speaker_${tag}" value="${name}" />
                </div>
            `;
        });
        
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Edit All Speaker Names</h3>
                ${speakerInputs}
                <div class="modal-buttons">
                    <button class="btn-secondary" onclick="this.closest('.modal').remove()">Cancel</button>
                    <button class="btn-primary" onclick="window.transcriptViewer.applyAllSpeakerEdits(this)">Apply All</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    applyAllSpeakerEdits(button) {
        const modal = button.closest('.modal');
        
        this.speakerNames.forEach((name, tag) => {
            const input = modal.querySelector(`#speaker_${tag}`);
            if (input && input.value.trim()) {
                this.speakerNames.set(tag, input.value.trim());
            }
        });
        
        // Re-render transcript with new names
        this.renderTranscript();
        modal.remove();
    }
    
    saveAllChanges() {
        const changes = {
            speakerNames: Object.fromEntries(this.speakerNames),
            correctedWords: Object.fromEntries(this.correctedWords),
            timestamp: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(changes, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'transcript_changes.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        alert('Changes saved to transcript_changes.json');
    }
    
    exportTranscript() {
        if (!this.confidenceData) {
            alert('No transcript loaded');
            return;
        }
        
        let exportText = '';
        const transcriptLines = this.parseTranscript();
        
        transcriptLines.forEach((line, lineIndex) => {
            const speakerName = this.speakerNames.get(line.speaker) || `Speaker ${line.speaker}`;
            exportText += `[${line.timestamp}] ${speakerName}: `;
            
            // Apply word corrections
            const words = line.text.split(/\s+/).filter(word => word.trim());
            let wordIndex = 0;
            
            const correctedWords = words.map(word => {
                if (word.trim()) {
                    const corrected = this.correctedWords.get(wordIndex);
                    wordIndex++;
                    return corrected || word;
                }
                return word;
            });
            
            exportText += correctedWords.join(' ') + '\n';
        });
        
        // Download file
        const blob = new Blob([exportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'reviewed_transcript.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    startVisualization() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.animateWaveform();
    }
    
    stopVisualization() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }
    
    animateWaveform() {
        if (!this.audioPlayer.paused) {
            this.animationId = requestAnimationFrame(() => this.animateWaveform());
        }
    }
    
    // Add loading state for waveform
    showWaveformLoading() {
        const canvas = this.waveformCanvas;
        const ctx = canvas.getContext('2d');
        
        // Clear canvas with dark background
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw loading animation
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        
        ctx.fillStyle = '#94a3b8';
        ctx.font = '14px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Loading waveform...', centerX, centerY);
        
        // Draw loading dots
        const time = Date.now() * 0.005;
        for (let i = 0; i < 3; i++) {
            const x = centerX + (i - 1) * 20;
            const opacity = 0.3 + 0.7 * Math.sin(time + i * 0.5);
            ctx.fillStyle = `rgba(59, 130, 246, ${opacity})`;
            ctx.beginPath();
            ctx.arc(x, centerY + 20, 3, 0, 2 * Math.PI);
            ctx.fill();
        }
    }
}

// Initialize the transcript viewer
document.addEventListener('DOMContentLoaded', () => {
    window.transcriptViewer = new TranscriptViewer();
});
