const REVIEW_CONFIG = {
    confidence: {
        low: 0.6,
        critical: 0.5,
        commonWords: 0.25
    },
    flags: {
        phone: true,
        case: true,
        money: true,
        date: true,
        time: true,
        names: true,
        spelled: true,
        numbers: true
    },
    context: {
        before: 5,
        after: 5
    },
    months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December',
        'Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 'Sep', 'Sept', 'Oct', 'Nov', 'Dec'],
    days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
        'Mon', 'Tue', 'Tues', 'Wed', 'Thu', 'Thur', 'Thurs', 'Fri', 'Sat', 'Sun'],
    commonWords: [
        'I', 'A', 'The', 'An', 'Hello', 'Hi', 'Yes', 'No', 'Okay', 'Ok', 'Thank', 'Thanks', 'Please', 'Sorry',
        'And', 'But', 'Or', 'This', 'That', 'These', 'Those', 'What', 'When', 'Where', 'Why', 'How', 'Who',
        'Which', 'Of', 'So', 'To', 'From', 'For', 'With', 'Can', 'Will', 'Was', 'Were', 'Are', 'Is', 'Be',
        'Been', 'Am', 'Do', 'Does', 'Did', 'On', 'In', 'At', 'By', 'Up', 'Out', 'Off', 'About', 'Into', 'It',
        'We', 'They', 'You', 'He', 'She', 'Them', 'Him', 'Her', 'Me', 'My', 'Your', 'Their', 'Our', 'His',
        'Its', 'Alright', 'Uh', 'Um', 'Uh-huh', 'Mm-hmm', 'Yeah', 'Nope'
    ]
};

const DEMO_REVIEW = {
    generated_at: new Date().toISOString(),
    review_engine: 'assemblyai_native',
    confidence_file: 'demo.confidence.json',
    transcript_file: 'demo_transcript.txt',
    config: {
        low_confidence_threshold: REVIEW_CONFIG.confidence.low,
        critical_confidence_threshold: REVIEW_CONFIG.confidence.critical,
        common_words_confidence_threshold: REVIEW_CONFIG.confidence.commonWords,
        context_words_before: REVIEW_CONFIG.context.before,
        context_words_after: REVIEW_CONFIG.context.after
    },
    overall_confidence: 0.856,
    statistics: {
        total_words: 52,
        flagged_words: 12,
        flag_percentage: 23.1,
        priority_counts: { high: 5, medium: 4, low: 3 },
        average_confidence: 0.821
    },
    flag_summary: {
        phone_number: 2,
        case_number: 1,
        money_amount: 1,
        date: 1,
        time: 1,
        names: 3,
        spelled_word: 2
    },
    words: [
        {
            word: 'Yes,',
            confidence: 0.28,
            start_time: 0.64,
            end_time: 0.96,
            speaker: 'A',
            index: 0,
            context_before: '',
            context_after: 'sir. Hi, Carlos.',
            flags: [
                { type: 'critical_confidence', reason: 'Critical: Very low confidence (28.0%)', priority: 'high' }
            ]
        },
        {
            word: 'sir.',
            confidence: 0.41,
            start_time: 1.04,
            end_time: 1.28,
            speaker: 'A',
            index: 1,
            context_before: 'Yes,',
            context_after: 'Hi, Carlos.',
            flags: [
                { type: 'low_confidence', reason: 'Low confidence (41.3%)', priority: 'medium' }
            ]
        },
        {
            word: 'Carlos.',
            confidence: 0.75,
            start_time: 1.92,
            end_time: 2.4,
            speaker: 'B',
            index: 3,
            context_before: 'Yes, sir. Hi,',
            context_after: 'I have Progressive',
            flags: [
                { type: 'names', reason: 'Possible proper noun', priority: 'medium' }
            ]
        },
        {
            word: 'Progressive',
            confidence: 0.92,
            start_time: 2.96,
            end_time: 3.68,
            speaker: 'B',
            index: 6,
            context_before: 'Carlos. I have',
            context_after: 'on the phone,',
            flags: [
                { type: 'names', reason: 'Possible proper noun', priority: 'medium' }
            ]
        },
        {
            word: 'phone,',
            confidence: 0.62,
            start_time: 4,
            end_time: 4.24,
            speaker: 'B',
            index: 9,
            context_before: 'Progressive on the',
            context_after: 'the adjuster',
            flags: [
                { type: 'phone_number', reason: 'Phone number detected - verify accuracy', priority: 'high' }
            ]
        },
        {
            word: 'case',
            confidence: 0.99,
            start_time: 5.68,
            end_time: 5.76,
            speaker: 'B',
            index: 14,
            context_before: 'the adjuster for the',
            context_after: 'of Anissa Roy',
            flags: [
                { type: 'case_number', reason: 'Possible case number - verify accuracy', priority: 'high' }
            ]
        },
        {
            word: 'Anissa',
            confidence: 0.53,
            start_time: 6.08,
            end_time: 6.72,
            speaker: 'B',
            index: 16,
            context_before: 'case of',
            context_after: 'Roy Hampton',
            flags: [
                { type: 'names', reason: 'Possible proper noun', priority: 'medium' },
                { type: 'critical_confidence', reason: 'Critical: Very low confidence (53.0%)', priority: 'high' }
            ]
        },
        {
            word: 'Hampton',
            confidence: 0.89,
            start_time: 7.04,
            end_time: 7.52,
            speaker: 'B',
            index: 18,
            context_before: 'Anissa Roy',
            context_after: 'regarding negotiations.',
            flags: [
                { type: 'names', reason: 'Possible proper noun', priority: 'medium' }
            ]
        },
        {
            word: 'negotiations.',
            confidence: 0.71,
            start_time: 8.16,
            end_time: 8.72,
            speaker: 'B',
            index: 21,
            context_before: 'Roy Hampton regarding',
            context_after: 'Oh, that would',
            flags: []
        },
        {
            word: 'offer',
            confidence: 0.98,
            start_time: 31.57,
            end_time: 31.89,
            speaker: 'A',
            index: 38,
            context_before: 'There is a new',
            context_after: 'or a new',
            flags: []
        },
        {
            word: 'proposal?',
            confidence: 0.32,
            start_time: 32.37,
            end_time: 32.45,
            speaker: 'A',
            index: 44,
            context_before: 'new offer or a new',
            context_after: '',
            flags: [
                { type: 'critical_confidence', reason: 'Critical: Very low confidence (32.0%)', priority: 'high' }
            ]
        },
        {
            word: 'Hold',
            confidence: 0.45,
            start_time: 40.0,
            end_time: 40.2,
            speaker: 'A',
            index: 50,
            context_before: 'Hold on. Let me',
            context_after: 'check.',
            flags: [
                { type: 'low_confidence', reason: 'Low confidence (45.0%)', priority: 'medium' }
            ]
        }
    ],
    corrections: [],
    audit: []
};

class AssemblyAIReviewStudio {
    constructor() {
        this.reviewData = null;
        this.words = [];
        this.filteredWords = [];
        this.corrections = new Map();
        this.approvedWords = new Set();
        this.dictionaryTerms = new Set();
        this.wordElements = new Map();
        this.wordMap = new Map();
        this.speakerNames = new Map();
        this.wordsByIndex = new Map();
        this.lineWordElements = new Map();
        this.lines = [];
        this.selectedWordIndex = null;
        this.activeTranscriptView = 'lines';
        this.audioBuffer = null;
        this.waveformData = null;
        this.animationFrame = null;
        this.enableGreenHighlight = true;
        this.wordTrackerFocus = false;
        this.currentFilters = {
            priority: 'all',
            type: 'all',
            flaggedOnly: true,
            search: ''
        };

        this.totalWordsCount = 0;
        this.flaggedWordsCount = 0;
        this.lowConfidenceCount = 0;
        this.confidenceThreshold = 0.7;

        this.elements = {};

        this.initializeElements();
        if (this.elements.threshold) {
            const parsedThreshold = parseFloat(this.elements.threshold.value);
            if (!Number.isNaN(parsedThreshold)) {
                this.confidenceThreshold = parsedThreshold;
            }
            this.elements.threshold.setAttribute('aria-valuenow', this.confidenceThreshold.toFixed(2));
            if (this.elements.thresholdValue) {
                this.elements.thresholdValue.textContent = `${Math.round(this.confidenceThreshold * 100)}%`;
            }
        }
        this.updateFocusToggleButton();
        this.switchTranscriptView('lines');
        this.bindEvents();
        this.loadDemoReview();
    }

