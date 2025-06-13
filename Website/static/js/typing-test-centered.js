class TypingTest {
    constructor() {
        this.words = [];
        this.currentWordIndex = 0;
        this.currentCharIndex = 0;
        this.startTime = null;
        this.endTime = null;
        this.isActive = false;
        this.isPaused = false;
        this.errors = 0;
        this.totalChars = 0;
        this.correctChars = 0;
        this.testDuration = 60;
        this.timeLeft = this.testDuration;
        this.timer = null;
        this.difficulty = 'medium';
        this.keystrokes = [];
        this.wpmHistory = [];
        this.errorPatterns = {};
        this.currentInput = '';
        
        this.initializeElements();
        this.setupEventListeners();
        this.loadWords();
    }

    initializeElements() {
        this.wordsDisplay = document.getElementById('words-display');
        this.wordsContainer = document.getElementById('words-container');
        this.typingInput = document.getElementById('typing-input');
        this.testArea = document.getElementById('test-area');
        this.wpmDisplay = document.getElementById('wpm-display');
        this.accuracyDisplay = document.getElementById('accuracy-display');
        this.timeDisplay = document.getElementById('time-display');
        this.errorsDisplay = document.getElementById('errors-display');
        this.progressFill = document.getElementById('progress-fill');
        this.resultsModal = document.getElementById('results-modal');
        this.restartBtn = document.getElementById('restart-btn');
        this.pauseBtn = document.getElementById('pause-btn');
    }

    setupEventListeners() {
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelector('.difficulty-btn.active').classList.remove('active');
                btn.classList.add('active');
                this.difficulty = btn.dataset.difficulty;
                this.loadWords();
                this.addButtonClickEffect(btn);
            });
        });

        this.testArea.addEventListener('click', () => {
            this.typingInput.focus();
            if (!this.isActive && !this.isPaused) {
                this.startTest();
            }
        });

        this.typingInput.addEventListener('input', (e) => {
            if (!this.isActive) return;
            this.handleTyping(e.target.value);
        });

        this.typingInput.addEventListener('keydown', (e) => {
            if (!this.isActive) return;
            
            if (e.key === ' ') {
                e.preventDefault();
                this.completeCurrentWord();
            }
            
            if (e.key === 'Backspace') {
                this.handleBackspace();
            }
        });

        this.restartBtn.addEventListener('click', () => {
            this.resetTest();
            this.addButtonClickEffect(this.restartBtn);
        });

        this.pauseBtn.addEventListener('click', () => {
            this.togglePause();
            this.addButtonClickEffect(this.pauseBtn);
        });

        document.getElementById('test-again-btn').addEventListener('click', () => {
            this.hideResults();
            this.resetTest();
        });

        document.getElementById('view-stats-btn').addEventListener('click', () => {
            window.location.href = '/stats';
        });

        this.resultsModal.addEventListener('click', (e) => {
            if (e.target === this.resultsModal) {
                this.hideResults();
            }
        });
    }

    addButtonClickEffect(button) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 150);
    }

    async loadWords() {
        try {
            this.showLoadingState();
            
            const urlParams = new URLSearchParams(window.location.search);
            const lessonType = urlParams.get('lesson');
            
            let apiUrl;
            if (lessonType) {
                apiUrl = `/api/lessons`;
            } else {
                apiUrl = `/api/get_words?difficulty=${this.difficulty}&count=300`;
            }
            
            const response = await fetch(apiUrl);
            const data = await response.json();
            
            if (lessonType && data.lessons && data.lessons[lessonType]) {
                this.words = data.lessons[lessonType].words;
            } else {
                this.words = data.words;
            }
            
            this.renderWords();
            this.hideLoadingState();
        } catch (error) {
            console.error('Error loading words:', error);
            this.words = [
                'the', 'quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog', 'and', 'runs', 'away', 'fast',
                'computer', 'keyboard', 'typing', 'practice', 'skills', 'improve', 'speed', 'accuracy',
                'programming', 'development', 'software', 'hardware', 'network', 'internet', 'website',
                'function', 'variable', 'algorithm', 'structure', 'database', 'framework', 'library',
                'beautiful', 'amazing', 'wonderful', 'fantastic', 'incredible', 'outstanding', 'excellent',
                'challenge', 'achievement', 'success', 'progress', 'learning', 'education', 'knowledge'
            ];
            this.renderWords();
            this.hideLoadingState();
        }
    }

    showLoadingState() {
        this.wordsDisplay.innerHTML = '<div class="loading">Loading words...</div>';
    }

    hideLoadingState() {
    }

    renderWords() {
        if (this.words.length === 0) return;
        
        const wordsToShow = [];
        const wordsBeforeCurrent = 3;
        const wordsAfterCurrent = 3;
        
        for (let i = Math.max(0, this.currentWordIndex - wordsBeforeCurrent); i < this.currentWordIndex; i++) {
            wordsToShow.push({
                word: this.words[i],
                index: i,
                type: 'completed'
            });
        }
        
        if (this.currentWordIndex < this.words.length) {
            wordsToShow.push({
                word: this.words[this.currentWordIndex],
                index: this.currentWordIndex,
                type: 'current'
            });
        }
        
        for (let i = this.currentWordIndex + 1; i <= Math.min(this.words.length - 1, this.currentWordIndex + wordsAfterCurrent); i++) {
            wordsToShow.push({
                word: this.words[i],
                index: i,
                type: 'upcoming'
            });
        }
        
        let html = '';
        wordsToShow.forEach(wordObj => {
            html += `<span class="word ${wordObj.type}" data-word-index="${wordObj.index}">`;
            
            for (let charIndex = 0; charIndex < wordObj.word.length; charIndex++) {
                const char = wordObj.word[charIndex];
                let charClass = this.getCharClass(wordObj.index, charIndex);
                html += `<span class="char ${charClass}" data-word-index="${wordObj.index}" data-char-index="${charIndex}">${char}</span>`;
            }
            
            html += '</span>';
        });
        
        this.wordsDisplay.innerHTML = html;
        
        setTimeout(() => this.centerCurrentWord(), 10);
    }
    
    centerCurrentWord() {
        const container = this.wordsContainer;
        const currentWord = this.wordsDisplay.querySelector('.word.current');
        
        if (currentWord && container) {
            const containerCenter = container.offsetWidth / 2;
            const currentWordLeft = currentWord.offsetLeft;
            const currentWordWidth = currentWord.offsetWidth;
            const currentWordCenter = currentWordLeft + (currentWordWidth / 2);
            
            const offset = containerCenter - currentWordCenter;
            
            this.wordsDisplay.style.transform = `translateX(${offset}px)`;
        }
    }

    getCharClass(wordIndex, charIndex) {
        if (wordIndex < this.currentWordIndex) {
            const keystroke = this.getKeystrokeForPosition(wordIndex, charIndex);
            if (keystroke && keystroke.correct === true) {
                return 'correct';
            } else if (keystroke && keystroke.correct === false) {
                return 'incorrect';
            }
            return 'correct';
        } else if (wordIndex === this.currentWordIndex) {
            if (charIndex < this.currentCharIndex) {
                const keystroke = this.getKeystrokeForPosition(wordIndex, charIndex);
                if (keystroke && keystroke.correct === true) {
                    return 'correct';
                } else if (keystroke && keystroke.correct === false) {
                    return 'incorrect';
                }
                return 'pending';
            } else if (charIndex === this.currentCharIndex) {
                return 'current';
            }
        }
        return 'pending';
    }

    getKeystrokeForPosition(wordIndex, charIndex) {
        let position = 0;
        for (let i = 0; i < wordIndex; i++) {
            position += this.words[i].length;
        }
        position += charIndex;
        
        return this.keystrokes[position] || null;
    }

    startTest() {
        this.isActive = true;
        this.startTime = Date.now();
        this.testArea.classList.add('active');
        this.typingInput.focus();
        this.currentInput = '';
        
        this.timer = setInterval(() => {
            this.timeLeft--;
            this.timeDisplay.textContent = this.timeLeft;
            
            this.wpmHistory.push({
                time: this.testDuration - this.timeLeft,
                wpm: this.calculateWPM()
            });
            
            if (this.timeLeft <= 0) {
                this.endTest();
            }
        }, 1000);

        this.testArea.style.boxShadow = '0 0 20px rgba(255, 255, 255, 0.1)';
    }

    handleTyping(inputValue) {
        if (!this.isActive) return;

        this.currentInput = inputValue;
        
        const currentWord = this.words[this.currentWordIndex];
        if (!currentWord) return;
        
        this.clearCurrentWordClasses();
        
        for (let i = 0; i < inputValue.length && i < currentWord.length; i++) {
            const typedChar = inputValue[i];
            const expectedChar = currentWord[i];
            
            if (i >= this.currentCharIndex) {
                this.totalChars++;
                
                if (typedChar === expectedChar) {
                    this.correctChars++;
                    this.markCharacterCorrect(i);
                    
                    this.keystrokes.push({
                        position: this.getGlobalPosition(this.currentWordIndex, i),
                        correct: true,
                        timestamp: Date.now()
                    });
                } else {
                    this.errors++;
                    this.markCharacterIncorrect(i);
                    this.trackErrorPattern(expectedChar, typedChar);
                    
                    this.keystrokes.push({
                        position: this.getGlobalPosition(this.currentWordIndex, i),
                        correct: false,
                        timestamp: Date.now()
                    });
                    
                    this.addErrorEffect();
                }
                
                this.currentCharIndex = i + 1;
            }
        }
        
        if (inputValue.length > currentWord.length) {
            this.handleExtraCharacters(inputValue.substring(currentWord.length));
        }
        
        this.updateStats();
    }

    clearCurrentWordClasses() {
        const currentWordElement = document.querySelector(`[data-word-index="${this.currentWordIndex}"]`);
        if (currentWordElement) {
            const chars = currentWordElement.querySelectorAll('.char');
            chars.forEach(char => {
                char.classList.remove('correct', 'incorrect', 'current');
                char.classList.add('pending');
            });
        }
    }

    markCharacterCorrect(charIndex) {
        const charElement = document.querySelector(
            `[data-word-index="${this.currentWordIndex}"][data-char-index="${charIndex}"]`
        );
        if (charElement) {
            charElement.classList.remove('incorrect', 'current', 'pending');
            charElement.classList.add('correct');
        }
    }

    markCharacterIncorrect(charIndex) {
        const charElement = document.querySelector(
            `[data-word-index="${this.currentWordIndex}"][data-char-index="${charIndex}"]`
        );
        if (charElement) {
            charElement.classList.remove('correct', 'current', 'pending');
            charElement.classList.add('incorrect');
        }
    }

    handleExtraCharacters(extraChars) {
        for (let char of extraChars) {
            this.errors++;
            this.totalChars++;
            this.addErrorEffect();
        }
    }

    completeCurrentWord() {
        const currentWord = this.words[this.currentWordIndex];
        if (!currentWord) return;
        
        while (this.currentCharIndex < currentWord.length) {
            this.errors++;
            this.totalChars++;
            this.markCharacterIncorrect(this.currentCharIndex);
            this.currentCharIndex++;
        }
        
        this.advanceToNextWord();
    }

    advanceToNextWord() {
        this.currentWordIndex++;
        this.currentCharIndex = 0;
        this.currentInput = '';
        this.typingInput.value = '';
        
        if (this.currentWordIndex >= this.words.length) {
            this.endTest();
            return;
        }
        
        this.renderWords();
    }

    handleBackspace() {
        if (this.currentCharIndex > 0) {
            this.currentCharIndex--;
            this.currentInput = this.currentInput.slice(0, -1);
            this.typingInput.value = this.currentInput;
            this.renderWords();
        }
    }

    getGlobalPosition(wordIndex, charIndex) {
        let position = 0;
        for (let i = 0; i < wordIndex; i++) {
            position += this.words[i].length;
        }
        position += charIndex;
        return position;
    }

    addErrorEffect() {
        this.testArea.style.animation = 'shake 0.3s ease-in-out';
        setTimeout(() => {
            this.testArea.style.animation = '';
        }, 300);
    }

    trackErrorPattern(expected, typed) {
        const pattern = `${expected}->${typed}`;
        this.errorPatterns[pattern] = (this.errorPatterns[pattern] || 0) + 1;
    }

    calculateWPM() {
        if (!this.startTime) return 0;
        const timeElapsed = (Date.now() - this.startTime) / 1000 / 60;
        const wordsTyped = this.correctChars / 5;
        return Math.round(wordsTyped / timeElapsed) || 0;
    }

    calculateAccuracy() {
        if (this.totalChars === 0) return 100;
        return Math.round((this.correctChars / this.totalChars) * 100);
    }

    updateStats() {
        const currentWPM = this.calculateWPM();
        const currentAccuracy = this.calculateAccuracy();
        
        this.wpmDisplay.textContent = currentWPM;
        this.accuracyDisplay.textContent = currentAccuracy + '%';
        this.errorsDisplay.textContent = this.errors;
        
        this.updateProgress();
    }

    updateProgress() {
        const progress = (this.currentWordIndex / this.words.length) * 100;
        this.progressFill.style.width = progress + '%';
    }

    togglePause() {
        if (this.isPaused) {
            this.resumeTest();
        } else {
            this.pauseTest();
        }
    }

    pauseTest() {
        this.isPaused = true;
        this.isActive = false;
        clearInterval(this.timer);
        this.pauseBtn.textContent = 'Resume';
        this.testArea.classList.remove('active');
        this.testArea.style.boxShadow = 'none';
    }

    resumeTest() {
        this.isPaused = false;
        this.isActive = true;
        this.pauseBtn.textContent = 'Pause';
        this.testArea.classList.add('active');
        this.typingInput.focus();
        
        this.timer = setInterval(() => {
            this.timeLeft--;
            this.timeDisplay.textContent = this.timeLeft;
            
            if (this.timeLeft <= 0) {
                this.endTest();
            }
        }, 1000);
    }

    async endTest() {
        this.isActive = false;
        this.endTime = Date.now();
        clearInterval(this.timer);
        this.testArea.classList.remove('active');
        this.testArea.style.boxShadow = 'none';

        const finalWPM = this.calculateWPM();
        const finalAccuracy = this.calculateAccuracy();
        const testDuration = Math.round((this.endTime - this.startTime) / 1000);
        const wordsTyped = this.currentWordIndex;

        try {
            const response = await fetch('/api/save_result', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    wpm: finalWPM,
                    accuracy: finalAccuracy,
                    duration: testDuration,
                    words_typed: wordsTyped,
                    errors: this.errors,
                    difficulty: this.difficulty,
                    keystrokes: this.keystrokes,
                    error_patterns: this.errorPatterns,
                    wpm_history: this.wpmHistory
                })
            });

            const result = await response.json();
            this.showResults(finalWPM, finalAccuracy, testDuration, result.achievements || []);
        } catch (error) {
            console.error('Error saving results:', error);
            this.showResults(finalWPM, finalAccuracy, testDuration, []);
        }
    }

    showResults(wpm, accuracy, duration, achievements) {
        document.getElementById('final-wpm').textContent = wpm;
        document.getElementById('final-accuracy').textContent = accuracy + '%';
        document.getElementById('final-time').textContent = duration + 's';
        document.getElementById('final-errors').textContent = this.errors;
        
        if (achievements.length > 0) {
            const achievementsDiv = document.getElementById('achievements-unlocked');
            const achievementsList = document.getElementById('achievement-list');
            achievementsList.innerHTML = achievements.map(achId => {
                const ach = window.ACHIEVEMENTS && window.ACHIEVEMENTS[achId];
                return ach ? `<span class="achievement">${ach.icon} ${ach.name}</span>` : '';
            }).join('');
            achievementsDiv.style.display = 'block';
        }
        
        this.resultsModal.style.display = 'flex';
        
        if (wpm >= 60 && accuracy >= 95) {
            this.addCelebrationEffect();
        }
    }

    addCelebrationEffect() {
        for (let i = 0; i < 30; i++) {
            setTimeout(() => {
                this.createConfetti();
            }, i * 50);
        }
    }

    createConfetti() {
        const confetti = document.createElement('div');
        confetti.style.position = 'fixed';
        confetti.style.width = '8px';
        confetti.style.height = '8px';
        confetti.style.backgroundColor = '#ffffff';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.top = '-10px';
        confetti.style.zIndex = '9999';
        confetti.style.pointerEvents = 'none';
        
        document.body.appendChild(confetti);
        
        const animation = confetti.animate([
            { transform: 'translateY(0) rotate(0deg)', opacity: 1 },
            { transform: `translateY(100vh) rotate(360deg)`, opacity: 0 }
        ], {
            duration: 2000,
            easing: 'ease-out'
        });
        
        animation.onfinish = () => confetti.remove();
    }

    hideResults() {
        this.resultsModal.style.display = 'none';
    }

    resetTest() {
        this.isActive = false;
        this.isPaused = false;
        this.currentWordIndex = 0;
        this.currentCharIndex = 0;
        this.errors = 0;
        this.totalChars = 0;
        this.correctChars = 0;
        this.timeLeft = this.testDuration;
        this.startTime = null;
        this.endTime = null;
        this.keystrokes = [];
        this.wpmHistory = [];
        this.currentInput = '';
        
        clearInterval(this.timer);
        
        this.timeDisplay.textContent = this.testDuration;
        this.wpmDisplay.textContent = '0';
        this.accuracyDisplay.textContent = '100%';
        this.errorsDisplay.textContent = '0';
        this.progressFill.style.width = '0%';
        this.pauseBtn.textContent = 'Pause';
        this.testArea.classList.remove('active');
        this.testArea.style.boxShadow = 'none';
        this.typingInput.value = '';
        
        this.loadWords();
        this.hideResults();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.typingTest = new TypingTest();
});
