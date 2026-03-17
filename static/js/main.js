document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initMobileMenu();
  initSmoothScroll();
});

function initThemeToggle() {
  const btn = document.getElementById('themeToggle');
  const html = document.documentElement;
  const saved = localStorage.getItem('theme') || 'light';
  html.setAttribute('data-theme', saved);

  btn?.addEventListener('click', () => {
    const next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: next } }));
  });
}

function initMobileMenu() {
  const btn = document.getElementById('mobileMenuBtn');
  const menu = document.getElementById('mobileMenu');
  btn?.addEventListener('click', () => menu.classList.toggle('show'));
}

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

function showToast(message, type = 'info', duration = 3000) {
  const box = document.getElementById('toastContainer');
  if (!box) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${message}</span><button class="toast-close" aria-label="Жабу">&times;</button>`;
  toast.querySelector('.toast-close').onclick = () => toast.remove();
  box.appendChild(toast);

  setTimeout(() => toast.remove(), duration);
}

function showLoading(text = 'Мәтін талданып жатыр...') {
  const overlay = document.getElementById('loadingOverlay');
  const t = overlay?.querySelector('.loading-text');
  if (!overlay) return;

  overlay.classList.add('active');
  if (t) t.textContent = text;

  const bar = document.getElementById('progressBar');
  if (bar) bar.style.width = '0%';
}

function hideLoading() {
  document.getElementById('loadingOverlay')?.classList.remove('active');
}

function updateProgress(p) {
  const bar = document.getElementById('progressBar');
  if (bar) bar.style.width = `${p}%`;
}

function formatPercent(value) {
  const n = Number(value);
  if (Number.isNaN(n)) return '0%';
  const pct = n <= 1 ? n * 100 : n;
  return `${pct.toFixed(1)}%`;
}

async function apiCall(url, options = {}) {
  const defaults = {
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
  };

  const res = await fetch(url, { ...defaults, ...options });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Сервер қатесі');
  return data;
}

function getCookie(name) {
  const v = document.cookie.match(`(^|;)\\s*${name}\\s*=\\s*([^;]+)`);
  return v ? v.pop() : '';
}

const storage = {
  set: (k, v) => localStorage.setItem(k, JSON.stringify(v)),
  get: (k, d = null) => {
    try {
      return JSON.parse(localStorage.getItem(k)) ?? d;
    } catch {
      return d;
    }
  },
  remove: (k) => localStorage.removeItem(k),
};

window.EmotionAI = {
  showToast,
  showLoading,
  hideLoading,
  updateProgress,
  formatPercent,
  apiCall,
  storage,
};
