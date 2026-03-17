/**
 * Emotion AI - Analyzer JavaScript
 * Text analysis, results display, charts
 */

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAnalyzer);
} else {
    initAnalyzer();
}

// Global variables
let barChart = null;
let pieChart = null;
let radarChart = null;
let currentAnalysisId = null;

function safeFormatPercent(value) {
    const formatter = window.EmotionAI && window.EmotionAI.formatPercent;
    if (typeof formatter === 'function') {
        return formatter(value);
    }
    const n = Number(value);
    if (!Number.isFinite(n)) return '0%';
    const pct = n <= 1 ? n * 100 : n;
    return `${pct.toFixed(1)}%`;
}

function getCssVar(name, fallback) {
    const value = getComputedStyle(document.body).getPropertyValue(name).trim();
    return value || fallback;
}

function initAnalyzer() {
    const textInput = document.getElementById('textInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const clearBtn = document.getElementById('clearBtn');
    const demoBtn = document.getElementById('demoBtn');
    const languageSelect = document.getElementById('languageSelect');
    
    // Character counter
    if (textInput) {
        textInput.addEventListener('input', updateStats);
        textInput.addEventListener('paste', () => setTimeout(updateStats, 0));
    }
    
    // Analyze button
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeText);
    }
    
    // Clear button
    if (clearBtn) {
        clearBtn.addEventListener('click', clearAll);
    }
    
    // Demo button
    if (demoBtn) {
        demoBtn.addEventListener('click', loadDemoText);
    }
    
    // Chart tabs
    initChartTabs();
    
    // Export buttons
    initExportButtons();
    
    // Feedback buttons
    initFeedbackButtons();
    
    // Theme change listener for charts
    window.addEventListener('themeChanged', updateChartColors);
}

/**
 * Update character/word/sentence stats
 */
function updateStats() {
    const textInput = document.getElementById('textInput');
    const charCount = document.getElementById('charCount');
    const wordCount = document.getElementById('wordCount');
    const sentenceCount = document.getElementById('sentenceCount');
    
    if (!textInput) return;
    
    const text = textInput.value;
    
    // Character count
    if (charCount) {
        charCount.textContent = text.length.toLocaleString('kk-KZ');
    }
    
    // Word count
    if (wordCount) {
        const words = text.trim().split(/\s+/).filter(w => w.length > 0);
        wordCount.textContent = words.length.toLocaleString('kk-KZ');
    }
    
    // Sentence count
    if (sentenceCount) {
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
        sentenceCount.textContent = sentences.length.toLocaleString('kk-KZ');
    }
}

/**
 * Analyze text
 */
async function analyzeText() {
    const textInput = document.getElementById('textInput');
    const languageSelect = document.getElementById('languageSelect');
    
    if (!textInput) return;
    
    const text = textInput.value.trim();
    const lang = languageSelect ? languageSelect.value : 'auto';
    
    // Validation
    if (!text) {
        window.EmotionAI.showToast('Мәтінді енгізіңіз', 'warning');
        textInput.focus();
        return;
    }
    
    if (text.length < 3) {
        window.EmotionAI.showToast('Мәтін тым қысқа', 'warning');
        textInput.focus();
        return;
    }
    
    // Show loading
    window.EmotionAI.showLoading('Мәтін талдануда...');
    
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        window.EmotionAI.updateProgress(progress);
    }, 200);
    
    try {
        const response = await window.EmotionAI.apiCall('/api/predict/', {
            method: 'POST',
            body: JSON.stringify({ text, lang })
        });
        
        clearInterval(progressInterval);
        window.EmotionAI.updateProgress(100);
        
        if (response.success) {
            currentAnalysisId = response.data.id;
            displayResults(response.data);
            window.EmotionAI.showToast('Талдау сәтті аяқталды!', 'success');
        } else {
            throw new Error(response.error || 'Талдау қатесі');
        }
        
    } catch (error) {
        clearInterval(progressInterval);
        window.EmotionAI.hideLoading();
        window.EmotionAI.showToast(error.message, 'error');
        console.error('Analysis error:', error);
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    
    if (!resultsSection) return;
    resultsSection.style.display = 'block';
    
    // Update primary emotion
    const primaryEmoji = document.getElementById('primaryEmoji');
    const primaryEmotionName = document.getElementById('primaryEmotionName');
    const primaryPercentage = document.getElementById('primaryPercentage');
    const confidenceFill = document.getElementById('confidenceFill');
    const confidenceValue = document.getElementById('confidenceValue');
    
    const emotionInfoMap = data.emotion_info || {};
    const emotionInfo = emotionInfoMap[data.primary_emotion];
    
    if (primaryEmoji) primaryEmoji.textContent = emotionInfo?.emoji || '😐';
    if (primaryEmotionName) primaryEmotionName.textContent = emotionInfo?.name || data.primary_emotion;
    if (primaryPercentage) primaryPercentage.textContent = safeFormatPercent(data.confidence);
    if (confidenceFill) {
        setTimeout(() => {
            confidenceFill.style.width = safeFormatPercent(data.confidence);
        }, 100);
    }
    if (confidenceValue) confidenceValue.textContent = safeFormatPercent(data.confidence);
    
    try {
        updateTopEmotions(data.probabilities || {}, emotionInfoMap);
    } catch (error) {
        console.error('Top emotions render error:', error);
    }
    
    try {
        updateCharts(data.probabilities || {}, emotionInfoMap);
    } catch (error) {
        console.error('Charts render error:', error);
    }
    
    try {
        updateSentenceAnalysis(data.sentence_results || []);
    } catch (error) {
        console.error('Sentence analysis render error:', error);
    }
    
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Hide loading
    setTimeout(() => {
        window.EmotionAI.hideLoading();
    }, 500);
}

