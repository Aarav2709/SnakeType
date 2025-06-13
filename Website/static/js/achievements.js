document.addEventListener('DOMContentLoaded', function() {
    loadAchievements();
    animateAchievements();
});

function loadAchievements() {
    fetch('/api/achievements')
        .then(response => response.json())
        .then(data => {
            updateAchievementProgress(data);
        })
        .catch(error => {
            console.error('Error loading achievements:', error);
        });
}

function updateAchievementProgress(data) {
    const unlockedIds = new Set(data.achievements.map(ach => ach[0]));
    const achievementCards = document.querySelectorAll('.achievement-card');
    
    achievementCards.forEach(card => {
        const achievementId = card.dataset.achievementId;
        if (achievementId && unlockedIds.has(achievementId)) {
            card.classList.add('unlocked');
            card.classList.remove('locked');
            
            setTimeout(() => {
                card.style.animation = 'unlockPulse 0.6s ease';
            }, Math.random() * 2000);
        }
    });
}

function animateAchievements() {
    const achievementCards = document.querySelectorAll('.achievement-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    });
    
    achievementCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const achievementCards = document.querySelectorAll('.achievement-card');
    
    achievementCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            if (this.classList.contains('unlocked')) {
                this.style.transform = 'translateY(-3px) scale(1.02)';
                this.style.boxShadow = '0 8px 30px rgba(76, 175, 80, 0.4)';
            } else {
                this.style.transform = 'translateY(-2px)';
                this.style.opacity = '0.8';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            if (this.classList.contains('unlocked')) {
                this.style.boxShadow = '0 4px 20px rgba(76, 175, 80, 0.2)';
            } else {
                this.style.opacity = '0.6';
            }
        });
        
        card.addEventListener('click', function() {
            showAchievementDetails(this);
        });
    });
});

function showAchievementDetails(card) {
    const achievementId = card.dataset.achievementId;
    const isUnlocked = card.classList.contains('unlocked');
    
    const modal = createAchievementModal(achievementId, isUnlocked);
    document.body.appendChild(modal);
    
    setTimeout(() => {
        modal.style.opacity = '1';
        modal.querySelector('.achievement-modal-content').style.transform = 'translateY(0) scale(1)';
    }, 10);
}

function createAchievementModal(achievementId, isUnlocked) {
    const modal = document.createElement('div');
    modal.className = 'achievement-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(4px);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
        cursor: pointer;
    `;
    
    const content = document.createElement('div');
    content.className = 'achievement-modal-content';
    content.style.cssText = `
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 2rem;
        max-width: 400px;
        text-align: center;
        transform: translateY(-20px) scale(0.9);
        transition: transform 0.3s ease;
        cursor: default;
    `;
    
    content.innerHTML = `
        <div class="achievement-icon" style="font-size: 4rem; margin-bottom: 1rem;">
            ${getAchievementIcon(achievementId)}
        </div>
        <h2 style="color: #fff; margin-bottom: 0.5rem;">${getAchievementName(achievementId)}</h2>
        <p style="color: #ccc; margin-bottom: 1.5rem; line-height: 1.6;">
            ${getAchievementDescription(achievementId)}
        </p>
        <div class="achievement-status" style="
            padding: 1rem;
            border-radius: 8px;
            background: ${isUnlocked ? '#1e7e34' : '#333'};
            color: ${isUnlocked ? '#fff' : '#ccc'};
            font-weight: 600;
        ">
            ${isUnlocked ? '🎉 Achievement Unlocked!' : '🔒 Not Yet Unlocked'}
        </div>
    `;
    
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeAchievementModal(modal);
        }
    });
    
    content.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    modal.appendChild(content);
    return modal;
}

function closeAchievementModal(modal) {
    modal.style.opacity = '0';
    modal.querySelector('.achievement-modal-content').style.transform = 'translateY(-20px) scale(0.9)';
    
    setTimeout(() => {
        document.body.removeChild(modal);
    }, 300);
}

function getAchievementIcon(achievementId) {
    const icons = {
        'speed_demon': '🚀',
        'accuracy_master': '🎯',
        'perfectionist': '💎',
        'persistent': '🔥',
        'speed_machine': '⚡',
        'consistent': '📈',
        'marathon': '🏃',
        'improver': '📊',
        'streak_master': '🔥',
        'early_bird': '🌅',
        'night_owl': '🦉',
        'weekend_warrior': '🎮'
    };
    return icons[achievementId] || '🏆';
}

function getAchievementName(achievementId) {
    const names = {
        'speed_demon': 'Speed Demon',
        'accuracy_master': 'Accuracy Master',
        'perfectionist': 'Perfectionist',
        'persistent': 'Persistent',
        'speed_machine': 'Speed Machine',
        'consistent': 'Consistent',
        'marathon': 'Marathon',
        'improver': 'Improver',
        'streak_master': 'Streak Master',
        'early_bird': 'Early Bird',
        'night_owl': 'Night Owl',
        'weekend_warrior': 'Weekend Warrior'
    };
    return names[achievementId] || achievementId.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function getAchievementDescription(achievementId) {
    const descriptions = {
        'speed_demon': 'Reach 80+ WPM to prove your lightning-fast typing skills.',
        'accuracy_master': 'Maintain 98%+ accuracy to show your precision.',
        'perfectionist': 'Complete a test with 100% accuracy - no mistakes allowed!',
        'persistent': 'Complete 10 tests to demonstrate your dedication.',
        'speed_machine': 'Reach 100+ WPM to join the elite typing club.',
        'consistent': '5 tests in a row with >90% accuracy shows true skill.',
        'marathon': 'Type for 5 minutes straight without stopping.',
        'improver': 'Improve your WPM by 20+ points through practice.',
        'streak_master': 'Maintain a 7-day typing streak.',
        'early_bird': 'Take a test before 8 AM to earn this achievement.',
        'night_owl': 'Take a test after 10 PM for the night owls.',
        'weekend_warrior': 'Practice on weekends to stay sharp.'
    };
    return descriptions[achievementId] || 'Complete the challenge to unlock this achievement.';
}

function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-fill');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const targetWidth = entry.target.style.width;
                entry.target.style.width = '0%';
                setTimeout(() => {
                    entry.target.style.width = targetWidth;
                }, 200);
            }
        });
    });
    
    progressBars.forEach(bar => {
        observer.observe(bar);
    });
}

const unlockAnimationCSS = `
    @keyframes unlockPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); box-shadow: 0 0 20px rgba(76, 175, 80, 0.6); }
        100% { transform: scale(1); }
    }
`;

const style = document.createElement('style');
style.textContent = unlockAnimationCSS;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', animateProgressBars);

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modal = document.querySelector('.achievement-modal');
        if (modal) {
            closeAchievementModal(modal);
        }
    }
});
