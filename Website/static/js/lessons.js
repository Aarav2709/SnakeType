let currentLesson = null;
let selectedLessonData = null;

document.addEventListener('DOMContentLoaded', function() {
    loadLessonProgress();
});

function startLesson(lessonId) {
    fetch('/api/lessons')
        .then(response => response.json())
        .then(data => {
            const lesson = data.lessons[lessonId];
            if (lesson) {
                currentLesson = lessonId;
                selectedLessonData = lesson;
                showLessonModal(lesson);
            }
        })
        .catch(error => {
            console.error('Error loading lesson:', error);
        });
}

function showLessonModal(lesson) {
    const modal = document.getElementById('lessonModal');
    const title = document.getElementById('lessonTitle');
    const description = document.getElementById('lessonDescription');
    const words = document.getElementById('lessonWords');
    
    title.textContent = lesson.name;
    description.textContent = lesson.desc;
    words.textContent = lesson.words.join(' ');
    
    modal.style.display = 'block';
    
    document.addEventListener('keydown', handleModalEscape);
}

function closeLessonModal() {
    const modal = document.getElementById('lessonModal');
    modal.style.display = 'none';
    currentLesson = null;
    selectedLessonData = null;
    
    document.removeEventListener('keydown', handleModalEscape);
}

function handleModalEscape(event) {
    if (event.key === 'Escape') {
        closeLessonModal();
    }
}

function confirmStartLesson() {
    if (currentLesson && selectedLessonData) {
        sessionStorage.setItem('lessonType', currentLesson);
        sessionStorage.setItem('lessonData', JSON.stringify(selectedLessonData));
        
        window.location.href = `/test?lesson=${currentLesson}`;
    }
}

function loadLessonProgress() {
    const progress = JSON.parse(localStorage.getItem('lessonProgress') || '{}');
    
    Object.keys(progress).forEach(lessonId => {
        const card = document.querySelector(`[onclick="startLesson('${lessonId}')"]`);
        if (card && progress[lessonId].completed) {
            card.classList.add('completed');
            const completedBadge = document.createElement('div');
            completedBadge.className = 'lesson-completed';
            completedBadge.innerHTML = '✓ Completed';
            card.appendChild(completedBadge);
        }
    });
}

function updateLessonProgress(lessonId, stats) {
    const progress = JSON.parse(localStorage.getItem('lessonProgress') || '{}');
    
    if (!progress[lessonId]) {
        progress[lessonId] = {
            attempts: 0,
            bestWpm: 0,
            bestAccuracy: 0,
            completed: false
        };
    }
    
    progress[lessonId].attempts++;
    progress[lessonId].bestWpm = Math.max(progress[lessonId].bestWpm, stats.wpm);
    progress[lessonId].bestAccuracy = Math.max(progress[lessonId].bestAccuracy, stats.accuracy);
    
    if (stats.accuracy >= 90) {
        progress[lessonId].completed = true;
    }
    
    localStorage.setItem('lessonProgress', JSON.stringify(progress));
}

document.addEventListener('click', function(event) {
    const modal = document.getElementById('lessonModal');
    if (event.target === modal) {
        closeLessonModal();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const lessonCards = document.querySelectorAll('.lesson-card');
    
    lessonCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

document.addEventListener('keydown', function(event) {
    const lessonCards = document.querySelectorAll('.lesson-card');
    const focusedElement = document.activeElement;
    
    if (event.key === 'Enter' && focusedElement.classList.contains('lesson-card')) {
        focusedElement.click();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const lessonCards = document.querySelectorAll('.lesson-card');
    lessonCards.forEach((card, index) => {
        card.setAttribute('tabindex', index + 1);
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', `Start ${card.querySelector('h3').textContent} lesson`);
    });
});

function animateOnScroll() {
    const cards = document.querySelectorAll('.lesson-card');
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
    
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

document.addEventListener('DOMContentLoaded', animateOnScroll);