/**
 * Update top emotions list
 */
function updateTopEmotions(probabilities, emotionInfo) {
    const emotionsList = document.getElementById('emotionsList');
    if (!emotionsList) return;
    
    // Sort by probability
    const sorted = Object.entries(probabilities)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    emotionsList.innerHTML = sorted.map(([emotion, prob], index) => {
        const info = emotionInfo[emotion] || { emoji: '😐', color: '#95A5A6', name: emotion };
        return `
            <div class="emotion-item" style="animation: fadeInUp 0.3s ease ${index * 0.1}s both;">
                <span class="emotion-rank">${index + 1}</span>
                <span class="emotion-icon-small">${info.emoji}</span>
                <div class="emotion-details">
                    <span class="emotion-label">${info.name}</span>
                    <div class="emotion-bar-container">
                        <div class="emotion-bar-fill" style="width: 0%; background-color: ${info.color};"></div>
                    </div>
                </div>
                <span class="emotion-percent">${safeFormatPercent(prob)}</span>
            </div>
        `;
    }).join('');
    
    // Animate bars
    setTimeout(() => {
        const bars = emotionsList.querySelectorAll('.emotion-bar-fill');
        bars.forEach((bar, index) => {
            bar.style.width = safeFormatPercent(sorted[index][1]);
        });
    }, 100);
}

/**
 * Update charts
 */
