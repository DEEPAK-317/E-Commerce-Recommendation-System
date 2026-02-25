/* ═══════════════════════════════════════════════════════
   ShopWiz — main.js  (Client-side interactivity)
═══════════════════════════════════════════════════════ */

// ── Theme ─────────────────────────────────────────────
const html = document.documentElement;
const themeBtn = document.getElementById('themeToggle');

function applyTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('sw-theme', theme);
    if (themeBtn) {
        themeBtn.querySelector('i').className =
            theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    }
}

(function initTheme() {
    const saved = localStorage.getItem('sw-theme') ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    applyTheme(saved);
})();

if (themeBtn) {
    themeBtn.addEventListener('click', () => {
        applyTheme(html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    });
}

// ── Navbar scroll ─────────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 10);
    document.getElementById('backToTop').classList.toggle('show', window.scrollY > 400);
}, { passive: true });

// ── Back to top ───────────────────────────────────────
const btt = document.getElementById('backToTop');
if (btt) btt.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// ── Hamburger ─────────────────────────────────────────
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
if (hamburger) {
    hamburger.addEventListener('click', () => mobileMenu.classList.toggle('open'));
}

// ── Search suggestions (navbar) ───────────────────────
const searchInput = document.getElementById('searchInput');
const searchSuggestions = document.getElementById('searchSuggestions');

if (searchInput) {
    let debounce;
    searchInput.addEventListener('input', function () {
        clearTimeout(debounce);
        const q = this.value.trim();
        if (q.length < 2) {
            searchSuggestions.innerHTML = '';
            searchSuggestions.classList.remove('show');
            return;
        }
        debounce = setTimeout(async () => {
            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
                const data = await res.json();
                if (data.length) {
                    searchSuggestions.innerHTML = data
                        .map(name => `<div class="sugg-item"
              onclick="window.location='/product/${encodeURIComponent(name)}'">${name}</div>`)
                        .join('');
                    searchSuggestions.classList.add('show');
                } else {
                    searchSuggestions.innerHTML = '';
                    searchSuggestions.classList.remove('show');
                }
            } catch (e) { }
        }, 250);
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
            searchSuggestions.classList.remove('show');
        }
    });
}

// ── Cart (localStorage) ───────────────────────────────
function getCart() {
    return JSON.parse(localStorage.getItem('sw-cart') || '[]');
}
function saveCart(cart) {
    localStorage.setItem('sw-cart', JSON.stringify(cart));
}
function showCartNotif(name) {
    const el = document.createElement('div');
    el.className = 'cart-notif';
    el.innerHTML = `<i class="bi bi-bag-check-fill"></i><span><strong>${name.substring(0, 28)}…</strong> added to cart!</span>`;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 2800);
}

document.addEventListener('click', function (e) {
    const btn = e.target.closest('.add-cart-btn');
    if (!btn) return;
    const name = btn.dataset.name;
    const price = parseFloat(btn.dataset.price);
    const cart = getCart();
    const idx = cart.findIndex(i => i.name === name);
    if (idx >= 0) cart[idx].qty += 1;
    else cart.push({ name, price, qty: 1 });
    saveCart(cart);
    btn.classList.add('adding');
    setTimeout(() => btn.classList.remove('adding'), 300);
    showCartNotif(name);
});

// ── Wishlist (API) ────────────────────────────────────
document.addEventListener('click', async function (e) {
    const btn = e.target.closest('.wishlist-btn');
    if (!btn) return;
    const name = btn.dataset.name;
    try {
        const res = await fetch('/api/wishlist/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (res.status === 401) {
            // Not logged in — redirect
            showToast('Please log in to use Wishlist', 'info');
            return;
        }
        const data = await res.json();
        const icon = btn.querySelector('i');
        if (data.status === 'added') {
            btn.classList.add('active');
            icon.className = 'bi bi-heart-fill';
            showToast('Added to wishlist ❤️', 'success');
        } else {
            btn.classList.remove('active');
            icon.className = 'bi bi-heart';
            showToast('Removed from wishlist', 'info');
        }
    } catch (e) { }
});

// ── Toast helper ──────────────────────────────────────
function showToast(message, category = 'info') {
    const icons = { success: 'bi-check-circle', error: 'bi-x-circle', info: 'bi-info-circle' };
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${category}`;
    toast.innerHTML = `
    <i class="bi ${icons[category] || 'bi-info-circle'}"></i>
    <span>${message}</span>
    <button onclick="this.parentElement.remove()"><i class="bi bi-x"></i></button>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ── Auto-dismiss flash toasts ─────────────────────────
document.querySelectorAll('.toast').forEach(t => {
    setTimeout(() => t.remove(), 4000);
});

// ── Animate cards on scroll (Intersection Observer) ───
const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
        if (e.isIntersecting) {
            e.target.style.opacity = '1';
            e.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.product-card, .feature-card, .category-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity .5s ease, transform .5s ease';
    observer.observe(el);
});
