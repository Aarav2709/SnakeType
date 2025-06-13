document.addEventListener('DOMContentLoaded', function() {
    initializeStatsPage();
});

function initializeStatsPage() {
    const hasStats = document.querySelector('.stats-overview');
    
    if (hasStats) {
        initializePerformanceChart();
        initializeAchievements();
        initializeAdvancedAnalytics();
        initializeErrorAnalysis();
        addInteractivity();
    }
    
    setupExportFeature();
    
    loadPerformanceInsights();
    
    initializeTimeFilters();
}

function initializeAdvancedAnalytics() {
    loadConsistencyTrends();
    
    loadTypingPatterns();
    
    loadDifficultyProgression();
    
    loadSessionAnalysis();
}

function initializeErrorAnalysis() {
    loadErrorPatterns();
    
    loadCharacterAnalysis();
    
    loadFingerPerformance();
}

function loadPerformanceInsights() {
    fetch('/api/performance_insights')
        .then(response => response.json())
        .then(data => {
            updatePerformanceInsights(data);
        })
        .catch(error => {
            console.error('Error loading performance insights:', error);
        });
}

function loadConsistencyTrends() {
    fetch('/api/stats?detailed=true')
        .then(response => response.json())
        .then(data => {
            if (data.consistency_data) {
                renderConsistencyChart(data.consistency_data);
            }
        })
        .catch(error => {
            console.error('Error loading consistency trends:', error);
        });
}

function loadTypingPatterns() {
    fetch('/api/typing_patterns')
        .then(response => response.json())
        .then(data => {
            updateTypingPatterns(data);
        })
        .catch(error => {
            console.error('Error loading typing patterns:', error);
        });
}

function loadErrorPatterns() {
    fetch('/api/error_analysis')
        .then(response => response.json())
        .then(data => {
            renderErrorAnalysis(data);
        })
        .catch(error => {
            console.error('Error loading error analysis:', error);
        });
}

function initializeTimeFilters() {
    const timeFilters = document.querySelectorAll('.time-filter');
    
    timeFilters.forEach(filter => {
        filter.addEventListener('click', function() {
            timeFilters.forEach(f => f.classList.remove('active'));
            
            this.classList.add('active');
            
            const timeRange = this.dataset.range;
            updateChartsWithTimeRange(timeRange);
        });
    });
}

function initializePerformanceChart() {
    const chartCanvas = document.getElementById('performanceChart');
    if (!chartCanvas) return;

    const testDataScript = document.querySelector('script[data-test-data]');
    let testData = [];
    
    if (testDataScript) {
        try {
            testData = JSON.parse(testDataScript.textContent);
        } catch (e) {
            console.error('Error parsing test data:', e);
        }
    }

    if (testData.length === 0) {
        showNoDataMessage();
        return;
    }

    const labels = testData.map(test => {
        const date = new Date(test[6]);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
        });
    });
    
    const wpmData = testData.map(test => test[0]);
    const accuracyData = testData.map(test => test[1]);

    const ctx = chartCanvas.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'WPM',
                data: wpmData,
                borderColor: '#ffffff',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                tension: 0.4,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: '#000000',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
                yAxisID: 'y'
            }, {
                label: 'Accuracy (%)',
                data: accuracyData,
                borderColor: '#cccccc',
                backgroundColor: 'rgba(204, 204, 204, 0.1)',
                tension: 0.4,
                pointBackgroundColor: '#cccccc',
                pointBorderColor: '#000000',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff',
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#ffffff',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#cccccc'
                    },
                    grid: {
                        color: '#333333'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    ticks: {
                        color: '#cccccc'
                    },
                    grid: {
                        color: '#333333'
                    },
                    title: {
                        display: true,
                        text: 'Words Per Minute',
                        color: '#ffffff'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 100,
                    ticks: {
                        color: '#cccccc'
                    },
                    grid: {
                        drawOnChartArea: false,
                        color: '#333333'
                    },
                    title: {
                        display: true,
                        text: 'Accuracy (%)',
                        color: '#ffffff'
                    }
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart'
            }
        }
    });

    chartCanvas.addEventListener('click', (event) => {
        const points = chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
        if (points.length) {
            const firstPoint = points[0];
            const dataIndex = firstPoint.index;
            showTestDetails(testData[dataIndex]);
        }
    });
}

function showNoDataMessage() {
    const chartContainer = document.querySelector('.chart-container');
    if (chartContainer) {
        chartContainer.innerHTML = `
            <div class="no-data">
                <p>No performance data available yet.</p>
                <p>Take some typing tests to see your progress!</p>
            </div>
        `;
    }
}

