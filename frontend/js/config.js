// API Base URL — empty string means same origin (frontend served by FastAPI at :8000)
const API_BASE = '';

// Helper: make authenticated API calls
async function apiCall(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    const response = await fetch(`${API_BASE}${endpoint}`, options);

    if (response.status === 401) {
        localStorage.clear();
        const loginPath = window.location.pathname.includes('/pages/')
            ? '../index.html'
            : 'index.html';
        window.location.href = loginPath;
        return;
    }

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong');
    }
    return data;
}

// Upload file (for photos — no JSON content-type)
async function apiUpload(endpoint, formData) {
    const token = localStorage.getItem('token');
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers,
        body: formData
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Upload failed');
    }
    return data;
}

// Check auth — redirect to login if not authenticated
function requireAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '../index.html';
        return null;
    }
    return token;
}

// Get stored user info
function getStoredUser() {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
}

// Format date as DD/MM/YYYY (Indian format)
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

// Show toast notification
function showToast(message, type = 'success') {
    const existing = document.getElementById('toast-notification');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'toast-notification';
    toast.style.cssText = `
        position: fixed; bottom: 1.5rem; right: 1.5rem;
        padding: 1rem 1.5rem; border-radius: 0.75rem;
        font-size: 0.9rem; font-weight: 500;
        z-index: 9999; max-width: 350px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease;
        color: white;
        background: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#F59E0B'};
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; }, 3000);
    setTimeout(() => toast.remove(), 3300);
}

// Logout
function logout() {
    localStorage.clear();
    window.location.href = '../index.html';
}