    initializeElements() {
        this.elements.reviewFile = document.getElementById('reviewFile');
        this.elements.audioFile = document.getElementById('audioFile');
        this.elements.demoBtn = document.getElementById('demoBtn');
        this.elements.statsGrid = document.getElementById('statsGrid');
        this.elements.wordList = document.getElementById('wordList');
        this.elements.lineList = document.getElementById('transcriptLineList');
        this.elements.lineView = document.getElementById('lineView');
        this.elements.wordView = document.getElementById('wordTrackerView');
        this.elements.viewButtons = Array.from(document.querySelectorAll('[data-transcript-view]'));
        this.elements.focusWordTrackerBtn = document.getElementById('focusWordTrackerBtn');
        this.elements.filterPriority = document.getElementById('filterPriority');
        this.elements.filterType = document.getElementById('filterType');
        this.elements.showOnlyFlagged = document.getElementById('showOnlyFlagged');
        this.elements.enableGreenHighlight = document.getElementById('enableGreenHighlight');
        this.elements.searchInput = document.getElementById('searchInput');
        this.elements.threshold = document.getElementById('confidenceThreshold');
        this.elements.thresholdValue = document.getElementById('thresholdValue');
        this.elements.lineTotalWords = document.getElementById('lineTotalWords');
        this.elements.lineLowConfidence = document.getElementById('lineLowConfidence');
        this.elements.lineFlaggedWords = document.getElementById('lineFlaggedWords');
        this.elements.lineCurrentWord = document.getElementById('lineCurrentWord');
        this.elements.dictionaryList = document.getElementById('dictionaryList');
        this.elements.dictCount = document.getElementById('dictCount');
        this.elements.correctorSelected = document.getElementById('correctorSelected');
        this.elements.correctorContext = document.getElementById('correctorContext');
        this.elements.correctorFlags = document.getElementById('correctorFlags');
        this.elements.correctorForm = document.getElementById('correctorForm');
        this.elements.correctorInput = document.getElementById('correctorInput');
        this.elements.clearCorrectionBtn = document.getElementById('clearCorrectionBtn');
        this.elements.saveCorrectionBtn = document.getElementById('saveCorrectionBtn');
        this.elements.audioPlayer = document.getElementById('audioPlayer');
        this.elements.waveformCanvas = document.getElementById('waveformCanvas');
        this.elements.currentTime = document.getElementById('currentTime');
        this.elements.duration = document.getElementById('duration');
        this.elements.confidenceScore = document.getElementById('confidenceScore');
        this.elements.exportCorrectionsBtn = document.getElementById('exportCorrectionsBtn');
        this.elements.exportTranscriptBtn = document.getElementById('exportTranscriptBtn');
        this.elements.saveReviewBtn = document.getElementById('saveReviewBtn');
        this.elements.exportDictionaryBtn = document.getElementById('exportDictionaryBtn');
        this.elements.toast = document.getElementById('toast');
        this.elements.toggles = Array.from(document.querySelectorAll('.toggle'));
        this.elements.editSpeakersBtn = document.getElementById('editSpeakersBtn');
    }

