// Magic-link sign-in via Supabase. Requires site-config.js values.
const FETCH_TIMEOUT_MS = 15000;
const LAST_EMAIL_KEY = 'igiari_last_email';

function apiBase() {
    return window.API_BASE || 'https://igiari-backend.onrender.com';
}

let supabaseClient = null;
let currentSession = null;
let ignoreAuthEvents = false;
let authUiRequestId = 0;

function authConfigured() {
    return Boolean(window.IGIARI_SUPABASE_URL && window.IGIARI_SUPABASE_ANON_KEY);
}

function signInRequired() {
    return authConfigured();
}

function getAccessToken() {
    return currentSession?.access_token || null;
}

function isSignedIn() {
    return Boolean(currentSession);
}

function rememberEmail(email) {
    if (email) {
        localStorage.setItem(LAST_EMAIL_KEY, email);
    }
}

function prefillEmail() {
    const input = document.getElementById('authEmail');
    if (!input || input.value) {
        return;
    }
    const saved = localStorage.getItem(LAST_EMAIL_KEY);
    if (saved) {
        input.value = saved;
    }
}

function refreshScanControls() {
    if (window.updateScanButton) {
        window.updateScanButton();
    }
}

function formatAuthError(error) {
    const message = error?.message || 'Sign-in failed. Please try again.';
    if (/rate limit/i.test(message)) {
        return 'Too many sign-in emails sent. Use the 6-digit code from your latest email instead.';
    }
    if (/code verifier|pkce|invalid flow state|both auth code and code verifier/i.test(message)) {
        return 'That link did not match this browser session. Enter the 6-digit code from your email below, or paste the link into this tab.';
    }
    return message;
}

function clearAuthCallbackFromUrl() {
    window.history.replaceState({}, document.title, window.location.pathname);
}

async function completeAuthFromUrl(statusEl) {
    const url = new URL(window.location.href);
    const authError = url.searchParams.get('error_description') || url.searchParams.get('error');
    if (authError) {
        const message = decodeURIComponent(authError.replace(/\+/g, ' '));
        if (statusEl) {
            statusEl.textContent = message;
        }
        clearAuthCallbackFromUrl();
        return false;
    }

    const hashParams = new URLSearchParams(url.hash.replace(/^#/, '?'));
    const accessToken = hashParams.get('access_token');
    const refreshToken = hashParams.get('refresh_token');
    if (accessToken && refreshToken) {
        if (statusEl) {
            statusEl.textContent = 'Completing sign-in…';
        }
        const { data, error } = await supabaseClient.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken,
        });
        clearAuthCallbackFromUrl();
        if (error) {
            if (statusEl) {
                statusEl.textContent = formatAuthError(error);
            }
            return false;
        }
        if (data.session) {
            applySession(data.session);
            return true;
        }
    }

    const code = url.searchParams.get('code');
    if (code) {
        if (statusEl) {
            statusEl.textContent = 'Completing sign-in…';
        }
        const { data, error } = await supabaseClient.auth.exchangeCodeForSession(code);
        clearAuthCallbackFromUrl();
        if (error) {
            if (statusEl) {
                statusEl.textContent = formatAuthError(error);
            }
            return false;
        }
        if (data.session) {
            applySession(data.session);
            return true;
        }
    }

    return false;
}

function fetchWithTimeout(url, options = {}, timeoutMs = FETCH_TIMEOUT_MS) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    return fetch(url, { ...options, signal: controller.signal })
        .finally(() => clearTimeout(timer));
}

function bindAuthButtons() {
    document.getElementById('signInButton')?.addEventListener('click', (event) => {
        event.preventDefault();
        void handleSignIn();
    });
    document.getElementById('signOutButton')?.addEventListener('click', (event) => {
        event.preventDefault();
        void handleSignOut();
    });
    document.getElementById('authEmail')?.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            void handleSignIn();
        }
    });
    document.getElementById('verifyOtpButton')?.addEventListener('click', (event) => {
        event.preventDefault();
        void handleVerifyOtp();
    });
    document.getElementById('authOtp')?.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            void handleVerifyOtp();
        }
    });
}

function applySession(session) {
    currentSession = session;
    if (session?.user?.email) {
        rememberEmail(session.user.email);
    }
    void updateAuthUI();
}

