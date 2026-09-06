/**
 * api.js — API Communication Module  
 * Phase 5: Frontend ES6 Module Split + Phase 3: SSE Streaming
 * 
 * Handles: all fetch calls to backend APIs
 * Key feature: fetchChatStream() uses SSE to stream agent thoughts live,
 * eliminating the silent 60-90s loading screen.
 */

import { getSessionId } from './auth.js';

/**
 * Base fetch wrapper — automatically includes credentials (HttpOnly cookie)
 * and proper headers. No more manual Authorization header management.
 */
async function apiFetch(url, options = {}) {
    const defaults = {
        credentials: 'include',  // Always send HttpOnly cookie
        headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
    };
    const merged = { ...defaults, ...options, headers: { ...defaults.headers, ...(options.headers || {}) } };
    const res = await fetch(url, merged);
    if (res.status === 401) {
        // Session expired — redirect to login
        window.location.href = '/login';
        throw new Error('Session expired');
    }
    return res;
}

/**
 * Standard (non-streaming) chat. Kept for backward compatibility.
 */
export async function sendChat(message, provider = 'auto') {
    const session_id = getSessionId();
    const res = await apiFetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message, session_id, provider })
    });
    if (!res.ok) throw new Error(`Chat API error: ${res.status}`);
    return await res.json();
}

/**
 * Phase 3: SSE Streaming Chat
 * 
 * Returns an EventSource-like async generator that yields parsed event objects.
 * The server streams agent thought steps in real-time.
 * 
 * Usage:
 *   for await (const event of fetchChatStream(message)) {
 *     if (event.type === 'thinking') showThought(event.content);
 *     if (event.type === 'final') showAnswer(event.content);
 *   }
 */
export async function* fetchChatStream(message, provider = 'auto') {
    const session_id = getSessionId();
    const params = new URLSearchParams({ message, session_id, provider });
    
    // Use fetch with ReadableStream for SSE — works with credentials (cookies)
    // EventSource does NOT support credentials/cookies, so we use fetch instead
    const res = await fetch(`/api/chat/stream?${params}`, {
        credentials: 'include',
        headers: { 'Accept': 'text/event-stream' }
    });
    
    if (!res.ok) {
        throw new Error(`Stream error: ${res.status}`);
    }
    
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep incomplete line in buffer
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const jsonStr = line.slice(6).trim();
                if (!jsonStr) continue;
                try {
                    const event = JSON.parse(jsonStr);
                    yield event;
                    if (event.type === 'done' || event.type === 'final' || event.type === 'error') {
                        return;
                    }
                } catch (e) {
                    console.warn('Failed to parse SSE event:', jsonStr);
                }
            }
        }
    }
}

/**
 * Fetch and calculate a birth chart.
 */
export async function calculateChart(chartData) {
    const res = await apiFetch('/api/chart/calculate', {
        method: 'POST',
        body: JSON.stringify(chartData)
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Chart calculation failed');
    }
    return await res.json();
}

/**
 * Fetch chart data for rendering.
 */
export async function getChartData(sessionId) {
    const res = await apiFetch(`/api/chart-data?session_id=${sessionId}`);
    if (res.status === 404) return null;
    if (!res.ok) throw new Error('Failed to fetch chart data');
    return await res.json();
}

/**
 * Check if chart exists.
 */
export async function checkChartStatus(sessionId) {
    const res = await apiFetch(`/api/chart/status?session_id=${sessionId}`);
    if (!res.ok) return { has_chart: false };
    return await res.json();
}

/**
 * Save user birth profile.
 */
export async function saveProfile(profileData) {
    const res = await apiFetch('/api/profile', {
        method: 'POST',
        body: JSON.stringify(profileData)
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Profile save failed');
    }
    return await res.json();
}

/**
 * Get user birth profile.
 */
export async function getProfile() {
    const res = await apiFetch('/api/profile');
    if (res.status === 404) return null;
    if (!res.ok) throw new Error('Failed to fetch profile');
    return await res.json();
}

/**
 * Fetch timezone for coordinates.
 */
export async function getTimezone(lat, lon) {
    const res = await apiFetch(`/api/location/timezone?lat=${lat}&lon=${lon}`);
    if (!res.ok) throw new Error('Timezone fetch failed');
    return await res.json();
}

/**
 * Fetch available AI models.
 */
export async function fetchModels() {
    const res = await fetch('/api/models'); // Public endpoint
    if (!res.ok) return { models: [] };
    return await res.json();
}
