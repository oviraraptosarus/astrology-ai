/**
 * auth.js — Authentication Module
 * Phase 5: Frontend ES6 Module Split
 * 
 * Handles: auth state, token management, login/logout UI
 * Uses HttpOnly cookies (the server sets them), but keeps the token in
 * memory as a fallback for Authorization headers on older API calls.
 * 
 * The server now sets HttpOnly cookies, so JS cannot read them directly.
 * Instead of localStorage, we use a module-level variable + /api/auth/me
 * to verify session on page load.
 */

// Module-level auth state (not in localStorage = XSS-safe)
let _currentUser = null;
let _sessionId = null;

/**
 * Initialize auth state by calling /api/auth/me.
 * Since the HttpOnly cookie is sent automatically by the browser,
 * we don't need to read any token from JS. Just check if the server
 * validates the session.
 */
export async function initAuth() {
    try {
        const res = await fetch('/api/auth/me', { credentials: 'include' });
        if (res.ok) {
            _currentUser = await res.json();
            updateUserUI(_currentUser);
            return true;
        } else {
            // Not logged in — redirect to login page
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
            return false;
        }
    } catch (e) {
        console.error('Auth check failed:', e);
        return false;
    }
}

export function getCurrentUser() {
    return _currentUser;
}

export function getSessionId() {
    if (!_sessionId) {
        _sessionId = sessionStorage.getItem('astro_session') || generateUUID();
        sessionStorage.setItem('astro_session', _sessionId);
    }
    return _sessionId;
}

export async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
    } catch (e) {
        console.error('Logout error:', e);
    } finally {
        _currentUser = null;
        _sessionId = null;
        sessionStorage.removeItem('astro_session');
        window.location.href = '/login';
    }
}

function updateUserUI(user) {
    const nameEl = document.getElementById('userName');
    const planEl = document.getElementById('userPlan');
    if (nameEl) nameEl.textContent = user.full_name || user.email;
    if (planEl) planEl.textContent = user.plan || 'free';
}

function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = Math.random() * 16 | 0;
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
}

// Expose logout globally for onclick handlers in HTML
window.logout = logout;
