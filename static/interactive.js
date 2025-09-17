document.addEventListener('DOMContentLoaded', function() {
    const commandInput = document.getElementById('command-input');
    const checkButton = document.getElementById('check-answer');
    const consoleOutput = document.getElementById('console-output');
    const feedbackDiv = document.getElementById('feedback');

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
            showFeedback('Please enter a Redis command', false);
            return;
        }

        checkButton.disabled = true;
        checkButton.textContent = 'Checking...';

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

            showOutput(data.output);
            showFeedback(data.feedback_message, data.is_correct);

            if (data.is_correct) {
                commandInput.style.borderColor = '#5cb85c';
                setTimeout(() => {
                    commandInput.style.borderColor = '';
                }, 3000);
            }

        } catch (error) {
            showFeedback('Error connecting to server: ' + error.message, false);
        } finally {
            checkButton.disabled = false;
            checkButton.textContent = 'Check Answer';
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

    commandInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            checkAnswer();
        }
    });

    commandInput.focus();
});