async function initAuth() {
    const section = document.getElementById('authSection');
    const statusEl = document.getElementById('authStatus');

    if (!authConfigured()) {
        section?.classList.add('hidden');
        return;
    }

    section?.classList.remove('hidden');
    bindAuthButtons();

    if (!window.supabase) {
        if (statusEl) {
            statusEl.textContent = 'Sign-in failed to load. Try disabling ad blockers and refresh.';
        }
        return;
    }

    // Implicit flow: magic links return tokens in the URL hash (no PKCE verifier needed).
    supabaseClient = window.supabase.createClient(
        window.IGIARI_SUPABASE_URL,
        window.IGIARI_SUPABASE_ANON_KEY,
        {
            auth: {
                autoRefreshToken: true,
                detectSessionInUrl: false,
                persistSession: true,
                flowType: 'implicit',
                storage: window.localStorage,
            },
        }
    );

    supabaseClient.auth.onAuthStateChange((event, session) => {
        if (ignoreAuthEvents) {
            return;
        }
        applySession(session);
    });

    try {
        await completeAuthFromUrl(statusEl);
    } catch (error) {
        console.error('Sign-in redirect failed:', error);
        if (statusEl) {
            statusEl.textContent = formatAuthError(error);
        }
    }

    if (!currentSession) {
        const { data, error: sessionError } = await supabaseClient.auth.getSession();
        if (sessionError) {
            console.error('Session restore failed:', sessionError);
        }
        applySession(data.session ?? null);
    }

    prefillEmail();
}

async function handleSignIn() {
    const emailInput = document.getElementById('authEmail');
    const statusEl = document.getElementById('authStatus');
    const email = emailInput?.value.trim();

    if (!email) {
        if (statusEl) {
            statusEl.textContent = 'Enter your email address.';
        }
        return;
    }

    if (!supabaseClient) {
        if (statusEl) {
            statusEl.textContent = 'Sign-in is not ready yet. Refresh and try again.';
        }
        return;
    }

    if (statusEl) {
        statusEl.textContent = 'Sending sign-in link…';
    }

    const { error } = await supabaseClient.auth.signInWithOtp({
        email,
        options: {
            emailRedirectTo: window.location.origin,
        },
    });

    rememberEmail(email);

    if (error) {
        if (statusEl) {
            statusEl.textContent = formatAuthError(error);
        }
        return;
    }

    if (statusEl) {
        statusEl.textContent = 'Check your email. Click the link, or enter the 6-digit code below.';
    }
}

async function handleVerifyOtp() {
    const emailInput = document.getElementById('authEmail');
    const otpInput = document.getElementById('authOtp');
    const statusEl = document.getElementById('authStatus');
    const email = emailInput?.value.trim();
    const token = otpInput?.value.trim().replace(/\s/g, '');

    if (!email) {
        if (statusEl) {
            statusEl.textContent = 'Enter your email address.';
        }
        return;
    }

    if (!token) {
        if (statusEl) {
            statusEl.textContent = 'Enter the 6-digit code from your email.';
        }
        return;
    }

    if (!supabaseClient) {
        if (statusEl) {
            statusEl.textContent = 'Sign-in is not ready yet. Refresh and try again.';
        }
        return;
    }

    rememberEmail(email);

    if (statusEl) {
        statusEl.textContent = 'Verifying code…';
    }

    const { data, error } = await supabaseClient.auth.verifyOtp({
        email,
        token,
        type: 'email',
    });

    if (error) {
        if (statusEl) {
            statusEl.textContent = formatAuthError(error);
        }
        return;
    }

    if (otpInput) {
        otpInput.value = '';
    }
    applySession(data.session);
}

async function handleSignOut() {
    ignoreAuthEvents = true;
    currentSession = null;
    void updateAuthUI();

    if (supabaseClient) {
        try {
            await supabaseClient.auth.signOut();
        } catch (error) {
            console.error('Sign out failed:', error);
        }
    }

    ignoreAuthEvents = false;
    void updateAuthUI();
}

async function fetchAccount() {
    const token = getAccessToken();
    if (!token) {
        return { error: 'Not signed in.' };
    }

    try {
        const response = await fetchWithTimeout(`${apiBase()}/api/account/me`, {
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
                : (detail.message || `Server error (${response.status}).`);
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
        refreshScanControls();
        return;
    }

    signedOut?.classList.add('hidden');
    signedIn?.classList.remove('hidden');

    if (balanceEl) {
        balanceEl.textContent = 'Loading scans…';
    }
    if (statusEl) {
        statusEl.textContent = '';
    }

    const requestId = ++authUiRequestId;
    const result = await fetchAccount();
    if (requestId !== authUiRequestId || !currentSession) {
        return;
    }
    if (result.account && balanceEl) {
        balanceEl.textContent = `${result.account.credit_balance} scans left`;
        refreshScanControls();
        return;
    }

    if (balanceEl) {
        balanceEl.textContent = result.error || 'Balance unavailable';
    }
    refreshScanControls();
}

document.addEventListener('DOMContentLoaded', initAuth);
window.getAccessToken = getAccessToken;
window.signInRequired = signInRequired;
window.isSignedIn = isSignedIn;
window.updateAuthUI = updateAuthUI;
window.handleSignIn = handleSignIn;
window.handleSignOut = handleSignOut;
