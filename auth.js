// Magic-link sign-in via Supabase. Requires site-config.js values.
const API_BASE = window.API_BASE || 'https://igiari-backend.onrender.com';

let supabaseClient = null;
let currentSession = null;

function authConfigured() {
    return Boolean(window.IGIARI_SUPABASE_URL && window.IGIARI_SUPABASE_ANON_KEY);
}

function getAccessToken() {
    return currentSession?.access_token || null;
}

async function initAuth() {
    const section = document.getElementById('authSection');
    if (!authConfigured()) {
        if (section) {
            section.classList.add('hidden');
        }
        return;
    }

    if (section) {
        section.classList.remove('hidden');
    }

    supabaseClient = window.supabase.createClient(
        window.IGIARI_SUPABASE_URL,
        window.IGIARI_SUPABASE_ANON_KEY
    );

    const params = new URLSearchParams(window.location.hash.replace(/^#/, '?'));
    if (params.get('access_token')) {
        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');
        if (accessToken && refreshToken) {
            await supabaseClient.auth.setSession({
                access_token: accessToken,
                refresh_token: refreshToken,
            });
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }

    const { data } = await supabaseClient.auth.getSession();
    currentSession = data.session;
    updateAuthUI();

    supabaseClient.auth.onAuthStateChange((_event, session) => {
        currentSession = session;
        updateAuthUI();
    });

    document.getElementById('signInButton')?.addEventListener('click', handleSignIn);
    document.getElementById('signOutButton')?.addEventListener('click', handleSignOut);
}

async function handleSignIn() {
    const emailInput = document.getElementById('authEmail');
    const statusEl = document.getElementById('authStatus');
    const email = emailInput?.value.trim();

    if (!email) {
        statusEl.textContent = 'Enter your email address.';
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
    await supabaseClient.auth.signOut();
    currentSession = null;
    updateAuthUI();
}

async function fetchAccount() {
    const token = getAccessToken();
    if (!token) {
        return null;
    }

    const response = await fetch(`${API_BASE}/api/account/me`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        return null;
    }

    return response.json();
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
        if (statusEl) {
            statusEl.textContent = '';
        }
        return;
    }

    signedOut?.classList.add('hidden');
    signedIn?.classList.remove('hidden');

    const account = await fetchAccount();
    if (account && balanceEl) {
        balanceEl.textContent = `${account.credit_balance} scans left`;
    }
}

document.addEventListener('DOMContentLoaded', initAuth);
window.getAccessToken = getAccessToken;
window.updateAuthUI = updateAuthUI;