function showTestDetails(testData) {
    const modal = document.createElement('div');
    modal.className = 'test-detail-modal';
    modal.innerHTML = `
        <div class="test-detail-content">
            <h3>Test Details</h3>
            <p><strong>Date:</strong> ${new Date(testData[6]).toLocaleString()}</p>
            <p><strong>WPM:</strong> ${testData[0].toFixed(0)}</p>
            <p><strong>Accuracy:</strong> ${testData[1].toFixed(0)}%</p>
            <p><strong>Duration:</strong> ${testData[2]}s</p>
            <p><strong>Words Typed:</strong> ${testData[3]}</p>
            <p><strong>Errors:</strong> ${testData[4]}</p>
            <p><strong>Difficulty:</strong> ${testData[5].charAt(0).toUpperCase() + testData[5].slice(1)}</p>
            <button onclick="this.parentElement.parentElement.remove()">Close</button>
        </div>
    `;
    
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    `;
    
    modal.querySelector('.test-detail-content').style.cssText = `
        background: #111111;
        border: 2px solid #ffffff;
        padding: 2rem;
        max-width: 400px;
        color: #ffffff;
    `;
    
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

function initializeAchievements() {
    const achievementCards = document.querySelectorAll('.achievement-card');
    
    const bestWPM = parseFloat(document.querySelector('.stat-card h3')?.textContent) || 0;
    const statsCards = document.querySelectorAll('.stat-card h3');
    
    if (statsCards.length >= 4) {
        const bestAccuracy = parseFloat(statsCards[2].textContent.replace('%', '')) || 0;
        const totalTests = parseInt(statsCards[4].textContent) || 0;
        
        updateAchievementStatus(achievementCards, bestWPM, bestAccuracy, totalTests);
    }
    
    achievementCards.forEach(card => {
        card.addEventListener('click', () => {
            showAchievementDetails(card);
        });
    });
}

function updateAchievementStatus(cards, bestWPM, bestAccuracy, totalTests) {
    const achievements = [
        { threshold: bestWPM >= 80, name: 'Speed Demon' },
        { threshold: bestAccuracy >= 98, name: 'Accuracy Master' },
        { threshold: totalTests >= 10, name: 'Persistent' },
        { threshold: false, name: 'Marathon' }, // Requires duration check
        { threshold: bestAccuracy >= 100, name: 'Perfectionist' },
        { threshold: false, name: 'Consistent' }, // Requires streak check
        { threshold: bestWPM >= 100, name: 'Speed Machine' },
        { threshold: false, name: 'Improver' } // Requires improvement check
    ];
    
    cards.forEach((card, index) => {
        if (achievements[index] && achievements[index].threshold) {
            card.classList.remove('locked');
            card.classList.add('unlocked');
            
            setTimeout(() => {
                card.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    card.style.transform = 'scale(1)';
                }, 200);
            }, index * 100);
        }
    });
}

function showAchievementDetails(card) {
    const name = card.querySelector('.achievement-name').textContent;
    const desc = card.querySelector('.achievement-desc').textContent;
    const icon = card.querySelector('.achievement-icon').textContent;
    const isUnlocked = card.classList.contains('unlocked');
    
    const modal = document.createElement('div');
    modal.className = 'achievement-detail-modal';
    modal.innerHTML = `
        <div class="achievement-detail-content">
            <div class="achievement-icon-large">${icon}</div>
            <h3>${name}</h3>
            <p>${desc}</p>
            <div class="achievement-status ${isUnlocked ? 'unlocked' : 'locked'}">
                ${isUnlocked ? '✅ Unlocked!' : '🔒 Not yet unlocked'}
            </div>
            <button onclick="this.parentElement.parentElement.remove()">Close</button>
        </div>
    `;
    
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    `;
    
    const content = modal.querySelector('.achievement-detail-content');
    content.style.cssText = `
        background: #111111;
        border: 2px solid #ffffff;
        padding: 3rem;
        text-align: center;
        max-width: 400px;
        color: #ffffff;
    `;
    
    content.querySelector('.achievement-icon-large').style.cssText = `
        font-size: 4rem;
        margin-bottom: 1rem;
    `;
    
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

function addInteractivity() {
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-2px)';
            card.style.boxShadow = '0 5px 20px rgba(255, 255, 255, 0.1)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = 'none';
        });
    });
    
    const table = document.querySelector('.test-table');
    if (table) {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                sortTable(table, index);
            });
        });
    }
}

function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isAscending = table.dataset.sortOrder !== 'asc';
    table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        return isAscending 
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
    });
    
    rows.forEach(row => tbody.appendChild(row));
    
    const headers = table.querySelectorAll('th');
    headers.forEach(h => h.classList.remove('sorted-asc', 'sorted-desc'));
    headers[columnIndex].classList.add(isAscending ? 'sorted-asc' : 'sorted-desc');
}

function setupExportFeature() {
    const exportBtn = document.querySelector('.export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportData);
    }
}

