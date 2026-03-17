/**
 * Emotion AI - Тарих бетінің скрипттері
 */

document.addEventListener('DOMContentLoaded', () => {
    initHistory();
});

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

function initHistory() {
    initDeleteButtons();
    initViewButtons();
    initClearAllButton();
    initEmotionDistributionChart();
}

function initDeleteButtons() {
    const deleteButtons = document.querySelectorAll('.delete-item');
    deleteButtons.forEach((btn) => {
        btn.addEventListener('click', async function () {
            const id = this.dataset.id;
            const item = this.closest('.history-item, .history-row');
            if (!id || !item) return;

            if (!confirm('Осы жазбаны жойғыңыз келе ме?')) return;

            try {
                await window.EmotionAI.apiCall(`/api/history/${id}/delete/`, { method: 'POST' });
                item.style.transition = 'all 0.3s ease';
                item.style.opacity = '0';
                item.style.transform = 'translateX(-100%)';
                setTimeout(() => {
                    item.remove();
                    updateStats();
                }, 300);
                window.EmotionAI.showToast('Жазба жойылды', 'success');
            } catch (error) {
                window.EmotionAI.showToast('Қате: ' + (error?.message || 'Сұраныс орындалмады'), 'error');
            }
        });
    });
}

function initViewButtons() {
    const viewButtons = document.querySelectorAll('.view-details');
    const modal = document.getElementById('detailsModal');
    const modalClose = document.getElementById('modalClose');
    const modalBody = document.getElementById('modalBody');

    viewButtons.forEach((btn) => {
        btn.addEventListener('click', async function () {
            const id = this.dataset.id;
            if (!id) return;

            if (modal) {
                modal.classList.add('active');
                if (modalBody) modalBody.innerHTML = '<div class="loading-spinner-small"></div>';
            }

            try {
                const response = await window.EmotionAI.apiCall(`/api/history/${id}/`);
                if (response?.success && response?.data && modalBody) {
                    const analysis = response.data;
                    const emotion = analysis.primary_emotion_label || analysis.primary_emotion || '-';
                    const confidence = Number.isFinite(Number(analysis.confidence)) ? Number(analysis.confidence) : 0;
                    const createdAt = analysis.created_at
                        ? new Date(analysis.created_at).toLocaleString('kk-KZ')
                        : '-';
                    const snippet = analysis.text_snippet || '-';

                    modalBody.innerHTML = `
                        <div class="detail-item">
                            <span class="detail-label">Эмоция:</span>
                            <span class="detail-value">${escapeHtml(emotion)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Сенімділік:</span>
                            <span class="detail-value">${safeFormatPercent(confidence)}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Уақыты:</span>
                            <span class="detail-value">${createdAt}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Мәтін:</span>
                            <p class="detail-text">${escapeHtml(snippet)}</p>
                        </div>
                    `;
                } else if (modalBody) {
                    modalBody.innerHTML = '<p class="error-text">Мәлімет табылмады</p>';
                }
            } catch (error) {
                if (modalBody) {
                    modalBody.innerHTML = `<p class="error-text">Жүктеу қатесі: ${escapeHtml(error?.message || 'белгісіз қате')}</p>`;
                }
            }
        });
    });

    if (modalClose) {
        modalClose.addEventListener('click', () => modal?.classList.remove('active'));
    }

    const modalOverlay = modal?.querySelector('.modal-overlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', () => modal?.classList.remove('active'));
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal?.classList.contains('active')) {
            modal.classList.remove('active');
        }
    });
}

function initClearAllButton() {
    const clearAllBtn = document.getElementById('clearAllBtn');
    if (!clearAllBtn) return;

    clearAllBtn.addEventListener('click', async () => {
        if (!confirm('Тарихтағы барлық жазбаны жойғыңыз келе ме?')) return;

        const historyItems = document.querySelectorAll('.history-item, .history-row');
        try {
            await window.EmotionAI.apiCall('/api/history/clear/', { method: 'POST' });

            historyItems.forEach((item, index) => {
                setTimeout(() => {
                    item.style.transition = 'all 0.3s ease';
                    item.style.opacity = '0';
                    item.style.transform = 'translateX(-100%)';
                    setTimeout(() => item.remove(), 300);
                }, index * 50);
            });

            setTimeout(() => location.reload(), historyItems.length * 50 + 500);
            window.EmotionAI.showToast('Тарих тазартылды', 'success');
        } catch (error) {
            window.EmotionAI.showToast('Қате: ' + (error?.message || 'Сұраныс орындалмады'), 'error');
        }
    });
}

function initEmotionDistributionChart() {
    const ctx = document.getElementById('emotionDistributionChart');
    if (!ctx || !window.Chart) return;
    if (typeof emotionDistribution === 'undefined' || !emotionDistribution) return;

    const emotions = Object.keys(emotionDistribution);
    const counts = Object.values(emotionDistribution);
    if (emotions.length === 0 || counts.length === 0) return;

    const colors = emotions.map(() => '#95A5A6');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: emotions,
            datasets: [{
                label: 'Саны',
                data: counts,
                backgroundColor: colors,
                borderRadius: 8,
                borderSkipped: false,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } },
                x: { grid: { display: false } },
            },
        },
    });
}

function updateStats() {
    const historyItems = document.querySelectorAll('.history-item, .history-row');
    const totalCount = document.getElementById('totalCount');

    if (totalCount && window.EmotionAI.animateCounter) {
        window.EmotionAI.animateCounter(totalCount, historyItems.length, 500, '');
    } else if (totalCount) {
        totalCount.textContent = String(historyItems.length);
    }

    if (historyItems.length === 0) {
        const historyList = document.querySelector('.history-list');
        if (historyList) {
            historyList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">Дерек жоқ</div>
                    <h3>Тарих бос</h3>
                    <p>Әзірге талдау жазбалары жоқ.</p>
                </div>
            `;
        }
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text ?? '';
    return div.innerHTML;
}
