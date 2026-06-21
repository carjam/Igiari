// Magic-link sign-in via Supabase. Requires site-config.js values.
const API_BASE = window.API_BASE || 'https://igiari-backend.onrender.com';
const FETCH_TIMEOUT_MS = 15000;

let supabaseClient = null;
let currentSession = null;

function authConfigured() {
    return Boolean(window.IGIARI_SUPABASE_URL && window.IGIARI_SUPABASE_ANON_KEY);
}

function getAccessToken() {
    return currentSession?.access_token || null;
}

function fetchWithTimeout(url, options = {}, timeoutMs = FETCH_TIMEOUT_MS) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    return fetch(url, { ...options, signal: controller.signal })
        .finally(() => clearTimeout(timer));
}

function bindAuthControls() {
    document.getElementById('signInButton')?.addEventListener('click', handleSignIn);
    document.getElementById('signOutButton')?.addEventListener('click', handleSignOut);
}

async function restoreSessionFromUrl() {
    const queryParams = new URLSearchParams(window.location.search);
    const code = queryParams.get('code');

    if (code) {
        const { error } = await supabaseClient.auth.exchangeCodeForSession(code);
        if (error) {
            throw error;
        }
        window.history.replaceState({}, document.title, window.location.pathname);
        return;
    }

    const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, '?'));
    const accessToken = hashParams.get('access_token');
    const refreshToken = hashParams.get('refresh_token');

    if (accessToken && refreshToken) {
        const { error } = await supabaseClient.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken,
        });
        if (error) {
            throw error;
        }
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

async function initAuth() {
    const section = document.getElementById('authSection');
    const statusEl = document.getElementById('authStatus');

    if (!authConfigured()) {
        section?.classList.add('hidden');
        return;
    }

    section?.classList.remove('hidden');
    bindAuthControls();

    if (!window.supabase) {
        if (statusEl) {
            statusEl.textContent = 'Sign-in failed to load. Try disabling ad blockers and refresh.';
        }
        return;
    }

    supabaseClient = window.supabase.createClient(
        window.IGIARI_SUPABASE_URL,
        window.IGIARI_SUPABASE_ANON_KEY,
        {
            auth: {
                detectSessionInUrl: true,
                persistSession: true,
                flowType: 'pkce',
            },
        }
    );

    try {
        await restoreSessionFromUrl();
    } catch (error) {
        console.error('Sign-in redirect failed:', error);
        if (statusEl) {
            statusEl.textContent = error.message || 'Sign-in link expired. Request a new one.';
        }
    }

    const { data } = await supabaseClient.auth.getSession();
    currentSession = data.session;
    void updateAuthUI();

    supabaseClient.auth.onAuthStateChange((_event, session) => {
        currentSession = session;
        void updateAuthUI();
    });
}

async function handleSignIn() {
    const emailInput = document.getElementById('authEmail');
    const statusEl = document.getElementById('authStatus');
    const email = emailInput?.value.trim();

    if (!email) {
        statusEl.textContent = 'Enter your email address.';
        return;
    }

    if (!supabaseClient) {
        statusEl.textContent = 'Sign-in is not ready yet. Refresh and try again.';
        return;
    }

    statusEl.textContent = 'Sending sign-in link…';

    const { error } = await supabaseClient.auth.signInWithOtp({
        email,
        options: {
            emailRedirectTo: window.location.origin + window.location.pathname,
        },
    });

    if (error) {
        statusEl.textContent = error.message;
        return;
    }

    statusEl.textContent = 'Check your email for a sign-in link.';
}

async function handleSignOut() {
    currentSession = null;
    void updateAuthUI();

    if (!supabaseClient) {
        return;
    }

    try {
        await supabaseClient.auth.signOut();
    } catch (error) {
        console.error('Sign out failed:', error);
    }

    currentSession = null;
    void updateAuthUI();
}

async function fetchAccount() {
    const token = getAccessToken();
    if (!token) {
        return { error: 'Not signed in.' };
    }

    try {
        const response = await fetchWithTimeout(`${API_BASE}/api/account/me`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        let data = {};
        try {
            data = await response.json();
        } catch (_error) {
            return { error: 'Could not read account response from server.' };
        }

        if (!response.ok) {
            const detail = data.detail || {};
            const message = typeof detail === 'string'
                ? detail
                : (detail.message || 'Could not load your account.');
            return { error: message };
        }

        return { account: data };
    } catch (error) {
        if (error.name === 'AbortError') {
            return { error: 'Loading account timed out. Try again in a moment.' };
        }
        return { error: 'Could not reach the server.' };
    }
}

async function updateAuthUI() {
    const signedOut = document.getElementById('authSignedOut');
    const signedIn = document.getElementById('authSignedIn');
    const balanceEl = document.getElementById('creditBalance');
    const statusEl = document.getElementById('authStatus');

    if (!currentSession) {
        signedOut?.classList.remove('hidden');
        signedIn?.classList.add('hidden');
        if (balanceEl) {
            balanceEl.textContent = '';
        }
        return;
    }

    signedOut?.classList.add('hidden');
    signedIn?.classList.remove('hidden');

    if (balanceEl) {
        balanceEl.textContent = 'Loading scans…';
    }

    const result = await fetchAccount();
    if (result.account && balanceEl) {
        balanceEl.textContent = `${result.account.credit_balance} scans left`;
        if (statusEl) {
            statusEl.textContent = '';
        }
        return;
    }

    if (balanceEl) {
        balanceEl.textContent = 'Balance unavailable';
    }
    if (statusEl && result.error) {
        statusEl.textContent = result.error;
    }
}

document.addEventListener('DOMContentLoaded', initAuth);
window.getAccessToken = getAccessToken;
window.updateAuthUI = updateAuthUI;
