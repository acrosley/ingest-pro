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
        this.audioBuffer = null;
        this.waveformData = null;
        this.animationFrame = null;
        this.enableGreenHighlight = true;
        this.currentFilters = {
            priority: 'all',
            type: 'all',
            flaggedOnly: true,
            search: ''
        };

        this.elements = {};

        this.initializeElements();
        this.bindEvents();
        this.loadDemoReview();
    }

    initializeElements() {
        this.elements.reviewFile = document.getElementById('reviewFile');
        this.elements.audioFile = document.getElementById('audioFile');
        this.elements.demoBtn = document.getElementById('demoBtn');
        this.elements.statsGrid = document.getElementById('statsGrid');
        this.elements.wordList = document.getElementById('wordList');
        this.elements.filterPriority = document.getElementById('filterPriority');
        this.elements.filterType = document.getElementById('filterType');
        this.elements.showOnlyFlagged = document.getElementById('showOnlyFlagged');
        this.elements.enableGreenHighlight = document.getElementById('enableGreenHighlight');
        this.elements.searchInput = document.getElementById('searchInput');
        this.elements.threshold = document.getElementById('confidenceThreshold');
        this.elements.thresholdValue = document.getElementById('thresholdValue');
        this.elements.dictionaryList = document.getElementById('dictionaryList');
        this.elements.dictCount = document.getElementById('dictCount');
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

        this.elements.threshold.addEventListener('input', () => {
            const value = parseFloat(this.elements.threshold.value);
            this.elements.thresholdValue.textContent = `${Math.round(value * 100)}%`;
            this.highlightConfidenceThreshold(value);
        });

        this.elements.exportCorrectionsBtn.addEventListener('click', () => this.exportCorrections());
        this.elements.exportTranscriptBtn.addEventListener('click', () => this.exportCorrectedTranscript());
        this.elements.saveReviewBtn.addEventListener('click', () => this.saveReviewSnapshot());
        this.elements.exportDictionaryBtn.addEventListener('click', () => this.exportDictionaryTerms());
        this.elements.editSpeakersBtn.addEventListener('click', () => this.editSpeakerNames());

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

        this.words = Array.isArray(this.reviewData.words) ? [...this.reviewData.words] : [];
        this.corrections.clear();
        this.approvedWords = new Set();
        this.dictionaryTerms = new Set();
        this.wordElements.clear();
        this.wordMap.clear();
        this.wordsByIndex.clear();

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
        this.updateStats();
        this.renderFilteredWords();
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
            return;
        }

        const stats = this.reviewData.statistics || {};
        const totalWords = stats.total_words || this.words.length;
        const flaggedWords = stats.flagged_words ?? this.words.filter(w => w.flags && w.flags.length).length;
        const flagPercentage = stats.flag_percentage ?? (totalWords ? ((flaggedWords / totalWords) * 100).toFixed(1) : 0);
        const avgConfidence = stats.average_confidence;
        const highPriority = stats.priority_counts?.high ?? this.words.filter(w => (w.flags || []).some(f => f.priority === 'high')).length;

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
                <button data-action="correct">Apply Correction</button>
                ${correctedWord ? '<button data-action="remove" class="destructive">Remove Correction</button>' : ''}
            </div>
        `;

        card.querySelector('[data-action="play"]').addEventListener('click', () => this.seekToWord(word));
        card.querySelector('[data-action="approve"]').addEventListener('click', () => this.toggleApprove(word));
        card.querySelector('[data-action="dictionary"]').addEventListener('click', () => this.toggleDictionary(word));
        card.querySelector('[data-action="correct"]').addEventListener('click', () => this.promptCorrection(word));
        const removeBtn = card.querySelector('[data-action="remove"]');
        if (removeBtn) {
            removeBtn.addEventListener('click', () => this.removeCorrection(word));
        }

        if (word.start_time !== null) {
            card.querySelector('.context-block .current').addEventListener('click', () => this.seekToWord(word));
        }

        return card;
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
        if (this.elements.audioPlayer.src && word.start_time !== null) {
            this.elements.audioPlayer.currentTime = word.start_time;
            this.elements.audioPlayer.play();
        }
        this.highlightWordCard(word.index);
    }

    highlightWordCard(index) {
        this.wordElements.forEach(card => card.classList.remove('current'));
        const card = this.wordElements.get(index);
        if (card) {
            card.classList.add('current');
            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
        const existing = this.corrections.get(word.index) || word.suggested_correction || '';
        const suggestion = window.prompt('Enter corrected word or phrase', existing);
        if (suggestion && suggestion.trim()) {
            this.corrections.set(word.index, suggestion.trim());
            this.updateStats();
            this.renderFilteredWords();
            this.showToast('Correction captured.');
        }
    }

    removeCorrection(word) {
        if (this.corrections.has(word.index)) {
            this.corrections.delete(word.index);
            this.updateStats();
            this.renderFilteredWords();
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
        this.wordElements.forEach((card, index) => {
            const word = this.wordsByIndex.get(index);
            if (!word) return;
            card.classList.toggle('confidence-low', typeof word.confidence === 'number' && word.confidence < threshold);
        });
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
        if (matching) {
            this.highlightWordCard(matching.word.index);
            if (matching.word.confidence !== null && matching.word.confidence !== undefined) {
                this.elements.confidenceScore.textContent = `Confidence: ${(matching.word.confidence * 100).toFixed(1)}%`;
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
    }
}

new AssemblyAIReviewStudio();