function updateCharts(probabilities, emotionInfo) {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is unavailable. Skipping chart rendering.');
        return;
    }

    const sorted = Object.entries(probabilities)
        .sort((a, b) => b[1] - a[1]);
    
    const labels = sorted.map(([emotion, _]) => emotionInfo[emotion]?.name || emotion);
    const data = sorted.map(([_, prob]) => Number((prob * 100).toFixed(1)));
    const colors = sorted.map(([emotion, _]) => emotionInfo[emotion]?.color || '#95A5A6');
    const emojis = sorted.map(([emotion, _]) => emotionInfo[emotion]?.emoji || '😐');
    
    // Bar Chart
    const barCtx = document.getElementById('barChart');
    if (barCtx) {
        if (barChart) barChart.destroy();
        
        barChart = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: labels.map((l, i) => `${emojis[i]} ${l}`),
                datasets: [{
                    label: 'Ықтималдық (%)',
                    data: data,
                    backgroundColor: colors,
                    borderRadius: 8,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.parsed.y}%`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: (value) => value + '%',
                            color: getCssVar('--text-secondary', getCssVar('--text-muted', '#5b6478'))
                        },
                        grid: {
                            color: getCssVar('--border-color', 'rgba(15, 23, 42, 0.15)')
                        }
                    },
                    x: {
                        ticks: {
                            color: getCssVar('--text-secondary', getCssVar('--text-muted', '#5b6478'))
                        },
                        grid: { display: false }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }
    
    // Pie Chart
    const pieCtx = document.getElementById('pieChart');
    if (pieCtx) {
        if (pieChart) pieChart.destroy();
        
        pieChart = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: getCssVar('--bg-card', '#ffffff')
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            color: getCssVar('--text-primary', getCssVar('--text', '#0f172a'))
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.label}: ${ctx.parsed}%`
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1000
                }
            }
        });
    }

    // Radar Chart
    const radarCtx = document.getElementById('radarChart');
    if (radarCtx) {
        if (radarChart) radarChart.destroy();

        radarChart = new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: labels.map((l, i) => `${emojis[i]} ${l}`),
                datasets: [{
                    label: 'Ықтималдық (%)',
                    data: data,
                    borderColor: '#5A6FF0',
                    backgroundColor: 'rgba(90, 111, 240, 0.18)',
                    borderWidth: 2,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: colors,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 1.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.parsed.r}%`
                        }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            color: getCssVar('--text-secondary', getCssVar('--text-muted', '#5b6478')),
                            callback: (value) => `${value}%`,
                            backdropColor: 'transparent'
                        },
                        grid: {
                            color: getCssVar('--border-color', 'rgba(15, 23, 42, 0.15)')
                        },
                        angleLines: {
                            color: getCssVar('--border-color', 'rgba(15, 23, 42, 0.15)')
                        },
                        pointLabels: {
                            color: getCssVar('--text-primary', getCssVar('--text', '#0f172a')),
                            font: {
                                size: 12
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }
}

/**
 * Update chart colors on theme change
 */
function updateChartColors() {
    const textColor = getCssVar('--text-primary', getCssVar('--text', '#0f172a'));
    const secondaryColor = getCssVar('--text-secondary', getCssVar('--text-muted', '#5b6478'));
    const gridColor = getCssVar('--border-color', 'rgba(15, 23, 42, 0.15)');
    
    if (barChart) {
        barChart.options.scales.x.ticks.color = secondaryColor;
        barChart.options.scales.y.ticks.color = secondaryColor;
        barChart.options.scales.y.grid.color = gridColor;
        barChart.update();
    }
    
    if (pieChart) {
        pieChart.options.plugins.legend.labels.color = textColor;
        pieChart.update();
    }

    if (radarChart) {
        radarChart.options.scales.r.ticks.color = secondaryColor;
        radarChart.options.scales.r.grid.color = gridColor;
        radarChart.options.scales.r.angleLines.color = gridColor;
        radarChart.options.scales.r.pointLabels.color = textColor;
        radarChart.update();
    }
}

/**
 * Update sentence analysis
 */
function updateSentenceAnalysis(sentenceResults) {
    const sentencesList = document.getElementById('sentencesList');
    if (!sentencesList) return;
    
    if (!sentenceResults || sentenceResults.length === 0) {
        sentencesList.innerHTML = '<p class="text-muted">Сөйлемдер табылмады</p>';
        return;
    }
    
    sentencesList.innerHTML = sentenceResults.map((result, index) => `
        <div class="sentence-item" style="animation: fadeInUp 0.3s ease ${index * 0.05}s both; border-left-color: ${getEmotionColor(result.emotion)}">
            <span class="sentence-text">${escapeHtml(result.text)}</span>
            <div class="sentence-emotion">
                <span class="sentence-emoji">${result.emoji}</span>
                <span class="sentence-confidence">${safeFormatPercent(result.confidence)}</span>
            </div>
        </div>
    `).join('');
}

/**
 * Get emotion color
 */
function getEmotionColor(emotion) {
    const colors = {
        'радость': '#FFD93D',
        'грусть': '#6B7AA1',
        'гнев': '#E74C3C',
        'страх': '#9B59B6',
        'удивление': '#3498DB',
        'отвращение': '#2ECC71',
        'нейтральный': '#95A5A6',
        'любовь': '#E91E63'
    };
    return colors[emotion] || '#95A5A6';
}

/**
 * Initialize chart tabs
 */
function initChartTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const barChartCanvas = document.getElementById('barChart');
    const pieChartCanvas = document.getElementById('pieChart');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const chartType = this.dataset.chart;
            
            // Update active tab
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Show/hide charts
            if (chartType === 'bar') {
                if (barChartCanvas) barChartCanvas.style.display = 'block';
                if (pieChartCanvas) pieChartCanvas.style.display = 'none';
            } else {
                if (barChartCanvas) barChartCanvas.style.display = 'none';
                if (pieChartCanvas) pieChartCanvas.style.display = 'block';
            }
        });
    });
}

/**
 * Initialize export buttons
 */
function initExportButtons() {
    const copyBtn = document.getElementById('copyResultBtn');
    const pngBtn = document.getElementById('exportPngBtn');
    const pdfBtn = document.getElementById('exportPdfBtn');
    
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const resultsContent = document.getElementById('resultsContent');
            if (resultsContent) {
                const text = extractResultsText();
                window.EmotionAI.copyToClipboard(text);
            }
        });
    }
    
    if (pngBtn) {
        pngBtn.addEventListener('click', () => {
            const resultsContent = document.getElementById('resultsContent');
            if (resultsContent) {
                window.EmotionAI.exportToPNG(resultsContent, 'emocija-taldauy.png');
            }
        });
    }
    
    if (pdfBtn) {
        pdfBtn.addEventListener('click', () => {
            window.EmotionAI.exportToPDF('Эмоция талдауы');
        });
    }
}

/**
 * Extract results text for copying
 */
function extractResultsText() {
    const primaryEmotion = document.getElementById('primaryEmotionName')?.textContent || '';
    const primaryPercentage = document.getElementById('primaryPercentage')?.textContent || '';
    
    let text = `Эмоция талдауы\n`;
    text += `================\n\n`;
    text += `Негізгі эмоция: ${primaryEmotion} (${primaryPercentage})\n\n`;
    text += `Барлық эмоциялар:\n`;
    
    const emotionItems = document.querySelectorAll('.emotion-item');
    emotionItems.forEach(item => {
        const name = item.querySelector('.emotion-label')?.textContent || '';
        const percent = item.querySelector('.emotion-percent')?.textContent || '';
        text += `- ${name}: ${percent}\n`;
    });
    
    return text;
}

/**
 * Initialize feedback buttons
 */
function initFeedbackButtons() {
    const positiveBtn = document.getElementById('feedbackPositive');
    const negativeBtn = document.getElementById('feedbackNegative');
    const feedbackComment = document.getElementById('feedbackComment');
    const submitFeedback = document.getElementById('submitFeedback');
    const feedbackText = document.getElementById('feedbackText');
    
    let selectedFeedback = null;
    
    if (positiveBtn) {
        positiveBtn.addEventListener('click', () => {
            selectedFeedback = 'positive';
            positiveBtn.classList.add('active');
            negativeBtn.classList.remove('active');
            if (feedbackComment) feedbackComment.style.display = 'block';
        });
    }
    
    if (negativeBtn) {
        negativeBtn.addEventListener('click', () => {
            selectedFeedback = 'negative';
            negativeBtn.classList.add('active');
            positiveBtn.classList.remove('active');
            if (feedbackComment) feedbackComment.style.display = 'block';
        });
    }
    
    if (submitFeedback) {
        submitFeedback.addEventListener('click', async () => {
            if (!selectedFeedback || !currentAnalysisId) return;
            
            try {
                await window.EmotionAI.apiCall('/api/feedback/', {
                    method: 'POST',
                    body: JSON.stringify({
                        analysis_id: currentAnalysisId,
                        feedback_type: selectedFeedback,
                        comment: feedbackText?.value || ''
                    })
                });
                
                window.EmotionAI.showToast('Кері байланыс үшін рахмет!', 'success');
                if (feedbackComment) feedbackComment.style.display = 'none';
                if (feedbackText) feedbackText.value = '';
                
            } catch (error) {
                window.EmotionAI.showToast('Қате: ' + error.message, 'error');
            }
        });
    }
}

/**
 * Clear all
 */
function clearAll() {
    const textInput = document.getElementById('textInput');
    const resultsSection = document.getElementById('resultsSection');
    
    if (textInput) {
        textInput.value = '';
        textInput.focus();
    }
    
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    
    updateStats();
    window.EmotionAI.showToast('Тазаланды', 'info');
}

/**
 * Load demo text
 */
function loadDemoText() {
    const textInput = document.getElementById('textInput');
    const languageSelect = document.getElementById('languageSelect');
    
    if (!textInput) return;
    
    // Check current language selection
    const lang = languageSelect?.value || 'auto';
    
    // Use demo texts defined in template
    let demoText = '';
    if (typeof demoTexts !== 'undefined') {
        if (lang === 'kk') {
            demoText = demoTexts.kk;
        } else if (lang === 'ru') {
            demoText = demoTexts.ru;
        } else {
            // Random or default
            demoText = demoTexts.kk;
        }
    } else {
        demoText = 'Бүгін керемет күн! Мен өте бақыттымын. Досыммен кездесіп, тамаша уақыт өткіздім.';
    }
    
    // Typewriter effect
    textInput.value = '';
    let i = 0;
    const typeInterval = setInterval(() => {
        textInput.value += demoText[i];
        i++;
        if (i >= demoText.length) {
            clearInterval(typeInterval);
            updateStats();
        }
    }, 20);
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
