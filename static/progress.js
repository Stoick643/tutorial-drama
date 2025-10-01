document.addEventListener('DOMContentLoaded', function() {
    const currentTopic = getCurrentTopicFromURL();
    if (currentTopic) {
        updateProgressDisplay(currentTopic);
        markCompletedLessons(currentTopic);
    }

    function getCurrentTopicFromURL() {
        const pathParts = window.location.pathname.split('/');
        // URL format: /tutorial/redis
        if (pathParts.length >= 3 && pathParts[1] === 'tutorial') {
            return pathParts[2];
        }
        return null;
    }

    function getCompletedLessons(topic) {
        const progressKey = `tutorial_progress_${topic}`;
        return JSON.parse(localStorage.getItem(progressKey) || '[]');
    }

    function updateProgressDisplay(topic) {
        const completedLessons = getCompletedLessons(topic);
        const totalLessons = document.querySelectorAll('.lesson-card').length;
        const completedCount = completedLessons.length;
        const progressPercentage = totalLessons > 0 ? Math.round((completedCount / totalLessons) * 100) : 0;

        // Update progress bar
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');

        if (progressFill) {
            progressFill.style.width = progressPercentage + '%';
        }

        if (progressText) {
            progressText.textContent = `${completedCount} of ${totalLessons} lessons completed (${progressPercentage}%)`;
        }
    }

    function markCompletedLessons(topic) {
        const completedLessons = getCompletedLessons(topic);
        const lessonCards = document.querySelectorAll('.lesson-card');

        lessonCards.forEach(card => {
            const lessonLink = card.querySelector('a[href*="/tutorial/"]');
            if (lessonLink) {
                const hrefParts = lessonLink.href.split('/');
                const lessonId = hrefParts[hrefParts.length - 1];

                if (completedLessons.includes(lessonId)) {
                    // Add completion indicator
                    if (!card.querySelector('.completion-badge')) {
                        const badge = document.createElement('div');
                        badge.className = 'completion-badge';
                        badge.innerHTML = '✅';
                        badge.style.cssText = `
                            position: absolute;
                            top: 10px;
                            right: 10px;
                            background: #5cb85c;
                            color: white;
                            border-radius: 50%;
                            width: 30px;
                            height: 30px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 14px;
                            font-weight: bold;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                        `;

                        // Make lesson card position relative if not already
                        card.style.position = 'relative';
                        card.appendChild(badge);
                    }

                    // Update button text
                    const button = card.querySelector('.btn-primary');
                    if (button && button.textContent === 'Start Lesson') {
                        button.textContent = '✅ Completed';
                        button.style.backgroundColor = '#5cb85c';
                    }
                }
            }
        });
    }

    // Add progress bar styles
    const style = document.createElement('style');
    style.textContent = `
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #5cb85c, #4cae4c);
            transition: width 0.3s ease;
        }

        .progress-text {
            text-align: center;
            color: #666;
            font-weight: bold;
            margin-top: 5px;
        }

        .completion-badge {
            animation: completionPulse 0.6s ease-in-out;
        }

        @keyframes completionPulse {
            0% { transform: scale(0); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
    `;
    document.head.appendChild(style);
});