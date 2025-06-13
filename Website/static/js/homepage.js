document.addEventListener('DOMContentLoaded', function() {
    const content = document.querySelector('div[style*="min-height: 70vh"]');
    if (content) {
        content.style.opacity = '0';
        content.style.transition = 'opacity 0.5s ease';
        setTimeout(() => {
            content.style.opacity = '1';
        }, 100);
    }
});

function loadPerformanceInsights() {
    fetch('/api/performance_insights')
        .then(response => response.json())
        .then(data => {
            updatePerformanceInsights(data);
        })
        .catch(error => {
            console.log('Performance insights not available yet');
        });
}

function loadAchievementsOverview() {
    fetch('/api/achievements')
        .then(response => response.json())
        .then(data => {
            updateAchievementsOverview(data);
        })
        .catch(error => {
            console.log('Achievements not available yet');
        });
}

function loadDailyGoalsAndStreaks() {
    fetch('/api/daily_progress')
        .then(response => response.json())
        .then(data => {
            updateDailyProgress(data);
        })
        .catch(error => {
            console.log('Daily progress not available yet');
        });
}

function initializeCustomTextUpload() {
    const uploadArea = document.getElementById('custom-text-upload');
    const fileInput = document.getElementById('custom-text-file');
    const textArea = document.getElementById('custom-text-area');
    
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });
        
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }
    
    const submitCustomText = document.getElementById('submit-custom-text');
    if (submitCustomText && textArea) {
        submitCustomText.addEventListener('click', () => {
            const customText = textArea.value.trim();
            if (customText) {
                uploadCustomText(customText);
            }
        });
    }
}

function handleFileUpload(file) {
    if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const text = e.target.result;
            uploadCustomText(text);
        };
        reader.readAsText(file);
    } else {
        showNotification('Please upload a .txt file', 'error');
    }
}

function uploadCustomText(text) {
    const formData = new FormData();
    formData.append('text', text);
    
    fetch('/api/upload_text', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Custom text uploaded successfully!', 'success');
            const textArea = document.getElementById('custom-text-area');
            if (textArea) textArea.value = '';
        } else {
            showNotification('Error uploading text: ' + data.error, 'error');
        }
    })
    .catch(error => {
        showNotification('Error uploading text', 'error');
    });
}

function calculateConsistencyScore(recentTests) {
    if (recentTests.length < 3) return 0;
    
    const wpms = recentTests.slice(0, 10).map(test => test.wpm);
    const average = wpms.reduce((a, b) => a + b, 0) / wpms.length;
    const variance = wpms.reduce((acc, wpm) => acc + Math.pow(wpm - average, 2), 0) / wpms.length;
    const standardDeviation = Math.sqrt(variance);
    
    const coefficientOfVariation = standardDeviation / average;
    const consistency = Math.max(0, Math.min(100, 100 - (coefficientOfVariation * 100)));
    
    return Math.round(consistency);
}

function updateRecentTests(recentTests) {
    const recentTestsList = document.getElementById('recent-tests-list');
    if (recentTestsList) {
        recentTestsList.innerHTML = '';
        
        recentTests.forEach((test, index) => {
            const testItem = document.createElement('div');
            testItem.className = 'recent-test-item';
            testItem.innerHTML = `
                <div class="test-rank">#${index + 1}</div>
                <div class="test-details">
                    <div class="test-wpm">${Math.round(test.wpm)} WPM</div>
                    <div class="test-accuracy">${Math.round(test.accuracy)}% acc</div>
                    <div class="test-date">${formatDate(test.date)}</div>
                </div>
                <div class="test-score-badge ${getScoreBadgeClass(test.wpm, test.accuracy)}">
                    ${getScoreRating(test.wpm, test.accuracy)}
                </div>
            `;
            recentTestsList.appendChild(testItem);
        });
    }
}

function updatePerformanceInsights(insights) {
    const insightsContainer = document.getElementById('performance-insights');
    if (insightsContainer && insights) {
        const trendElement = document.getElementById('typing-trend');
        if (trendElement) {
            const trend = insights.trend || 'stable';
            trendElement.textContent = trend.charAt(0).toUpperCase() + trend.slice(1);
            trendElement.className = `trend-indicator ${trend}`;
        }
        
        const problemAreasElement = document.getElementById('problem-areas');
        if (problemAreasElement && insights.problem_characters) {
            problemAreasElement.innerHTML = insights.problem_characters
                .slice(0, 5)
                .map(char => `<span class="problem-char">${char}</span>`)
                .join('');
        }
        
        const recommendedLessonElement = document.getElementById('recommended-lesson');
        if (recommendedLessonElement && insights.recommended_lesson) {
            recommendedLessonElement.textContent = insights.recommended_lesson;
        }
    }
}

