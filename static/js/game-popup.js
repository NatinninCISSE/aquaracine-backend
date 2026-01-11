/**
 * AQUA-RACINE GAME POPUP
 * Quiz + Wheel of Fortune Game
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        apiBase: '/api',
        showDelay: 3000, // Show popup after 3 seconds
        storageKey: 'aquaracine_game_shown',
        wheelSpinDuration: 4000,
    };

    // Wheel segments configuration (will be loaded from API)
    let WHEEL_SEGMENTS = [
        { label: '10%', color: '#4caf50', prize: 'discount', is_winning: true },
        { label: 'Perdu', color: '#f44336', prize: 'lost', is_winning: false },
        { label: '15%', color: '#2196f3', prize: 'discount', is_winning: true },
        { label: 'Perdu', color: '#ff9800', prize: 'lost', is_winning: false },
        { label: 'Livraison', color: '#9c27b0', prize: 'free_delivery', is_winning: true },
        { label: 'Perdu', color: '#e91e63', prize: 'lost', is_winning: false },
        { label: '20%', color: '#00bcd4', prize: 'discount', is_winning: true },
        { label: 'Perdu', color: '#795548', prize: 'lost', is_winning: false },
    ];

    // State
    let state = {
        currentStep: 'registration', // registration, quiz, score, wheel, result
        currentQuestionIndex: 0,
        questions: [],
        answers: {},
        userData: {},
        quizScore: 0,
        quizTotal: 4,
        scoreMessage: '',
        prize: null,
        promoCode: '',
    };

    // DOM Elements
    let popup, overlay;

    /**
     * Initialize the game
     */
    function init() {
        // Check if already shown in this session
        if (sessionStorage.getItem(CONFIG.storageKey)) {
            return;
        }

        // Create popup HTML
        createPopupHTML();

        // Get DOM elements
        popup = document.getElementById('game-popup');
        overlay = document.getElementById('game-popup-overlay');

        // Bind events
        bindEvents();

        // Show popup after delay
        setTimeout(showPopup, CONFIG.showDelay);
    }

    /**
     * Create popup HTML structure
     */
    function createPopupHTML() {
        const html = `
        <div class="game-popup-overlay" id="game-popup-overlay">
            <div class="game-popup" id="game-popup">
                <button class="game-popup-close" id="game-close-btn">&times;</button>

                <!-- Header -->
                <div class="game-popup-header">
                    <div class="gift-icon">🎁</div>
                    <h2>Tentez votre chance !</h2>
                    <p>Testez vos connaissances et gagnez des cadeaux</p>
                </div>

                <!-- Steps Indicator -->
                <div class="game-popup-body">
                    <div class="game-steps">
                        <div class="game-step active" data-step="registration">
                            <div class="game-step-icon">📝</div>
                            <span class="game-step-label">Inscription</span>
                        </div>
                        <div class="game-step" data-step="quiz">
                            <div class="game-step-icon">❓</div>
                            <span class="game-step-label">Quiz</span>
                        </div>
                        <div class="game-step" data-step="score">
                            <div class="game-step-icon">📊</div>
                            <span class="game-step-label">Score</span>
                        </div>
                        <div class="game-step" data-step="wheel">
                            <div class="game-step-icon">🎯</div>
                            <span class="game-step-label">Roue</span>
                        </div>
                    </div>

                    <!-- Error Message -->
                    <div class="game-error" id="game-error"></div>

                    <!-- Loading -->
                    <div class="game-loading" id="game-loading">
                        <div class="spinner"></div>
                        <p style="color: #fff;">Chargement...</p>
                    </div>

                    <!-- Registration Section -->
                    <div class="registration-section" id="registration-section">
                        <div class="game-form-group">
                            <label for="game-name">Votre nom complet</label>
                            <input type="text" id="game-name" placeholder="Ex: Jean Kouadio" required>
                        </div>
                        <div class="game-form-group">
                            <label for="game-email">Votre email</label>
                            <input type="email" id="game-email" placeholder="Ex: jean@example.com" required>
                        </div>
                        <div class="game-form-group">
                            <label for="game-phone">Votre telephone</label>
                            <input type="tel" id="game-phone" placeholder="Ex: 07 XX XX XX XX" required>
                        </div>
                        <button class="game-btn game-btn-primary" id="start-quiz-btn">
                            <span>Commencer le quiz</span>
                            <span>→</span>
                        </button>
                    </div>

                    <!-- Quiz Section -->
                    <div class="quiz-section" id="quiz-section">
                        <div class="quiz-progress" id="quiz-progress"></div>
                        <div class="quiz-question-card" id="quiz-card">
                            <div class="quiz-question-number" id="quiz-number">Question 1/4</div>
                            <div class="quiz-question-text" id="quiz-question"></div>
                            <div class="quiz-options" id="quiz-options"></div>
                        </div>
                        <button class="game-btn game-btn-primary" id="next-question-btn" disabled>
                            <span>Question suivante</span>
                            <span>→</span>
                        </button>
                    </div>

                    <!-- Score Section (shown after quiz, before wheel) -->
                    <div class="score-section" id="score-section">
                        <div class="score-icon" id="score-icon">📊</div>
                        <div class="score-title" id="score-title">Votre score</div>
                        <div class="score-value" id="score-value">0/4</div>
                        <div class="score-message" id="score-message"></div>
                        <p style="color: #666; margin: 20px 0;">
                            Tournez maintenant la roue pour decouvrir votre recompense !
                        </p>
                        <button class="game-btn game-btn-primary" id="go-to-wheel-btn">
                            <span>🎯</span>
                            <span>Tourner la roue</span>
                        </button>
                    </div>

                    <!-- Wheel Section -->
                    <div class="wheel-section" id="wheel-section">
                        <p style="color: #666; margin-bottom: 20px;">
                            Cliquez sur le bouton pour tourner la roue !
                        </p>
                        <div class="wheel-container">
                            <div class="wheel-pointer"></div>
                            <canvas id="wheel-canvas" width="280" height="280"></canvas>
                            <div class="wheel-center"><span>🎯</span></div>
                        </div>
                        <button class="game-btn game-btn-primary" id="spin-wheel-btn">
                            <span>🎰</span>
                            <span>Tourner la roue !</span>
                        </button>
                    </div>

                    <!-- Result Section -->
                    <div class="result-section" id="result-section">
                        <div class="result-icon" id="result-icon"></div>
                        <div class="result-title" id="result-title"></div>
                        <div class="quiz-score-display" id="quiz-score-display"></div>
                        <div class="result-message" id="result-message"></div>
                        <div class="promo-code-box" id="promo-code-box" style="display: none;">
                            <div class="promo-code-label">Votre code promo</div>
                            <div class="promo-code-value" id="promo-code-value"></div>
                            <button class="promo-code-copy" id="copy-code-btn">Copier le code</button>
                        </div>
                        <button class="game-btn game-btn-secondary" id="close-result-btn">
                            Fermer
                        </button>
                    </div>
                </div>
            </div>
        </div>
        `;

        document.body.insertAdjacentHTML('beforeend', html);
    }

    /**
     * Bind all event listeners
     */
    function bindEvents() {
        // Close button
        document.getElementById('game-close-btn').addEventListener('click', hidePopup);

        // Click outside to close
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                hidePopup();
            }
        });

        // Start quiz button
        document.getElementById('start-quiz-btn').addEventListener('click', handleStartQuiz);

        // Next question button
        document.getElementById('next-question-btn').addEventListener('click', handleNextQuestion);

        // Go to wheel button (after score display)
        document.getElementById('go-to-wheel-btn').addEventListener('click', handleGoToWheel);

        // Spin wheel button
        document.getElementById('spin-wheel-btn').addEventListener('click', handleSpinWheel);

        // Copy code button
        document.getElementById('copy-code-btn').addEventListener('click', handleCopyCode);

        // Close result button
        document.getElementById('close-result-btn').addEventListener('click', hidePopup);

        // ESC key to close
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && overlay.classList.contains('active')) {
                hidePopup();
            }
        });
    }

    /**
     * Show the popup
     */
    function showPopup() {
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Hide the popup
     */
    function hidePopup() {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
        sessionStorage.setItem(CONFIG.storageKey, 'true');
    }

    /**
     * Show error message
     */
    function showError(message) {
        const errorEl = document.getElementById('game-error');
        errorEl.textContent = message;
        errorEl.classList.add('active');
        setTimeout(() => errorEl.classList.remove('active'), 5000);
    }

    /**
     * Show/hide loading
     */
    function setLoading(show) {
        const loadingEl = document.getElementById('game-loading');
        loadingEl.classList.toggle('active', show);
    }

    /**
     * Update step indicators
     */
    function updateSteps(currentStep) {
        const steps = document.querySelectorAll('.game-step');
        const stepOrder = ['registration', 'quiz', 'score', 'wheel'];
        const currentIndex = stepOrder.indexOf(currentStep);

        steps.forEach((step, index) => {
            step.classList.remove('active', 'completed');
            if (index < currentIndex) {
                step.classList.add('completed');
            } else if (index === currentIndex) {
                step.classList.add('active');
            }
        });
    }

    /**
     * Handle start quiz button
     */
    async function handleStartQuiz() {
        const name = document.getElementById('game-name').value.trim();
        const email = document.getElementById('game-email').value.trim();
        const phone = document.getElementById('game-phone').value.trim();

        // Validation
        if (!name || !email || !phone) {
            showError('Veuillez remplir tous les champs');
            return;
        }

        if (!isValidEmail(email)) {
            showError('Veuillez entrer un email valide');
            return;
        }

        // Save user data
        state.userData = { name, email, phone };

        setLoading(true);

        try {
            // Check eligibility
            const eligibilityResponse = await fetch(`${CONFIG.apiBase}/game/check-eligibility/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, phone }),
            });

            const eligibilityData = await eligibilityResponse.json();

            if (!eligibilityData.eligible) {
                showError(eligibilityData.message);
                setLoading(false);
                return;
            }

            // Get quiz questions
            const questionsResponse = await fetch(`${CONFIG.apiBase}/game/questions/`);
            const questionsData = await questionsResponse.json();

            state.questions = questionsData.questions;
            state.currentQuestionIndex = 0;
            state.answers = {};

            // Show quiz section
            showSection('quiz');
            updateSteps('quiz');
            renderQuestion();

        } catch (error) {
            console.error('Error:', error);
            showError('Une erreur est survenue. Veuillez reessayer.');
        }

        setLoading(false);
    }

    /**
     * Render current question
     */
    function renderQuestion() {
        const question = state.questions[state.currentQuestionIndex];
        const totalQuestions = state.questions.length;

        // Update progress
        const progressHTML = state.questions.map((_, i) => {
            let classes = 'quiz-progress-dot';
            if (i < state.currentQuestionIndex) classes += ' completed';
            else if (i === state.currentQuestionIndex) classes += ' current';
            return `<div class="${classes}"></div>`;
        }).join('');
        document.getElementById('quiz-progress').innerHTML = progressHTML;

        // Update question number
        document.getElementById('quiz-number').textContent = `Question ${state.currentQuestionIndex + 1}/${totalQuestions}`;

        // Update question text
        document.getElementById('quiz-question').textContent = question.question;

        // Update options
        const optionsHTML = question.options.map((option, index) => `
            <label class="quiz-option" data-index="${index}">
                <input type="radio" name="quiz-answer" value="${index}">
                <span class="quiz-option-marker"></span>
                <span class="quiz-option-text">${option}</span>
            </label>
        `).join('');
        document.getElementById('quiz-options').innerHTML = optionsHTML;

        // Bind option click events
        document.querySelectorAll('.quiz-option').forEach(option => {
            option.addEventListener('click', function() {
                // Remove selected class from all
                document.querySelectorAll('.quiz-option').forEach(o => o.classList.remove('selected'));
                // Add selected class to clicked
                this.classList.add('selected');
                this.querySelector('input').checked = true;
                // Enable next button
                document.getElementById('next-question-btn').disabled = false;
            });
        });

        // Update button text for last question
        const btnText = state.currentQuestionIndex === totalQuestions - 1 ? 'Voir le resultat' : 'Question suivante';
        document.querySelector('#next-question-btn span:first-child').textContent = btnText;
        document.getElementById('next-question-btn').disabled = true;
    }

    /**
     * Handle next question button
     */
    async function handleNextQuestion() {
        // Save current answer
        const selectedOption = document.querySelector('.quiz-option.selected');
        if (selectedOption) {
            const question = state.questions[state.currentQuestionIndex];
            state.answers[question.id] = parseInt(selectedOption.dataset.index);
        }

        // Check if last question
        if (state.currentQuestionIndex === state.questions.length - 1) {
            // Submit quiz and show score
            await submitQuizAndShowScore();
        } else {
            // Next question
            state.currentQuestionIndex++;
            renderQuestion();
        }
    }

    /**
     * Submit quiz and display score before wheel
     */
    async function submitQuizAndShowScore() {
        setLoading(true);

        try {
            // Submit quiz and spin
            const response = await fetch(`${CONFIG.apiBase}/game/submit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ...state.userData,
                    answers: state.answers,
                }),
            });

            const data = await response.json();

            if (!data.success) {
                showError(data.message);
                setLoading(false);
                return;
            }

            // Save response data to state
            state.quizScore = data.quiz_score;
            state.quizTotal = data.quiz_total;
            state.scoreMessage = data.score_message;
            state.prize = data.prize;
            state.promoCode = data.promo_code;

            setLoading(false);

            // Show score section
            showSection('score');
            updateSteps('score');
            displayScore();

        } catch (error) {
            console.error('Error:', error);
            showError('Une erreur est survenue. Veuillez reessayer.');
            setLoading(false);
        }
    }

    /**
     * Display score after quiz
     */
    function displayScore() {
        const scoreValueEl = document.getElementById('score-value');
        const scoreMessageEl = document.getElementById('score-message');
        const scoreIconEl = document.getElementById('score-icon');

        scoreValueEl.textContent = `${state.quizScore}/${state.quizTotal}`;
        scoreMessageEl.textContent = state.scoreMessage;

        // Update icon based on score
        const percentage = state.quizScore / state.quizTotal;
        if (percentage === 1) {
            scoreIconEl.textContent = '🏆';
        } else if (percentage >= 0.75) {
            scoreIconEl.textContent = '🎉';
        } else if (percentage >= 0.5) {
            scoreIconEl.textContent = '👍';
        } else {
            scoreIconEl.textContent = '💪';
        }
    }

    /**
     * Handle go to wheel button (from score screen)
     */
    function handleGoToWheel() {
        showSection('wheel');
        updateSteps('wheel');
        loadWheelSegments();
        drawWheel();
    }

    /**
     * Load wheel segments from API
     */
    async function loadWheelSegments() {
        try {
            const response = await fetch(`${CONFIG.apiBase}/game/wheel-segments/`);
            const data = await response.json();
            if (data.segments && data.segments.length > 0) {
                WHEEL_SEGMENTS = data.segments;
            }
        } catch (error) {
            console.error('Error loading wheel segments:', error);
            // Keep default segments
        }
    }

    /**
     * Draw the wheel
     */
    function drawWheel(rotation = 0) {
        const canvas = document.getElementById('wheel-canvas');
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = canvas.width / 2 - 10;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const segmentAngle = (2 * Math.PI) / WHEEL_SEGMENTS.length;
        const startOffset = rotation - Math.PI / 2;

        WHEEL_SEGMENTS.forEach((segment, index) => {
            const startAngle = startOffset + (index * segmentAngle);
            const endAngle = startAngle + segmentAngle;

            // Draw segment
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, startAngle, endAngle);
            ctx.closePath();
            ctx.fillStyle = segment.color;
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Draw text
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(startAngle + segmentAngle / 2);
            ctx.textAlign = 'right';
            ctx.fillStyle = '#333';
            ctx.font = 'bold 12px Arial';
            ctx.fillText(segment.label, radius - 15, 4);
            ctx.restore();
        });

        // Draw outer ring
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = '#ffcc00';
        ctx.lineWidth = 5;
        ctx.stroke();
    }

    /**
     * Handle spin wheel (quiz already submitted, just animate)
     */
    function handleSpinWheel() {
        const spinBtn = document.getElementById('spin-wheel-btn');
        spinBtn.disabled = true;

        // Find the prize index based on prize type or pick random for animation
        let prizeIndex = 0;
        if (state.prize && state.prize.won) {
            // Find a winning segment for visual effect
            prizeIndex = WHEEL_SEGMENTS.findIndex(s => s.is_winning === true);
        } else {
            // Find a losing segment
            prizeIndex = WHEEL_SEGMENTS.findIndex(s => s.is_winning === false);
        }

        // If not found, pick random
        if (prizeIndex < 0) {
            prizeIndex = Math.floor(Math.random() * WHEEL_SEGMENTS.length);
        }

        // Animate wheel
        animateWheel(prizeIndex, () => {
            showResult();
        });
    }

    /**
     * Animate the wheel spinning
     */
    function animateWheel(targetIndex, callback) {
        const segmentAngle = (2 * Math.PI) / WHEEL_SEGMENTS.length;
        const targetAngle = -targetIndex * segmentAngle - segmentAngle / 2;
        const totalRotation = (5 * 2 * Math.PI) + targetAngle; // 5 full spins + target

        const startTime = Date.now();
        const duration = CONFIG.wheelSpinDuration;

        function animate() {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function (ease out cubic)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentRotation = totalRotation * easeOut;

            drawWheel(currentRotation);

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                callback();
            }
        }

        requestAnimationFrame(animate);
    }

    /**
     * Show result section
     */
    function showResult() {
        showSection('result');

        const resultSection = document.getElementById('result-section');
        const iconEl = document.getElementById('result-icon');
        const titleEl = document.getElementById('result-title');
        const scoreEl = document.getElementById('quiz-score-display');
        const messageEl = document.getElementById('result-message');
        const promoBox = document.getElementById('promo-code-box');
        const promoValue = document.getElementById('promo-code-value');

        // Show quiz score
        scoreEl.innerHTML = `Score au quiz: <span>${state.quizScore}/${state.quizTotal}</span>`;

        if (state.prize.won) {
            // Won!
            resultSection.classList.remove('result-lost');
            iconEl.textContent = '🎉';
            titleEl.textContent = 'Felicitations !';

            // Build message with fresh products info
            let prizeMessage = `Vous avez gagne: ${state.prize.name}`;
            if (state.prize.applies_to_fresh_only) {
                prizeMessage += '\n(Applicable uniquement sur les produits frais)';
            }
            messageEl.textContent = prizeMessage;
            messageEl.style.whiteSpace = 'pre-line';

            promoBox.style.display = 'block';
            promoValue.textContent = state.promoCode;

            // Confetti effect
            createConfetti();
        } else {
            // Lost
            resultSection.classList.add('result-lost');
            iconEl.textContent = '😔';
            titleEl.textContent = 'Pas de chance...';
            messageEl.textContent = 'Vous n\'avez pas gagne cette fois-ci, mais merci d\'avoir participe !';
            promoBox.style.display = 'none';
        }
    }

    /**
     * Show a specific section
     */
    function showSection(sectionName) {
        const sections = ['registration', 'quiz', 'score', 'wheel', 'result'];
        sections.forEach(s => {
            const el = document.getElementById(`${s}-section`);
            if (el) {
                el.classList.toggle('active', s === sectionName);
                el.style.display = s === sectionName ? 'block' : 'none';
            }
        });
    }

    /**
     * Handle copy code
     */
    function handleCopyCode() {
        const code = state.promoCode;
        navigator.clipboard.writeText(code).then(() => {
            const btn = document.getElementById('copy-code-btn');
            const originalText = btn.textContent;
            btn.textContent = 'Code copie !';
            setTimeout(() => btn.textContent = originalText, 2000);
        });
    }

    /**
     * Create confetti effect
     */
    function createConfetti() {
        const container = document.createElement('div');
        container.className = 'confetti-container';
        document.body.appendChild(container);

        const colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3', '#F38181', '#AA96DA'];

        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.cssText = `
                left: ${Math.random() * 100}%;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                animation: confettiFall ${2 + Math.random() * 2}s ease-out forwards;
                animation-delay: ${Math.random() * 0.5}s;
            `;
            container.appendChild(confetti);
        }

        setTimeout(() => container.remove(), 5000);
    }

    /**
     * Validate email
     */
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
