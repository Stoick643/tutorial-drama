document.addEventListener('DOMContentLoaded', function() {
    const commandInput = document.getElementById('command-input');
    const checkButton = document.getElementById('check-answer');
    const consoleOutput = document.getElementById('console-output');
    const feedbackDiv = document.getElementById('feedback');
    const consoleEl = document.querySelector('.interactive-console');
    const isChat = consoleEl && consoleEl.dataset.mode === 'chat';

    function getCurrentLesson() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 1];
    }

    function getCurrentTopic() {
        const pathParts = window.location.pathname.split('/');
        // URL format: /tutorial/redis/00_setup
        if (pathParts.length >= 3 && pathParts[1] === 'tutorial') {
            return pathParts[2];
        }
        return 'redis'; // fallback
    }

    async function checkAnswer() {
        const command = commandInput.value.trim();

        if (!command) {
            showFeedback(isChat ? 'Please type a message' : 'Please enter a command', false);
            return;
        }

        checkButton.disabled = true;
        checkButton.textContent = isChat ? 'Sending...' : 'Checking...';

        try {
            const response = await fetch('/api/check-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: command,
                    topic: getCurrentTopic(),
                    lesson: getCurrentLesson()
                })
            });

            const data = await response.json();

            if (!response.ok) {
                showFeedback('Server error: ' + (data.detail || 'Unknown error'), false);
                return;
            }

            showOutput(data.output);

            if (isChat) {
                // Chat mode: no correct/incorrect, just show response
                markLessonCompleted(getCurrentTopic(), getCurrentLesson());
            } else {
                // Check mode: show grading feedback
                showFeedback(data.feedback_message, data.is_correct);

                if (data.is_correct) {
                    commandInput.style.borderColor = '#5cb85c';
                    setTimeout(() => {
                        commandInput.style.borderColor = '';
                    }, 3000);

                    // Mark lesson as completed
                    markLessonCompleted(getCurrentTopic(), getCurrentLesson());
                }
            }

        } catch (error) {
            showFeedback('Error connecting to server: ' + error.message, false);
        } finally {
            checkButton.disabled = false;
            checkButton.textContent = isChat ? 'Send' : 'Check Answer';
        }
    }

    function showOutput(output) {
        consoleOutput.textContent = output;
        consoleOutput.classList.add('show');
    }

    function showFeedback(message, isSuccess) {
        feedbackDiv.textContent = message;
        feedbackDiv.className = 'feedback-message';

        if (isSuccess) {
            feedbackDiv.classList.add('success');
        } else {
            feedbackDiv.classList.add('error');
        }

        setTimeout(() => {
            feedbackDiv.style.opacity = '0';
            setTimeout(() => {
                feedbackDiv.style.opacity = '1';
                feedbackDiv.className = 'feedback-message';
            }, 500);
        }, 5000);
    }

    checkButton.addEventListener('click', checkAnswer);

    // Only bind Enter to submit for single-line inputs (not textareas)
    if (commandInput.tagName === 'INPUT') {
        commandInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                checkAnswer();
            }
        });
    } else {
        // For textarea, use Ctrl+Enter to submit
        commandInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                checkAnswer();
            }
        });
    }

    // Don't auto-focus console — let user read the lesson first
    // commandInput.focus();

    // Check if current lesson is completed on page load
    checkLessonCompletion();

    function checkLessonCompletion() {
        const topic = getCurrentTopic();
        const lesson = getCurrentLesson();
        const progressKey = `tutorial_progress_${topic}`;
        const completedLessons = JSON.parse(localStorage.getItem(progressKey) || '[]');

        const statusDiv = document.getElementById('lesson-status');
        if (statusDiv && completedLessons.includes(lesson)) {
            statusDiv.innerHTML = '<span class="completed-badge">✅ Completed</span>';
            statusDiv.style.cssText = `
                color: #5cb85c;
                font-weight: bold;
                margin-left: 10px;
            `;
        }
    }

    // Mark current lesson as completed and update progress
    function markLessonCompleted(topic, lesson) {
        const progressKey = `tutorial_progress_${topic}`;
        let completedLessons = JSON.parse(localStorage.getItem(progressKey) || '[]');

        if (!completedLessons.includes(lesson)) {
            completedLessons.push(lesson);
            localStorage.setItem(progressKey, JSON.stringify(completedLessons));

            // Show completion indicator
            showCompletionMessage();

            // Update lesson status display
            const statusDiv = document.getElementById('lesson-status');
            if (statusDiv) {
                statusDiv.innerHTML = '<span class="completed-badge">✅ Completed</span>';
                statusDiv.style.cssText = `
                    color: #5cb85c;
                    font-weight: bold;
                    margin-left: 10px;
                `;
            }
        }
    }

    function showCompletionMessage() {
        const completionDiv = document.createElement('div');
        completionDiv.className = 'completion-message';
        completionDiv.innerHTML = '✅ Lesson completed! Well done, detective.';
        completionDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #5cb85c;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            font-weight: bold;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(completionDiv);

        setTimeout(() => {
            completionDiv.style.animation = 'slideOut 0.3s ease-in forwards';
            setTimeout(() => {
                document.body.removeChild(completionDiv);
            }, 300);
        }, 3000);
    }

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
});