function updateAchievementsOverview(achievements) {
    const achievementsOverview = document.getElementById('achievements-overview');
    if (achievementsOverview && achievements) {
        const unlockedCount = achievements.filter(a => a.unlocked).length;
        const totalCount = achievements.length;
        
        const progressElement = document.getElementById('achievements-progress');
        if (progressElement) {
            progressElement.textContent = `${unlockedCount}/${totalCount}`;
        }
        
        const progressBar = document.getElementById('achievements-progress-bar');
        if (progressBar) {
            const percentage = (unlockedCount / totalCount) * 100;
            progressBar.style.width = `${percentage}%`;
        }
        
        const recentAchievement = achievements.find(a => a.unlocked && a.unlocked_recently);
        const recentAchievementElement = document.getElementById('recent-achievement');
        if (recentAchievementElement) {
            if (recentAchievement) {
                recentAchievementElement.innerHTML = `
                    <div class="achievement-icon">${recentAchievement.icon}</div>
                    <div class="achievement-name">${recentAchievement.name}</div>
                `;
                recentAchievementElement.classList.add('has-achievement');
            } else {
                recentAchievementElement.innerHTML = '<div class="no-recent">No recent achievements</div>';
                recentAchievementElement.classList.remove('has-achievement');
            }
        }
    }
}

function updateDailyProgress(progress) {
    const dailyProgressElement = document.getElementById('daily-progress');
    if (dailyProgressElement && progress) {
        const goalProgressElement = document.getElementById('daily-goal-progress');
        if (goalProgressElement) {
            const percentage = Math.min(100, (progress.tests_today / (progress.daily_goal || 5)) * 100);
            goalProgressElement.style.width = `${percentage}%`;
        }
        
        const goalTextElement = document.getElementById('daily-goal-text');
        if (goalTextElement) {
            goalTextElement.textContent = `${progress.tests_today}/${progress.daily_goal || 5} tests`;
        }
        
        const streakElement = document.getElementById('current-streak');
        if (streakElement) {
            streakElement.textContent = `${progress.current_streak || 0} days`;
        }
        
        const streakBadge = document.getElementById('streak-badge');
        if (streakBadge) {
            const streak = progress.current_streak || 0;
            if (streak >= 30) {
                streakBadge.className = 'streak-badge legendary';
                streakBadge.textContent = '🔥';
            } else if (streak >= 14) {
                streakBadge.className = 'streak-badge epic';
                streakBadge.textContent = '⭐';
            } else if (streak >= 7) {
                streakBadge.className = 'streak-badge good';
                streakBadge.textContent = '✨';
            } else {
                streakBadge.className = 'streak-badge';
                streakBadge.textContent = '📅';
            }
        }
    }
}

function initializeRealTimeUpdates() {
    let lastActivity = Date.now();
    
    document.addEventListener('click', () => {
        lastActivity = Date.now();
    });
    
    document.addEventListener('keypress', () => {
        lastActivity = Date.now();
    });
    
    setInterval(() => {
        if (Date.now() - lastActivity < 120000) {
            loadHomepageStats();
            loadDailyGoalsAndStreaks();
        }
    }, 30000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
        return 'Just now';
    } else if (diffInHours < 24) {
        return `${Math.floor(diffInHours)}h ago`;
    } else {
        return date.toLocaleDateString();
    }
}

function getScoreBadgeClass(wpm, accuracy) {
    if (wpm >= 80 && accuracy >= 98) return 'legendary';
    if (wpm >= 60 && accuracy >= 95) return 'excellent';
    if (wpm >= 40 && accuracy >= 90) return 'good';
    return 'average';
}

function getScoreRating(wpm, accuracy) {
    if (wpm >= 80 && accuracy >= 98) return 'Legendary';
    if (wpm >= 60 && accuracy >= 95) return 'Excellent';
    if (wpm >= 40 && accuracy >= 90) return 'Good';
    return 'Average';
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function updateStatDisplay(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
    }
}

function animateNumbers() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(element => {
        const finalValue = parseInt(element.textContent) || 0;
        const duration = 1000; // 1 second
        const startTime = performance.now();
        
        function updateNumber(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentValue = Math.floor(finalValue * easeOut);
            
            element.textContent = element.id === 'avg-accuracy' || element.id === 'best-accuracy' 
                ? currentValue + '%' 
                : currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        }
        
        if (finalValue > 0) {
            element.textContent = '0';
            requestAnimationFrame(updateNumber);
        }
    });
}

function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
    
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 30px rgba(255, 255, 255, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

function addTypingAnimation() {
    const heroTitle = document.querySelector('.hero h1');
    if (heroTitle) {
        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        
        let i = 0;
        const typeInterval = setInterval(() => {
            heroTitle.textContent += text.charAt(i);
            i++;
            
            if (i >= text.length) {
                clearInterval(typeInterval);
                heroTitle.innerHTML += '<span class="typing-cursor">|</span>';
            }
        }, 100);
    }
}

setTimeout(addTypingAnimation, 500);