function exportData() {
    const table = document.querySelector('.test-table');
    if (!table) {
        alert('No data to export');
        return;
    }
    
    const rows = table.querySelectorAll('tbody tr');
    if (rows.length === 0) {
        alert('No data to export');
        return;
    }
    
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
    const csvData = [headers.join(',')];
    
    rows.forEach(row => {
        const cells = Array.from(row.cells).map(cell => {
            let text = cell.textContent.trim();
            if (cell.querySelector('.difficulty-badge')) {
                text = cell.querySelector('.difficulty-badge').textContent.trim();
            }
            if (text.includes(',') || text.includes('"')) {
                text = `"${text.replace(/"/g, '""')}"`;
            }
            return text;
        });
        csvData.push(cells.join(','));
    });
    
    const csvContent = csvData.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `snaketype_stats_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } else {
        alert('Export feature not supported in this browser');
    }
}

function initializeSectionScrolling() {
    const sections = document.querySelectorAll('.stats-overview, .chart-section, .recent-tests, .achievements-section');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
}

document.addEventListener('DOMContentLoaded', initializeSectionScrolling);

function updatePerformanceInsights(insights) {
    const insightsContainer = document.getElementById('performance-insights-container');
    if (!insightsContainer || !insights) return;
    
    insightsContainer.innerHTML = `
        <div class="insight-card">
            <div class="insight-header">
                <h3>Typing Trend</h3>
                <span class="trend-indicator ${insights.trend || 'stable'}">${(insights.trend || 'stable').charAt(0).toUpperCase() + (insights.trend || 'stable').slice(1)}</span>
            </div>
            <p class="insight-description">Your typing speed is ${insights.trend || 'stable'} compared to last week.</p>
        </div>
        
        <div class="insight-card">
            <div class="insight-header">
                <h3>Consistency Score</h3>
                <span class="consistency-score">${insights.consistency_score || 0}%</span>
            </div>
            <p class="insight-description">Your typing consistency has ${insights.consistency_trend || 'remained stable'}.</p>
        </div>
        
        <div class="insight-card">
            <div class="insight-header">
                <h3>Problem Areas</h3>
                <div class="problem-chars">
                    ${(insights.problem_characters || []).slice(0, 5).map(char => `<span class="problem-char">${char}</span>`).join('')}
                </div>
            </div>
            <p class="insight-description">Focus on these characters to improve accuracy.</p>
        </div>
        
        <div class="insight-card">
            <div class="insight-header">
                <h3>Recommended Focus</h3>
                <span class="recommendation">${insights.recommended_lesson || 'Common Words'}</span>
            </div>
            <p class="insight-description">Practice this lesson type to improve your weakest areas.</p>
        </div>
    `;
}

function renderConsistencyChart(consistencyData) {
    const chartContainer = document.getElementById('consistency-chart');
    if (!chartContainer || !consistencyData || consistencyData.length === 0) return;
    
    const canvas = document.createElement('canvas');
    canvas.id = 'consistencyCanvas';
    canvas.width = 400;
    canvas.height = 200;
    chartContainer.innerHTML = '';
    chartContainer.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    
    const dataPoints = consistencyData.slice(-20); // Last 20 data points
    const maxConsistency = Math.max(...dataPoints);
    const minConsistency = Math.min(...dataPoints);
    const range = maxConsistency - minConsistency || 1;
    
    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    dataPoints.forEach((point, index) => {
        const x = (index / (dataPoints.length - 1)) * (canvas.width - 40) + 20;
        const y = canvas.height - 20 - ((point - minConsistency) / range) * (canvas.height - 40);
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
    
    ctx.fillStyle = '#ffffff';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Consistency Trend', canvas.width / 2, 15);
}

function updateTypingPatterns(patterns) {
    const patternsContainer = document.getElementById('typing-patterns');
    if (!patternsContainer || !patterns) return;
    
    patternsContainer.innerHTML = `
        <div class="pattern-item">
            <div class="pattern-header">
                <h4>Peak Performance Time</h4>
                <span class="pattern-value">${patterns.peak_time || 'Not enough data'}</span>
            </div>
        </div>
        
        <div class="pattern-item">
            <div class="pattern-header">
                <h4>Average Session Length</h4>
                <span class="pattern-value">${patterns.avg_session_length || 0} minutes</span>
            </div>
        </div>
        
        <div class="pattern-item">
            <div class="pattern-header">
                <h4>Most Active Day</h4>
                <span class="pattern-value">${patterns.most_active_day || 'Not enough data'}</span>
            </div>
        </div>
        
        <div class="pattern-item">
            <div class="pattern-header">
                <h4>Speed Improvement Rate</h4>
                <span class="pattern-value">${patterns.improvement_rate || 0} WPM/week</span>
            </div>
        </div>
    `;
}

function renderErrorAnalysis(errorData) {
    const errorContainer = document.getElementById('error-analysis-container');
    if (!errorContainer || !errorData) return;
    
    const problemChars = errorData.character_errors || {};
    const sortedChars = Object.entries(problemChars)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10);
    
    const charAnalysisHTML = sortedChars.map(([char, count]) => `
        <div class="error-char-item">
            <span class="error-char">${char}</span>
            <div class="error-bar">
                <div class="error-fill" style="width: ${(count / sortedChars[0][1]) * 100}%"></div>
            </div>
            <span class="error-count">${count}</span>
        </div>
    `).join('');
    
    const errorPatterns = errorData.error_patterns || {};
    const sortedPatterns = Object.entries(errorPatterns)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5);
    
    const patternsHTML = sortedPatterns.map(([pattern, count]) => `
        <div class="error-pattern-item">
            <span class="pattern-text">${pattern}</span>
            <span class="pattern-count">${count}x</span>
        </div>
    `).join('');
    
    errorContainer.innerHTML = `
        <div class="error-analysis-section">
            <h3>Most Problematic Characters</h3>
            <div class="error-chars-list">
                ${charAnalysisHTML}
            </div>
        </div>
        
        <div class="error-analysis-section">
            <h3>Common Error Patterns</h3>
            <div class="error-patterns-list">
                ${patternsHTML}
            </div>
        </div>
    `;
}

function loadCharacterAnalysis() {
    fetch('/api/character_analysis')
        .then(response => response.json())
        .then(data => {
            renderCharacterHeatmap(data);
        })
        .catch(error => {
            console.error('Error loading character analysis:', error);
        });
}

function renderCharacterHeatmap(data) {
    const heatmapContainer = document.getElementById('character-heatmap');
    if (!heatmapContainer || !data) return;
    
    const keyboard = [
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm']
    ];
    
    const maxErrors = Math.max(...Object.values(data.character_errors || {}));
    
    const heatmapHTML = keyboard.map(row => 
        `<div class="keyboard-row">
            ${row.map(char => {
                const errorCount = data.character_errors?.[char] || 0;
                const intensity = maxErrors > 0 ? errorCount / maxErrors : 0;
                const color = intensity > 0.7 ? 'high-error' : 
                            intensity > 0.4 ? 'medium-error' : 
                            intensity > 0.1 ? 'low-error' : 'no-error';
                
                return `<div class="key ${color}" data-char="${char}" data-errors="${errorCount}">
                    ${char.toUpperCase()}
                    <span class="error-count">${errorCount}</span>
                </div>`;
            }).join('')}
        </div>`
    ).join('');
    
    heatmapContainer.innerHTML = `
        <h3>Character Error Heatmap</h3>
        <div class="keyboard-layout">
            ${heatmapHTML}
        </div>
        <div class="heatmap-legend">
            <span class="legend-item no-error">No Errors</span>
            <span class="legend-item low-error">Low</span>
            <span class="legend-item medium-error">Medium</span>
            <span class="legend-item high-error">High</span>
        </div>
    `;
}

function updateChartsWithTimeRange(timeRange) {
    const params = new URLSearchParams({ time_range: timeRange });
    
    fetch(`/api/stats?${params}`)
        .then(response => response.json())
        .then(data => {
            updatePerformanceChart(data.test_data || []);
            
            if (data.consistency_data) {
                renderConsistencyChart(data.consistency_data);
            }
        })
        .catch(error => {
            console.error('Error updating charts:', error);
        });
}

function updatePerformanceChart(testData) {
    const chartCanvas = document.getElementById('performanceChart');
    if (!chartCanvas) return;
    
    const ctx = chartCanvas.getContext('2d');
    ctx.clearRect(0, 0, chartCanvas.width, chartCanvas.height);
    
    if (testData.length === 0) {
        showNoDataMessage();
        return;
    }
    
    renderChartData(testData, ctx, chartCanvas);
}

function renderChartData(testData, ctx, canvas) {
    const labels = testData.map(test => {
        const date = new Date(test[6]);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
        });
    });
    
    const wpmData = testData.map(test => test[0]);
    const accuracyData = testData.map(test => test[1]);
    
    const padding = 40;
    const chartWidth = canvas.width - 2 * padding;
    const chartHeight = canvas.height - 2 * padding;
    
    const maxWPM = Math.max(...wpmData);
    const minWPM = Math.min(...wpmData);
    const wpmRange = maxWPM - minWPM || 1;
    
    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    wpmData.forEach((wpm, index) => {
        const x = padding + (index / (wpmData.length - 1)) * chartWidth;
        const y = padding + chartHeight - ((wpm - minWPM) / wpmRange) * chartHeight;
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
    
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('WPM Over Time', canvas.width / 2, 20);
}