    bindEvents() {
        this.elements.reviewFile.addEventListener('change', (e) => {
            if (e.target.files?.length) {
                this.handleReviewFile(e.target.files[0]);
            }
        });

        this.elements.audioFile.addEventListener('change', (e) => {
            if (e.target.files?.length) {
                this.handleAudioFile(e.target.files[0]);
            }
        });

        this.elements.demoBtn.addEventListener('click', () => this.loadDemoReview(true));

        this.elements.filterPriority.addEventListener('change', () => {
            this.currentFilters.priority = this.elements.filterPriority.value;
            this.renderFilteredWords();
        });

        this.elements.filterType.addEventListener('change', () => {
            this.currentFilters.type = this.elements.filterType.value;
            this.renderFilteredWords();
        });

        this.elements.showOnlyFlagged.addEventListener('change', () => {
            this.currentFilters.flaggedOnly = this.elements.showOnlyFlagged.checked;
            this.renderFilteredWords();
        });

        this.elements.enableGreenHighlight.addEventListener('change', () => {
            this.enableGreenHighlight = this.elements.enableGreenHighlight.checked;
            this.renderFilteredWords();
        });

        this.elements.searchInput.addEventListener('input', () => {
            this.currentFilters.search = this.elements.searchInput.value.trim().toLowerCase();
            this.renderFilteredWords();
        });

        if (this.elements.threshold) {
            this.elements.threshold.addEventListener('input', () => {
                const value = parseFloat(this.elements.threshold.value);
                if (Number.isNaN(value)) {
                    return;
                }
                this.confidenceThreshold = value;
                if (this.elements.thresholdValue) {
                    this.elements.thresholdValue.textContent = `${Math.round(value * 100)}%`;
                }
                this.elements.threshold.setAttribute('aria-valuenow', value.toFixed(2));
                this.highlightConfidenceThreshold(value);
            });
        }

        this.elements.exportCorrectionsBtn.addEventListener('click', () => this.exportCorrections());
        this.elements.exportTranscriptBtn.addEventListener('click', () => this.exportCorrectedTranscript());
        this.elements.saveReviewBtn.addEventListener('click', () => this.saveReviewSnapshot());
        this.elements.exportDictionaryBtn.addEventListener('click', () => this.exportDictionaryTerms());
        this.elements.editSpeakersBtn.addEventListener('click', () => this.editSpeakerNames());

        this.elements.viewButtons.forEach(button => {
            button.addEventListener('click', () => this.switchTranscriptView(button.dataset.transcriptView));
        });

        if (this.elements.focusWordTrackerBtn) {
            this.elements.focusWordTrackerBtn.addEventListener('click', () => {
                this.setWordTrackerFocus(!this.wordTrackerFocus);
            });
        }

        if (this.elements.correctorForm) {
            this.elements.correctorForm.addEventListener('submit', (event) => {
                event.preventDefault();
                if (this.selectedWordIndex === null) return;
                const word = this.wordsByIndex.get(this.selectedWordIndex);
                if (!word) return;
                if (this.elements.saveCorrectionBtn && this.elements.saveCorrectionBtn.disabled) {
                    return;
                }
                const value = this.elements.correctorInput.value;
                this.applyCorrection(word, value);
            });
        }

        if (this.elements.clearCorrectionBtn) {
            this.elements.clearCorrectionBtn.addEventListener('click', () => {
                if (this.selectedWordIndex === null) return;
                const word = this.wordsByIndex.get(this.selectedWordIndex);
                if (!word) return;
                this.removeCorrection(word);
            });
        }

        if (this.elements.correctorInput) {
            this.elements.correctorInput.addEventListener('input', () => this.updateCorrectorButtons());
        }

        this.elements.toggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                toggle.classList.toggle('active');
                const flag = toggle.dataset.flag;
                if (flag && REVIEW_CONFIG.flags.hasOwnProperty(flag)) {
                    REVIEW_CONFIG.flags[flag] = toggle.classList.contains('active');
                    if (this.reviewData && !this.reviewData.wordsFromConfidence) {
                        // If original review file already had flags we simply re-filter
                        this.renderFilteredWords();
                    } else if (this.reviewData) {
                        // Recalculate from source when using confidence file
                        this.rebuildFromConfidence();
                    }
                }
            });
        });

        this.elements.audioPlayer.addEventListener('timeupdate', () => this.handleAudioTimeUpdate());
        this.elements.audioPlayer.addEventListener('loadedmetadata', () => this.updateAudioDuration());
        this.elements.audioPlayer.addEventListener('play', () => this.animateWaveformCursor());
        this.elements.audioPlayer.addEventListener('pause', () => this.stopWaveformCursor());
        this.elements.audioPlayer.addEventListener('ended', () => this.stopWaveformCursor());

        this.elements.waveformCanvas.addEventListener('click', (event) => this.seekFromWaveform(event));

        window.addEventListener('resize', () => {
            if (this.resizeTimeout) {
                clearTimeout(this.resizeTimeout);
            }
            this.resizeTimeout = setTimeout(() => {
                if (this.words.length) {
                    this.drawWaveform();
                }
            }, 200);
        });
    }

    async handleReviewFile(file) {
        try {
            const text = await file.text();
            const data = JSON.parse(text);

            if (Array.isArray(data.word_data)) {
                // Confidence file, build review
                this.reviewData = this.buildReviewFromConfidence(data);
                this.reviewData.wordsFromConfidence = data;
            } else if (Array.isArray(data.words)) {
                this.reviewData = data;
            } else {
                throw new Error('Unsupported review format');
            }

            this.initializeStateFromReview();
            this.showToast(`Loaded ${file.name}`);
        } catch (error) {
            console.error(error);
            this.showToast('Unable to load review file');
        }
    }

    buildReviewFromConfidence(confidenceData) {
        const words = confidenceData.word_data || [];
        const expectedTerms = Array.isArray(confidenceData.expected_terms) ? confidenceData.expected_terms : [];

        const reviewWords = words.map((wordData, index) => {
            const word = wordData.word || '';
            const cleanWord = word.replace(/[.,!?;:'"()]/g, '');
            const confidence = wordData.confidence !== undefined ? wordData.confidence : null;
            const flags = this.generateFlags(word, cleanWord, confidence, expectedTerms);
            const { before, after } = this.buildContext(words, index, REVIEW_CONFIG.context.before, REVIEW_CONFIG.context.after);

            return {
                word,
                confidence,
                start_time: wordData.start_time ?? null,
                end_time: wordData.end_time ?? null,
                speaker: wordData.speaker_tag ?? null,
                index,
                context_before: before,
                context_after: after,
                flags
            };
        });

        const totalWords = reviewWords.length;
        const flaggedWords = reviewWords.filter(w => w.flags && w.flags.length > 0);
        const priorityCounts = { high: 0, medium: 0, low: 0 };
        flaggedWords.forEach(word => {
            word.flags.forEach(flag => {
                if (priorityCounts[flag.priority] !== undefined) {
                    priorityCounts[flag.priority] += 1;
                }
            });
        });

        const avgConfidence = reviewWords.filter(w => typeof w.confidence === 'number').reduce((sum, w) => sum + w.confidence, 0);
        const avg = reviewWords.filter(w => typeof w.confidence === 'number').length
            ? avgConfidence / reviewWords.filter(w => typeof w.confidence === 'number').length
            : null;

        const flagSummary = {};
        flaggedWords.forEach(word => {
            word.flags.forEach(flag => {
                flagSummary[flag.type] = (flagSummary[flag.type] || 0) + 1;
            });
        });

        return {
            generated_at: new Date().toISOString(),
            review_engine: 'assemblyai_native',
            confidence_file: confidenceData.confidence_file || 'uploaded.confidence.json',
            transcript_file: confidenceData.transcript_file || 'uploaded_transcript.txt',
            config: {
                low_confidence_threshold: REVIEW_CONFIG.confidence.low,
                critical_confidence_threshold: REVIEW_CONFIG.confidence.critical,
                common_words_confidence_threshold: REVIEW_CONFIG.confidence.commonWords,
                context_words_before: REVIEW_CONFIG.context.before,
                context_words_after: REVIEW_CONFIG.context.after
            },
            overall_confidence: confidenceData.overall_confidence ?? null,
            statistics: {
                total_words: totalWords,
                flagged_words: flaggedWords.length,
                flag_percentage: totalWords ? Number(((flaggedWords.length / totalWords) * 100).toFixed(1)) : 0,
                priority_counts: priorityCounts,
                average_confidence: avg
            },
            flag_summary: flagSummary,
            words: reviewWords,
            corrections: [],
            audit: []
        };
    }

    generateFlags(word, cleanWord, confidence, expectedTerms) {
        const flags = [];
        const lowerWord = cleanWord.toLowerCase();
        const isExpected = expectedTerms.some(term => {
            const termLower = term.toLowerCase();
            return termLower === lowerWord || termLower.split(/\s+/).includes(lowerWord);
        });

        const isCommon = REVIEW_CONFIG.commonWords.includes(cleanWord);

        if (typeof confidence === 'number' && !isExpected) {
            const criticalThreshold = isCommon ? REVIEW_CONFIG.confidence.commonWords : REVIEW_CONFIG.confidence.critical;
            const lowThreshold = REVIEW_CONFIG.confidence.low;

            if (confidence < criticalThreshold) {
                flags.push({ type: 'critical_confidence', reason: `Critical: Very low confidence (${(confidence * 100).toFixed(1)}%)`, priority: 'high', confidence });
            } else if (!isCommon && confidence < lowThreshold) {
                flags.push({ type: 'low_confidence', reason: `Low confidence (${(confidence * 100).toFixed(1)}%)`, priority: 'medium', confidence });
            }
        }

        if (REVIEW_CONFIG.flags.phone && (/\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b/.test(cleanWord) || /^[\d-]+$/.test(cleanWord))) {
            flags.push({ type: 'phone_number', reason: 'Phone number detected - verify accuracy', priority: 'high' });
        }

        if (REVIEW_CONFIG.flags.case && /\b\d{6,}\b/.test(cleanWord)) {
            flags.push({ type: 'case_number', reason: 'Possible case number - verify accuracy', priority: 'high' });
        }

        if (REVIEW_CONFIG.flags.money && (/\$[\d,]+(?:\.\d{2})?|\b\d+\s*(?:dollars?|cents?)\b/i.test(word))) {
            flags.push({ type: 'money_amount', reason: 'Dollar amount detected - verify accuracy', priority: 'high' });
        }

        if (REVIEW_CONFIG.flags.date && /\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2})/i.test(word)) {
            flags.push({ type: 'date', reason: 'Date detected - verify accuracy', priority: 'medium' });
        }

        if (REVIEW_CONFIG.flags.time && /\b\d{1,2}:\d{2}\s*(?:AM|PM)?\b/i.test(word)) {
            flags.push({ type: 'time', reason: 'Time detected - verify accuracy', priority: 'medium' });
        }

        if (REVIEW_CONFIG.flags.numbers && /^\d+$/.test(cleanWord)) {
            flags.push({ type: 'number', reason: 'Number detected - confirm accuracy', priority: 'low' });
        }

        if (REVIEW_CONFIG.flags.spelled && /^[0-9-]+$/.test(cleanWord) && cleanWord.includes('-')) {
            flags.push({ type: 'spelled_word', reason: 'Spelled number or name - confirm transcription', priority: 'high' });
        }

        if (REVIEW_CONFIG.flags.names && this.isLikelyName(cleanWord)) {
            flags.push({ type: 'names', reason: 'Possible proper noun', priority: 'medium' });
        }

        return flags;
    }

    isLikelyName(word) {
        if (!word || word.length < 2) return false;
        if (word.toUpperCase() === word) return false;
        if (!isNaN(Number(word))) return false;
        if (/^[\d-]+$/.test(word)) return false;
        if (/^\d+(st|nd|rd|th)$/i.test(word)) return false;
        if (REVIEW_CONFIG.months.includes(word)) return false;
        if (REVIEW_CONFIG.days.includes(word)) return false;
        return word[0] === word[0].toUpperCase();
    }

    buildContext(words, index, beforeCount, afterCount) {
        const start = Math.max(0, index - beforeCount);
        const end = Math.min(words.length, index + afterCount + 1);

        const before = words.slice(start, index).map(w => w.word || '').join(' ');
        const after = words.slice(index + 1, end).map(w => w.word || '').join(' ');

        return { before, after };
    }

    initializeStateFromReview() {
        if (!this.reviewData) return;

        this.setWordTrackerFocus(false, { skipViewSwitch: true });
        this.switchTranscriptView('lines');

        this.words = Array.isArray(this.reviewData.words) ? [...this.reviewData.words] : [];
        this.corrections.clear();
        this.approvedWords = new Set();
        this.dictionaryTerms = new Set();
        this.wordElements.clear();
        this.wordMap.clear();
        this.wordsByIndex.clear();
        this.lineWordElements.clear();

        if (Array.isArray(this.reviewData.corrections)) {
            this.reviewData.corrections.forEach(correction => {
                if (correction && typeof correction.index === 'number') {
                    this.corrections.set(correction.index, correction.newValue);
                }
            });
        }

        if (Array.isArray(this.reviewData.approved_words)) {
            this.reviewData.approved_words.forEach(index => this.approvedWords.add(index));
        }

        if (Array.isArray(this.reviewData.dictionary_queue)) {
            this.reviewData.dictionary_queue.forEach(term => this.dictionaryTerms.add(term));
        }

        if (Array.isArray(this.reviewData.words)) {
            this.reviewData.words.forEach(word => {
                this.wordsByIndex.set(word.index, word);
                if (word.speaker && !this.speakerNames.has(word.speaker)) {
                    this.speakerNames.set(word.speaker, `Speaker ${word.speaker}`);
                }
            });
        }

        this.populateFlagFilter();
        this.lines = this.buildTranscriptLines(this.words);
        this.setSelectedWord(null, { forceRender: true });
        this.updateStats();
        this.renderFilteredWords();
        this.renderTranscriptLines();
        this.updateDictionaryList();
        this.drawWaveform();
        this.updateAudioDuration();
        this.highlightConfidenceThreshold(parseFloat(this.elements.threshold.value));
    }

    populateFlagFilter() {
        const types = new Set();
        this.words.forEach(word => {
            (word.flags || []).forEach(flag => types.add(flag.type));
        });

        const filter = this.elements.filterType;
        const selected = filter.value;
        filter.innerHTML = '<option value="all">All Types</option>';
        Array.from(types).sort().forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type.replace(/_/g, ' ');
            filter.appendChild(option);
        });
        if (Array.from(types).includes(selected)) {
            filter.value = selected;
        }
    }

    updateStats() {
        if (!this.reviewData) {
            this.elements.statsGrid.innerHTML = '';
            this.totalWordsCount = 0;
            this.flaggedWordsCount = 0;
            this.lowConfidenceCount = 0;
            this.updateLineStatusSummary();
            return;
        }

        const stats = this.reviewData.statistics || {};
        const totalWords = stats.total_words || this.words.length;
        const flaggedWords = stats.flagged_words ?? this.words.filter(w => w.flags && w.flags.length).length;
        const flagPercentage = stats.flag_percentage ?? (totalWords ? ((flaggedWords / totalWords) * 100).toFixed(1) : 0);
        const avgConfidence = stats.average_confidence;
        const highPriority = stats.priority_counts?.high ?? this.words.filter(w => (w.flags || []).some(f => f.priority === 'high')).length;
        const threshold = Number.isFinite(this.confidenceThreshold) ? this.confidenceThreshold : 0.7;
        const lowConfidence = stats.low_confidence_words ?? this.words.filter(w => typeof w.confidence === 'number' && w.confidence < threshold).length;

        const cards = [
            { title: 'Total Words', value: totalWords.toLocaleString(), trend: 'Review span' },
            { title: 'Flagged Words', value: flaggedWords.toLocaleString(), trend: 'Needs attention' },
            { title: 'Flag %', value: `${flagPercentage}%`, trend: 'Focus index' },
            { title: 'Avg Confidence', value: avgConfidence ? `${(avgConfidence * 100).toFixed(1)}%` : 'N/A', trend: 'Model trust' },
            { title: 'High Priority', value: highPriority, trend: 'Critical callbacks' },
            { title: 'Corrections', value: this.corrections.size, trend: 'Manual edits' },
            { title: 'Approved', value: this.approvedWords.size, trend: 'Validated terms' },
            { title: 'Dictionary', value: this.dictionaryTerms.size, trend: 'Playbook queue' }
        ];

        this.elements.statsGrid.innerHTML = cards.map(card => `
            <div class="stat-card">
                <h3>${card.title}</h3>
                <div class="value">${card.value}</div>
                <div class="trend">${card.trend}</div>
            </div>
        `).join('');

        this.totalWordsCount = totalWords;
        this.flaggedWordsCount = flaggedWords;
        this.lowConfidenceCount = lowConfidence;
        this.updateLineStatusSummary();
    }

    updateLineStatusSummary(overrides = {}) {
        const summary = {
            totalWords: this.totalWordsCount || 0,
            flaggedWords: this.flaggedWordsCount || 0,
            lowConfidence: this.lowConfidenceCount || 0,
            ...overrides
        };

        if (Number.isFinite(summary.totalWords)) {
            this.totalWordsCount = summary.totalWords;
        }
        if (Number.isFinite(summary.flaggedWords)) {
            this.flaggedWordsCount = summary.flaggedWords;
        }
        if (Number.isFinite(summary.lowConfidence)) {
            this.lowConfidenceCount = summary.lowConfidence;
        }

        if (this.elements.lineTotalWords) {
            this.elements.lineTotalWords.textContent = `Words: ${this.totalWordsCount.toLocaleString()}`;
        }
        if (this.elements.lineFlaggedWords) {
            this.elements.lineFlaggedWords.textContent = `Flags: ${this.flaggedWordsCount.toLocaleString()}`;
        }
        if (this.elements.lineLowConfidence) {
            this.elements.lineLowConfidence.textContent = `Low Confidence: ${this.lowConfidenceCount.toLocaleString()}`;
        }
    }

    updateCurrentLineStatus(word) {
        if (!this.elements.lineCurrentWord) {
            return;
        }

        if (!word) {
            this.elements.lineCurrentWord.textContent = 'Current: --';
            return;
        }

        const term = (this.corrections.get(word.index) || word.word || '').trim();
        const time = typeof word.start_time === 'number' ? this.formatTime(word.start_time) : null;
        const label = term ? term : '—';
        this.elements.lineCurrentWord.textContent = `Current: ${label}${time ? ` (${time})` : ''}`;
    }

    renderFilteredWords() {
        if (!this.words.length) {
            this.elements.wordList.innerHTML = `
                <div class="empty-state">
                    <h3>No transcript loaded.</h3>
                    <p>Upload a review file to begin quality checking.</p>
                </div>`;
            return;
        }

        this.filteredWords = this.words.filter(word => {
            if (this.currentFilters.flaggedOnly && (!word.flags || word.flags.length === 0) && !this.approvedWords.has(word.index)) {
                return false;
            }

            if (this.currentFilters.priority !== 'all') {
                const hasPriority = (word.flags || []).some(flag => flag.priority === this.currentFilters.priority);
                if (!hasPriority) return false;
            }

            if (this.currentFilters.type !== 'all') {
                const hasType = (word.flags || []).some(flag => flag.type === this.currentFilters.type);
                if (!hasType) return false;
            }

            if (this.currentFilters.search) {
                const haystack = [word.word, word.context_before, word.context_after].join(' ').toLowerCase();
                if (!haystack.includes(this.currentFilters.search)) {
                    return false;
                }
            }

            return true;
        });

        if (!this.filteredWords.length) {
            this.elements.wordList.innerHTML = `
                <div class="empty-state">
                    <h3>No matches for current filters.</h3>
                    <p>Adjust filters to broaden the review lens.</p>
                </div>`;
            return;
        }

        const fragment = document.createDocumentFragment();
        this.wordElements.clear();
        this.wordMap.clear();

        this.filteredWords.forEach(word => {
            const card = this.buildWordCard(word);
            fragment.appendChild(card);
            this.wordElements.set(word.index, card);
            if (word.start_time !== null && word.end_time !== null) {
                this.wordMap.set(word.index, { start: word.start_time, end: word.end_time, element: card, word });
            }
        });

        this.elements.wordList.innerHTML = '';
        this.elements.wordList.appendChild(fragment);
        this.highlightConfidenceThreshold(parseFloat(this.elements.threshold.value));
        this.updateSelectionHighlight();
    }

    buildWordCard(word) {
        const card = document.createElement('article');
        card.className = 'word-card';
        card.dataset.index = word.index;
        if (this.approvedWords.has(word.index) && this.enableGreenHighlight) {
            card.classList.add('approved');
        }

        const correctedWord = this.corrections.get(word.index);
        const displayWord = correctedWord ? `<del>${word.word}</del> <span class="replacement">${correctedWord}</span>` : word.word;
        const confidenceClass = this.getConfidenceClass(word.confidence);
        const highestPriority = this.getHighestPriority(word.flags);

        card.innerHTML = `
            <div class="word-header">
                <div class="word-title">${displayWord}</div>
                <div class="word-meta">
                    ${word.confidence !== null ? `<span class="badge ${confidenceClass}">${(word.confidence * 100).toFixed(1)}%</span>` : ''}
                    ${word.speaker ? `<span class="badge">${this.speakerNames.get(word.speaker) || `Speaker ${word.speaker}`}</span>` : ''}
                    ${highestPriority ? `<span class="badge priority-${highestPriority}">${highestPriority} priority</span>` : ''}
                    <span class="badge">⏱ ${this.formatTime(word.start_time)}</span>
                </div>
            </div>
            <div class="context-block">
                <span class="before">${word.context_before}</span>
                <span class="current" role="button">${correctedWord || word.word}</span>
                <span class="after">${word.context_after}</span>
            </div>
            ${(word.flags && word.flags.length) ? `
                <div class="flag-list">
                    ${word.flags.map(flag => `<span class="flag-chip priority-${flag.priority}" title="${flag.reason}">${flag.type.replace(/_/g, ' ')}</span>`).join('')}
                </div>` : ''}
            <div class="action-bar">
                <button data-action="play">▶️ Play</button>
                <button data-action="approve" class="secondary">${this.approvedWords.has(word.index) ? 'Unapprove' : 'Approve'}</button>
                <button data-action="dictionary" class="secondary">${this.dictionaryTerms.has(word.word) ? 'Remove from Dictionary' : 'Add to Dictionary'}</button>
                <button data-action="correct">Open Corrector</button>
                ${correctedWord ? '<button data-action="remove" class="destructive">Remove Correction</button>' : ''}
            </div>
        `;

        if (word.index === this.selectedWordIndex) {
            card.classList.add('selected');
        }

        card.querySelector('[data-action="play"]').addEventListener('click', () => this.seekToWord(word));
        card.querySelector('[data-action="approve"]').addEventListener('click', () => this.toggleApprove(word));
        card.querySelector('[data-action="dictionary"]').addEventListener('click', () => this.toggleDictionary(word));
        card.querySelector('[data-action="correct"]').addEventListener('click', () => this.focusCorrector(word));
        const removeBtn = card.querySelector('[data-action="remove"]');
        if (removeBtn) {
            removeBtn.addEventListener('click', () => this.removeCorrection(word));
        }

        if (word.start_time !== null) {
            card.querySelector('.context-block .current').addEventListener('click', () => this.seekToWord(word));
        }

        return card;
    }

    buildTranscriptLines(words) {
        if (!Array.isArray(words) || !words.length) {
            return [];
        }

        const lines = [];
        let currentLine = null;
        let lineId = 0;

        words.forEach(word => {
            if (!word) return;
            const speakerTag = word.speaker ?? null;
            const shouldStartNew = !currentLine
                || currentLine.speaker !== speakerTag
                || this.shouldBreakLine(currentLine, word);

            if (shouldStartNew) {
                if (currentLine) {
                    lines.push(currentLine);
                }
                currentLine = {
                    id: lineId++,
                    speaker: speakerTag,
                    wordIndexes: [],
                    start: word.start_time ?? null,
                    end: word.end_time ?? null
                };
            }

            currentLine.wordIndexes.push(word.index);
            if (currentLine.start === null && word.start_time !== null && word.start_time !== undefined) {
                currentLine.start = word.start_time;
            }
            if (word.end_time !== null && word.end_time !== undefined) {
                currentLine.end = word.end_time;
            }
        });

        if (currentLine) {
            lines.push(currentLine);
        }

        return lines;
    }

    shouldBreakLine(line, nextWord) {
        if (!line || !Array.isArray(line.wordIndexes) || !line.wordIndexes.length) {
            return true;
        }

        const lastIndex = line.wordIndexes[line.wordIndexes.length - 1];
        const lastWord = this.wordsByIndex.get(lastIndex);
        if (!lastWord) {
            return true;
        }

        if (nextWord.speaker !== lastWord.speaker) {
            return true;
        }

        const lastToken = (lastWord.word || '').trim();
        if (lastToken && /[.?!]/.test(lastToken.slice(-1))) {
            return true;
        }

        if (typeof lastWord.end_time === 'number' && typeof nextWord.start_time === 'number') {
            if ((nextWord.start_time - lastWord.end_time) > 2) {
                return true;
            }
        }

        return false;
    }

    renderTranscriptLines() {
        if (!this.elements.lineList) {
            return;
        }

        this.lineWordElements.clear();
        this.elements.lineList.innerHTML = '';

        if (!this.words.length) {
            this.elements.lineList.innerHTML = `
                <div class="empty-state">
                    <h3>No transcript loaded.</h3>
                    <p>Upload a review file to see the full line-by-line view.</p>
                </div>`;
            return;
        }

        if (!Array.isArray(this.lines) || !this.lines.length) {
            this.lines = this.buildTranscriptLines(this.words);
        }

        const fragment = document.createDocumentFragment();
        const threshold = Number.isFinite(this.confidenceThreshold)
            ? this.confidenceThreshold
            : parseFloat(this.elements.threshold?.value || '0.7') || 0.7;

        this.lines.forEach(line => {
            const lineElement = document.createElement('article');
            lineElement.className = 'line-card';
            lineElement.dataset.lineId = line.id;

            const firstWord = this.wordsByIndex.get(line.wordIndexes[0]);
            const speakerName = firstWord?.speaker ? (this.speakerNames.get(firstWord.speaker) || `Speaker ${firstWord.speaker}`) : 'Unknown speaker';
            const flaggedCount = line.wordIndexes.reduce((count, index) => {
                const word = this.wordsByIndex.get(index);
                return count + ((word?.flags && word.flags.length) ? 1 : 0);
            }, 0);
            const hasAudio = line.wordIndexes.some(index => {
                const word = this.wordsByIndex.get(index);
                return word && word.start_time !== null && word.start_time !== undefined;
            });

            const metrics = line.wordIndexes.reduce((acc, index) => {
                const word = this.wordsByIndex.get(index);
                if (!word || typeof word.confidence !== 'number') {
                    return acc;
                }
                acc.confidenceTotal += word.confidence;
                acc.confidenceCount += 1;
                if (word.confidence < threshold) {
                    acc.lowConfidence += 1;
                }
                return acc;
            }, { confidenceTotal: 0, confidenceCount: 0, lowConfidence: 0 });

            const avgConfidence = metrics.confidenceCount ? metrics.confidenceTotal / metrics.confidenceCount : null;
            const lowConfidence = metrics.lowConfidence;
            const timeLabel = line.start !== null && line.start !== undefined
                ? `${this.formatTime(line.start)}${line.end !== null && line.end !== undefined ? ` – ${this.formatTime(line.end)}` : ''}`
                : '';

            line.avgConfidence = avgConfidence;
            line.flaggedCount = flaggedCount;
            line.lowConfidence = lowConfidence;

            const metricsMarkup = `
                <div class="line-metrics">
                    ${avgConfidence !== null ? `<span class="metric-chip" data-line-avg>${(avgConfidence * 100).toFixed(0)}% avg conf</span>` : ''}
                    <span class="metric-chip ${flaggedCount ? 'flag-chip' : 'is-muted'}" data-line-flags>${flaggedCount ? `${flaggedCount} flag${flaggedCount === 1 ? '' : 's'}` : 'No flags'}</span>
                    <span class="metric-chip low-chip ${lowConfidence ? '' : 'is-muted'}" data-line-low>${lowConfidence ? `${lowConfidence} low conf` : 'No low conf'}</span>
                </div>
            `;

            lineElement.innerHTML = `
                <div class="line-header">
                    <div class="line-speaker">
                        <span class="speaker-chip">${speakerName}</span>
                        ${timeLabel ? `<span class="line-timestamp">${timeLabel}</span>` : ''}
                    </div>
                    <div class="line-controls">
                        ${metricsMarkup}
                        ${hasAudio ? '<button class="ghost-btn small" data-action="play-line">▶️ Play Line</button>' : ''}
                    </div>
                </div>
                <div class="line-body">
                    <p class="line-text"></p>
                </div>
            `;

            lineElement.dataset.avgConfidence = avgConfidence !== null ? avgConfidence.toString() : '';
            lineElement.dataset.flaggedCount = flaggedCount.toString();
            lineElement.dataset.lowConfidence = lowConfidence.toString();

            const textContainer = lineElement.querySelector('.line-text');
            line.wordIndexes.forEach((wordIndex, idx) => {
                const word = this.wordsByIndex.get(wordIndex);
                if (!word) return;

                const span = document.createElement('span');
                span.className = 'line-word';
                if ((word.flags || []).length) {
                    span.classList.add('flagged');
                }
                if (this.corrections.has(word.index)) {
                    span.classList.add('corrected');
                }
                if (word.index === this.selectedWordIndex) {
                    span.classList.add('selected');
                }
                if (typeof word.confidence === 'number' && word.confidence < threshold) {
                    span.classList.add('confidence-low');
                }
                span.dataset.index = word.index;
                const displayText = (this.corrections.get(word.index) || word.word || '').trim();
                span.textContent = displayText;
                const ariaParts = [displayText ? `Word ${displayText}` : 'Word'];
                if (speakerName && speakerName !== 'Unknown speaker') {
                    ariaParts.push(`spoken by ${speakerName}`);
                }
                if (word.start_time !== null && word.start_time !== undefined) {
                    ariaParts.push(`at ${this.formatTime(word.start_time)}`);
                }
                span.setAttribute('aria-label', ariaParts.join(', '));
                span.addEventListener('click', () => this.focusCorrector(word));
                span.setAttribute('role', 'button');
                span.setAttribute('tabindex', '0');
                span.addEventListener('keydown', (event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        this.focusCorrector(word);
                    }
                });
                textContainer.appendChild(span);
                if (idx !== line.wordIndexes.length - 1) {
                    textContainer.appendChild(document.createTextNode(' '));
                }
                this.lineWordElements.set(word.index, span);
            });

            if (hasAudio) {
                const playBtn = lineElement.querySelector('[data-action="play-line"]');
                playBtn?.addEventListener('click', () => this.playLine(line));
            }

            fragment.appendChild(lineElement);
        });

        this.elements.lineList.appendChild(fragment);
        this.updateLineConfidenceStates(threshold);
        this.updateSelectionHighlight();
        const selectedWord = this.selectedWordIndex !== null ? this.wordsByIndex.get(this.selectedWordIndex) : null;
        this.updateCurrentLineStatus(selectedWord || null);
    }

    updateLineConfidenceStates(threshold) {
        if (!Array.isArray(this.lines) || !this.elements.lineList) {
            return;
        }

        const safeThreshold = Number.isFinite(threshold) ? threshold : 0.7;
        let totalLowConfidence = 0;

        this.lines.forEach(line => {
            if (!Array.isArray(line.wordIndexes) || !line.wordIndexes.length) {
                return;
            }

            const lineElement = this.elements.lineList.querySelector(`[data-line-id="${line.id}"]`);
            if (!lineElement) {
                return;
            }

            const lowCount = line.wordIndexes.reduce((count, index) => {
                const word = this.wordsByIndex.get(index);
                if (!word || typeof word.confidence !== 'number') {
                    return count;
                }
                return count + (word.confidence < safeThreshold ? 1 : 0);
            }, 0);

            line.lowConfidence = lowCount;
            totalLowConfidence += lowCount;

            const lowChip = lineElement.querySelector('[data-line-low]');
            if (lowChip) {
                if (lowCount) {
                    lowChip.textContent = `${lowCount} low conf`;
                    lowChip.classList.remove('is-muted');
                } else {
                    lowChip.textContent = 'No low conf';
                    lowChip.classList.add('is-muted');
                }
            }

            const avgChip = lineElement.querySelector('[data-line-avg]');
            if (avgChip) {
                const avg = typeof line.avgConfidence === 'number' ? line.avgConfidence : null;
                avgChip.classList.toggle('low-chip', avg !== null && avg < safeThreshold);
            }

            lineElement.classList.toggle('has-low-confidence', lowCount > 0);
            lineElement.dataset.lowConfidence = lowCount.toString();
        });

        this.lowConfidenceCount = totalLowConfidence;
        this.updateLineStatusSummary({ lowConfidence: totalLowConfidence });
    }

    playLine(line) {
        if (!line || !Array.isArray(line.wordIndexes) || !line.wordIndexes.length) {
            return;
        }
        const timedWord = line.wordIndexes
            .map(index => this.wordsByIndex.get(index))
            .find(word => word && word.start_time !== null && word.start_time !== undefined);
        const targetWord = timedWord || this.wordsByIndex.get(line.wordIndexes[0]);
        if (!targetWord) {
            return;
        }
        this.seekToWord(targetWord);
    }

    switchTranscriptView(view) {
        if (view !== 'lines' && view !== 'words') {
            return;
        }

        if (view === 'lines' && this.wordTrackerFocus) {
            this.setWordTrackerFocus(false, { skipViewSwitch: true });
        }

        this.activeTranscriptView = view;

        if (this.elements.lineView) {
            this.elements.lineView.classList.toggle('is-active', view === 'lines');
        }
        if (this.elements.wordView) {
            this.elements.wordView.classList.toggle('is-active', view === 'words');
        }

        this.elements.viewButtons.forEach(button => {
            const isActive = button.dataset.transcriptView === view;
            button.classList.toggle('active', isActive);
            button.setAttribute('aria-selected', String(isActive));
        });

        if (view === 'lines' && this.selectedWordIndex !== null) {
            const target = this.lineWordElements.get(this.selectedWordIndex);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }

        if (view === 'words' && this.selectedWordIndex !== null) {
            this.highlightWordCard(this.selectedWordIndex, { scroll: true });
        }
    }

    setWordTrackerFocus(enable, options = {}) {
        const { skipViewSwitch = false } = options;
        const desiredState = Boolean(enable);

        const body = document.body;

        if (!this.elements.focusWordTrackerBtn || !body) {
            this.wordTrackerFocus = false;
            if (body) {
                body.classList.remove('word-tracker-focus');
            }
            return;
        }

        if (this.wordTrackerFocus === desiredState) {
            body.classList.toggle('word-tracker-focus', this.wordTrackerFocus);
            this.updateFocusToggleButton();
            return;
        }

        this.wordTrackerFocus = desiredState;
        body.classList.toggle('word-tracker-focus', this.wordTrackerFocus);
        this.updateFocusToggleButton();

        if (!skipViewSwitch) {
            const targetView = this.wordTrackerFocus ? 'words' : 'lines';
            if (this.activeTranscriptView !== targetView) {
                this.switchTranscriptView(targetView);
            }
        }
    }

    updateFocusToggleButton() {
        const button = this.elements.focusWordTrackerBtn;
        if (!button) {
            return;
        }

        button.classList.toggle('active', this.wordTrackerFocus);
        button.setAttribute('aria-pressed', String(this.wordTrackerFocus));
        button.textContent = this.wordTrackerFocus ? 'Restore Transcript Focus' : 'Word Tracker Focus';
    }

    setSelectedWord(index, options = {}) {
        const { 
            focusInput = false,
            scrollWordCard = false,
            scrollLine = false,
            forceRender = false
        } = options;

        const hasWord = index !== null && index !== undefined && this.wordsByIndex.has(index);
        const previousIndex = this.selectedWordIndex;
        const word = hasWord ? this.wordsByIndex.get(index) : null;

        if (!hasWord) {
            this.selectedWordIndex = null;
            if (forceRender || previousIndex !== null) {
                this.renderCorrectorPane();
            }
            this.wordElements.forEach(card => card.classList.remove('current'));
            this.updateSelectionHighlight();
            this.updateCorrectorButtons();
            this.updateCurrentLineStatus(null);
            return;
        }

        this.selectedWordIndex = index;

        if (forceRender || previousIndex !== index) {
            this.renderCorrectorPane();
        }

        this.highlightWordCard(index, { scroll: scrollWordCard });

        if (scrollLine) {
            const lineElement = this.lineWordElements.get(index);
            if (lineElement) {
                lineElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }

        if (focusInput && this.elements.correctorInput && !this.elements.correctorInput.disabled) {
            this.elements.correctorInput.focus();
            this.elements.correctorInput.select();
        }

        this.updateSelectionHighlight();
        this.updateCorrectorButtons();
        this.updateCurrentLineStatus(word);
    }

    updateSelectionHighlight() {
        const selected = this.selectedWordIndex;

        this.wordElements.forEach((card, index) => {
            if (!card) return;
            card.classList.toggle('selected', index === selected);
        });

        this.lineWordElements.forEach((element, index) => {
            if (!element) return;
            element.classList.toggle('selected', index === selected);
        });
    }

    focusCorrector(word, options = {}) {
        if (!word) {
            return;
        }
        const { focusInput = true } = options;
        this.switchTranscriptView('lines');
        this.setSelectedWord(word.index, {
            focusInput,
            scrollLine: true,
            scrollWordCard: true,
            forceRender: true
        });
    }

    renderCorrectorPane() {
        if (!this.elements.correctorSelected || !this.elements.correctorInput) {
            return;
        }

        if (this.selectedWordIndex === null || !this.wordsByIndex.has(this.selectedWordIndex)) {
            this.elements.correctorSelected.textContent = 'Pick a word from the transcript to begin.';
            if (this.elements.correctorContext) {
                this.elements.correctorContext.textContent = '';
            }
            if (this.elements.correctorFlags) {
                this.elements.correctorFlags.innerHTML = '';
            }
            this.elements.correctorInput.value = '';
            this.elements.correctorInput.disabled = true;
            if (this.elements.saveCorrectionBtn) {
                this.elements.saveCorrectionBtn.disabled = true;
            }
            if (this.elements.clearCorrectionBtn) {
                this.elements.clearCorrectionBtn.disabled = true;
            }
            return;
        }

        const word = this.wordsByIndex.get(this.selectedWordIndex);
        const corrected = this.corrections.get(word.index) || '';
        const display = corrected || word.word;
        const contextBefore = word.context_before ?? '';
        const contextAfter = word.context_after ?? '';
        const speakerName = word.speaker ? (this.speakerNames.get(word.speaker) || `Speaker ${word.speaker}`) : 'Unknown speaker';
        const confidence = typeof word.confidence === 'number' ? `${(word.confidence * 100).toFixed(1)}%` : '--';
        const timeRange = word.start_time !== null && word.start_time !== undefined
            ? `${this.formatTime(word.start_time)}${word.end_time !== null && word.end_time !== undefined ? ` – ${this.formatTime(word.end_time)}` : ''}`
            : 'No timestamp';

        this.elements.correctorSelected.innerHTML = `
            <strong>${display}</strong>
            <span>${speakerName}</span>
            <span>Confidence: ${confidence} • ${timeRange}</span>
        `;

        if (this.elements.correctorContext) {
            this.elements.correctorContext.innerHTML = `
                <span class="before">${contextBefore}</span>
                <span class="current">${display}</span>
                <span class="after">${contextAfter}</span>
            `;
        }

        if (this.elements.correctorFlags) {
            if (word.flags && word.flags.length) {
                this.elements.correctorFlags.innerHTML = word.flags
                    .map(flag => `<span class="flag-chip priority-${flag.priority}">${flag.type.replace(/_/g, ' ')}</span>`)
                    .join('');
            } else {
                this.elements.correctorFlags.innerHTML = '';
            }
        }

        this.elements.correctorInput.disabled = false;
        this.elements.correctorInput.value = corrected || word.word;
        this.updateCorrectorButtons();
    }

    updateCorrectorButtons() {
        if (!this.elements.correctorInput) {
            return;
        }

        const saveBtn = this.elements.saveCorrectionBtn;
        const clearBtn = this.elements.clearCorrectionBtn;

        if (this.selectedWordIndex === null || !this.wordsByIndex.has(this.selectedWordIndex)) {
            if (saveBtn) saveBtn.disabled = true;
            if (clearBtn) clearBtn.disabled = true;
            return;
        }

        const word = this.wordsByIndex.get(this.selectedWordIndex);
        const currentValue = (this.elements.correctorInput.value || '').trim();
        const baseline = word.word || '';
        const existing = this.corrections.get(word.index) || '';
        const hasText = currentValue.length > 0;
        const isDifferent = currentValue !== (existing || baseline);

        if (saveBtn) {
            saveBtn.disabled = !(hasText && isDifferent);
        }

        if (clearBtn) {
            clearBtn.disabled = !this.corrections.has(word.index);
        }
    }

    applyCorrection(word, newValue) {
        if (!word) {
            return;
        }

        const trimmed = (newValue ?? '').trim();
        const baseline = word.word || '';

        if (!trimmed || trimmed === baseline) {
            if (this.corrections.has(word.index)) {
                this.corrections.delete(word.index);
                this.showToast('Correction removed.');
            } else {
                this.showToast('No changes applied.');
            }
        } else {
            this.corrections.set(word.index, trimmed);
            this.showToast('Correction captured.');
        }

        this.updateStats();
        this.renderFilteredWords();
        this.renderTranscriptLines();
        this.setSelectedWord(word.index, { focusInput: true, scrollLine: false, scrollWordCard: false, forceRender: true });
    }

    getConfidenceClass(confidence) {
        if (confidence === null || confidence === undefined) return 'badge';
        if (confidence >= 0.9) return 'badge confidence-high';
        if (confidence >= 0.7) return 'badge confidence-medium';
        return 'badge confidence-low';
    }

    getHighestPriority(flags = []) {
        if (!flags.length) return null;
        if (flags.some(flag => flag.priority === 'high')) return 'high';
        if (flags.some(flag => flag.priority === 'medium')) return 'medium';
        if (flags.some(flag => flag.priority === 'low')) return 'low';
        return null;
    }

    seekToWord(word) {
        if (this.elements.audioPlayer.src && word.start_time !== null && word.start_time !== undefined) {
            this.elements.audioPlayer.currentTime = word.start_time;
            this.elements.audioPlayer.play();
        }
        this.setSelectedWord(word.index, {
            focusInput: false,
            scrollWordCard: true,
            scrollLine: this.activeTranscriptView === 'lines'
        });
    }

    highlightWordCard(index, options = {}) {
        const { scroll = false } = options;
        this.wordElements.forEach(card => card.classList.remove('current'));
        const card = this.wordElements.get(index);
        if (card) {
            card.classList.add('current');
            if (scroll) {
                card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }

    toggleApprove(word) {
        if (this.approvedWords.has(word.index)) {
            this.approvedWords.delete(word.index);
        } else {
            this.approvedWords.add(word.index);
        }
        this.renderFilteredWords();
        this.updateStats();
        this.showToast(`${word.word} ${this.approvedWords.has(word.index) ? 'approved' : 'unapproved'}.`);
    }

    toggleDictionary(word) {
        if (this.dictionaryTerms.has(word.word)) {
            this.dictionaryTerms.delete(word.word);
        } else {
            this.dictionaryTerms.add(word.word);
        }
        this.updateDictionaryList();
        this.renderFilteredWords();
        this.showToast(`${word.word} ${this.dictionaryTerms.has(word.word) ? 'added to' : 'removed from'} dictionary queue.`);
    }

    promptCorrection(word) {
        this.focusCorrector(word);
        this.showToast('Word loaded into the corrector pane.');
    }

    removeCorrection(word) {
        if (this.corrections.has(word.index)) {
            this.corrections.delete(word.index);
            this.updateStats();
            this.renderFilteredWords();
            this.renderTranscriptLines();
            this.setSelectedWord(word.index, { focusInput: true, scrollLine: false, scrollWordCard: false, forceRender: true });
            this.showToast('Correction removed.');
        }
    }

    updateDictionaryList() {
        this.elements.dictCount.textContent = this.dictionaryTerms.size;
        if (!this.dictionaryTerms.size) {
            this.elements.dictionaryList.innerHTML = '<div class="empty-state">No terms queued yet.</div>';
            return;
        }

        this.elements.dictionaryList.innerHTML = '';
        Array.from(this.dictionaryTerms).sort().forEach(term => {
            const item = document.createElement('div');
            item.className = 'dictionary-item';
            item.innerHTML = `<span>${term}</span><button class="ghost-btn" data-term="${term}">Remove</button>`;
            item.querySelector('button').addEventListener('click', () => {
                this.dictionaryTerms.delete(term);
                this.updateDictionaryList();
                this.renderFilteredWords();
            });
            this.elements.dictionaryList.appendChild(item);
        });
    }

    exportCorrections() {
        if (!this.corrections.size) {
            this.showToast('No corrections to export.');
            return;
        }

        const payload = Array.from(this.corrections.entries()).map(([index, newValue]) => ({ index, original: this.words.find(w => w.index === index)?.word, correction: newValue }));
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
        this.downloadBlob(blob, 'review_corrections.json');
        this.showToast('Corrections exported.');
    }

    exportCorrectedTranscript() {
        if (!this.words.length) {
            this.showToast('Load a review before exporting.');
            return;
        }

        const transcript = this.words.map(word => this.corrections.get(word.index) || word.word).join(' ');
        const blob = new Blob([transcript], { type: 'text/plain' });
        this.downloadBlob(blob, 'corrected_transcript.txt');
        this.showToast('Corrected transcript exported.');
    }

    saveReviewSnapshot() {
        if (!this.reviewData) {
            this.showToast('Load a review before saving.');
            return;
        }

        const snapshot = {
            ...this.reviewData,
            corrections: Array.from(this.corrections.entries()).map(([index, newValue]) => ({ index, newValue })),
            approved_words: Array.from(this.approvedWords),
            dictionary_queue: Array.from(this.dictionaryTerms)
        };

        const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json' });
        this.downloadBlob(blob, 'review_snapshot.json');
        this.showToast('Review snapshot saved.');
    }

    exportDictionaryTerms() {
        if (!this.dictionaryTerms.size) {
            this.showToast('Dictionary queue is empty.');
            return;
        }
        const payload = Array.from(this.dictionaryTerms).join('\n');
        const blob = new Blob([payload], { type: 'text/plain' });
        this.downloadBlob(blob, 'dictionary_queue.txt');
        this.showToast('Dictionary exported.');
    }

    downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    highlightConfidenceThreshold(threshold) {
        if (Number.isNaN(threshold)) {
            return;
        }

        this.confidenceThreshold = threshold;

        this.wordElements.forEach((card, index) => {
            const word = this.wordsByIndex.get(index);
            if (!word) return;
            card.classList.toggle('confidence-low', typeof word.confidence === 'number' && word.confidence < threshold);
        });

        this.lineWordElements.forEach((element, index) => {
            const word = this.wordsByIndex.get(index);
            if (!word) return;
            element.classList.toggle('confidence-low', typeof word.confidence === 'number' && word.confidence < threshold);
        });

        this.updateLineConfidenceStates(threshold);
    }

    async handleAudioFile(file) {
        const url = URL.createObjectURL(file);
        this.elements.audioPlayer.src = url;
        this.showToast(`Audio loaded: ${file.name}`);

        if (!window.AudioContext) return;

        const arrayBuffer = await file.arrayBuffer();
        const audioContext = new AudioContext();
        this.audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        this.drawWaveform();
    }

    drawWaveform() {
        const canvas = this.elements.waveformCanvas;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, rect.width, rect.height);

        const hasTiming = Array.from(this.wordMap.values()).length > 0;
        const duration = hasTiming ? Math.max(...Array.from(this.wordMap.values()).map(w => w.end || 0)) : (this.elements.audioPlayer.duration || 0);

        if (this.audioBuffer) {
            const waveformPoints = this.getWaveformFromAudioBuffer(this.audioBuffer, rect.width);
            this.renderWaveform(ctx, waveformPoints, rect.width, rect.height, duration);
        } else if (hasTiming) {
            const waveformPoints = this.buildWaveformFromWords(rect.width, duration);
            this.renderWaveform(ctx, waveformPoints, rect.width, rect.height, duration);
        } else {
            ctx.fillStyle = 'rgba(96, 165, 250, 0.2)';
            ctx.fillRect(0, rect.height / 2 - 10, rect.width, 20);
        }

        this.waveformData = { width: rect.width, height: rect.height, duration };
    }

    getWaveformFromAudioBuffer(buffer, width) {
        const rawData = buffer.getChannelData(0);
        const blockSize = Math.floor(rawData.length / width);
        const samples = [];
        for (let i = 0; i < width; i++) {
            let sum = 0;
            for (let j = 0; j < blockSize; j++) {
                sum += Math.abs(rawData[i * blockSize + j]);
            }
            samples.push(sum / blockSize);
        }
        return this.smoothWaveform(samples);
    }

    buildWaveformFromWords(width, duration) {
        const points = [];
        for (let x = 0; x < width; x++) {
            const time = (x / width) * duration;
            const wordsInRange = Array.from(this.wordMap.values()).filter(w => w.start <= time && w.end >= time);
            if (!wordsInRange.length) {
                points.push(0.1);
                continue;
            }
            const avgConfidence = wordsInRange.reduce((sum, item) => sum + (item.word.confidence || 0.5), 0) / wordsInRange.length;
            points.push(avgConfidence);
        }
        return this.smoothWaveform(points);
    }

    smoothWaveform(points) {
        const kernel = [0.06, 0.24, 0.4, 0.24, 0.06];
        const half = Math.floor(kernel.length / 2);
        return points.map((_, idx) => {
            let sum = 0;
            let weight = 0;
            kernel.forEach((value, kIdx) => {
                const sampleIndex = idx - half + kIdx;
                if (sampleIndex >= 0 && sampleIndex < points.length) {
                    sum += points[sampleIndex] * value;
                    weight += value;
                }
            });
            return sum / weight;
        });
    }

    renderWaveform(ctx, points, width, height, duration) {
        const center = height / 2;
        const maxHeight = (height - 40) / 2;

        ctx.save();
        const gradient = ctx.createLinearGradient(0, center - maxHeight, 0, center + maxHeight);
        gradient.addColorStop(0, '#60a5fa');
        gradient.addColorStop(1, '#2563eb');
        ctx.fillStyle = gradient;

        const barWidth = Math.max(1, width / points.length);
        points.forEach((point, idx) => {
            const x = idx * barWidth;
            const barHeight = Math.max(2, point * maxHeight);
            ctx.fillRect(x, center - barHeight, barWidth * 0.9, barHeight * 2);
        });
        ctx.restore();

        ctx.fillStyle = 'rgba(148,163,184,0.7)';
        ctx.font = '10px "Inter", sans-serif';
        ctx.textAlign = 'center';
        const markers = Math.min(8, Math.floor(duration));
        for (let i = 0; i <= markers; i++) {
            const time = (i / markers) * duration;
            const x = (time / duration) * width;
            ctx.fillText(this.formatTime(time), x, height - 8);
            ctx.strokeStyle = 'rgba(148,163,184,0.15)';
            ctx.beginPath();
            ctx.moveTo(x, height - 35);
            ctx.lineTo(x, height - 20);
            ctx.stroke();
        }
    }

    animateWaveformCursor() {
        const draw = () => {
            if (!this.waveformData) return;
            this.drawWaveform();
            const ctx = this.elements.waveformCanvas.getContext('2d');
            const { width, height, duration } = this.waveformData;
            const time = this.elements.audioPlayer.currentTime;
            const x = duration ? (time / duration) * width : 0;
            ctx.strokeStyle = '#facc15';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
            this.animationFrame = requestAnimationFrame(draw);
        };
        this.stopWaveformCursor();
        this.animationFrame = requestAnimationFrame(draw);
    }

    stopWaveformCursor() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
            this.animationFrame = null;
        }
    }

    seekFromWaveform(event) {
        if (!this.waveformData) return;
        const rect = this.elements.waveformCanvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const { duration, width } = this.waveformData;
        const ratio = x / width;
        if (this.elements.audioPlayer.duration) {
            this.elements.audioPlayer.currentTime = ratio * this.elements.audioPlayer.duration;
            this.elements.audioPlayer.play();
        }
    }

    handleAudioTimeUpdate() {
        const currentTime = this.elements.audioPlayer.currentTime;
        this.elements.currentTime.textContent = this.formatTime(currentTime);
        const matching = Array.from(this.wordMap.values()).find(word => word.start <= currentTime && word.end >= currentTime);
        let targetWord = matching?.word;
        if (!targetWord) {
            targetWord = this.words.find(word => {
                if (word.start_time === null || word.start_time === undefined || word.end_time === null || word.end_time === undefined) {
                    return false;
                }
                return word.start_time <= currentTime && word.end_time >= currentTime;
            });
        }

        if (targetWord) {
            this.setSelectedWord(targetWord.index, {
                focusInput: false,
                scrollWordCard: this.activeTranscriptView === 'words',
                scrollLine: this.activeTranscriptView === 'lines'
            });
            if (targetWord.confidence !== null && targetWord.confidence !== undefined) {
                this.elements.confidenceScore.textContent = `Confidence: ${(targetWord.confidence * 100).toFixed(1)}%`;
            }
        }
    }

    updateAudioDuration() {
        if (!isNaN(this.elements.audioPlayer.duration)) {
            this.elements.duration.textContent = this.formatTime(this.elements.audioPlayer.duration);
        }
    }

    formatTime(seconds) {
        if (!seconds && seconds !== 0) return '--';
        const total = Math.floor(seconds);
        const mins = Math.floor(total / 60);
        const secs = total % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    showToast(message) {
        if (!this.elements.toast) return;
        this.elements.toast.textContent = message;
        this.elements.toast.classList.add('show');
        clearTimeout(this.toastTimeout);
        this.toastTimeout = setTimeout(() => {
            this.elements.toast.classList.remove('show');
        }, 2600);
    }

    async loadDemoReview(playAudio = false) {
        this.reviewData = JSON.parse(JSON.stringify(DEMO_REVIEW));
        this.initializeStateFromReview();
        this.showToast('Demo call loaded. Upload your own review to go deeper.');

        if (playAudio) {
            // Generate a soft tone demo audio for experience
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const duration = 5;
                const sampleRate = audioContext.sampleRate;
                const buffer = audioContext.createBuffer(1, sampleRate * duration, sampleRate);
                const channelData = buffer.getChannelData(0);
                for (let i = 0; i < channelData.length; i++) {
                    channelData[i] = Math.sin((2 * Math.PI * 440 * i) / sampleRate) * Math.exp(-i / (sampleRate * 1.5));
                }
                const wavDataUrl = this.audioBufferToWav(buffer);
                this.elements.audioPlayer.src = wavDataUrl;
                this.elements.audioPlayer.play();
            } catch (error) {
                console.warn('Demo audio unsupported', error);
            }
        }
    }

    audioBufferToWav(buffer) {
        const numOfChan = buffer.numberOfChannels;
        const btwLength = buffer.length * numOfChan * 2 + 44;
        const btw = new ArrayBuffer(btwLength);
        const vw = new DataView(btw);
        const channels = [];
        let sample;
        let offset = 0;
        let pos = 0;

        const writeUTFBytes = (view, offset, string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };

        writeUTFBytes(vw, 0, 'RIFF');
        vw.setUint32(4, 36 + buffer.length * numOfChan * 2, true);
        writeUTFBytes(vw, 8, 'WAVE');
        writeUTFBytes(vw, 12, 'fmt ');
        vw.setUint32(16, 16, true);
        vw.setUint16(20, 1, true);
        vw.setUint16(22, numOfChan, true);
        vw.setUint32(24, buffer.sampleRate, true);
        vw.setUint32(28, buffer.sampleRate * numOfChan * 2, true);
        vw.setUint16(32, numOfChan * 2, true);
        vw.setUint16(34, 16, true);
        writeUTFBytes(vw, 36, 'data');
        vw.setUint32(40, buffer.length * numOfChan * 2, true);

        for (let i = 0; i < buffer.numberOfChannels; i++) {
            channels.push(buffer.getChannelData(i));
        }

        while (pos < buffer.length) {
            for (let i = 0; i < numOfChan; i++) {
                sample = Math.max(-1, Math.min(1, channels[i][pos]));
                vw.setInt16(44 + offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
                offset += 2;
            }
            pos++;
        }

        return URL.createObjectURL(new Blob([vw], { type: 'audio/wav' }));
    }

    rebuildFromConfidence() {
        if (this.reviewData?.wordsFromConfidence) {
            const originalConfidence = this.reviewData.wordsFromConfidence;
            this.reviewData = this.buildReviewFromConfidence(originalConfidence);
            this.reviewData.wordsFromConfidence = originalConfidence;
            this.initializeStateFromReview();
        }
    }

    editSpeakerNames() {
        if (!this.words.length) {
            this.showToast('Load a transcript to edit speakers.');
            return;
        }

        const speakers = Array.from(new Set(this.words.map(w => w.speaker).filter(Boolean)));
        speakers.forEach(speaker => {
            const current = this.speakerNames.get(speaker) || `Speaker ${speaker}`;
            const response = window.prompt(`Rename ${current}`, current);
            if (response && response.trim()) {
                this.speakerNames.set(speaker, response.trim());
            }
        });
        this.renderFilteredWords();
        this.renderTranscriptLines();
        this.setSelectedWord(this.selectedWordIndex, { forceRender: true });
    }
}

new AssemblyAIReviewStudio();
