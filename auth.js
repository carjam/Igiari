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
let billingProducts = [];
let lastAccount = null;

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
    if (/invalid|expired|already been used/i.test(message)) {
        return 'That code or link has expired or was already used. Request a new sign-in email and try again without clicking the link first — use the code only.';
    }
    if (/code verifier|pkce|invalid flow state|both auth code and code verifier/i.test(message)) {
        return 'That link did not match this browser session. Enter the 6-digit code from your email below instead.';
    }
    return message;
}

function clearAuthCallbackFromUrl() {
    window.history.replaceState({}, document.title, window.location.pathname);
}

async function verifyOtpFromParams(params, statusEl) {
    const tokenHash = params.get('token_hash');
    if (tokenHash) {
        const type = params.get('type') === 'magiclink' ? 'email' : (params.get('type') || 'email');
        const { data, error } = await supabaseClient.auth.verifyOtp({
            token_hash: tokenHash,
            type,
        });
        return { data, error };
    }

    return { data: null, error: null };
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

    if (url.searchParams.get('token_hash')) {
        if (statusEl) {
            statusEl.textContent = 'Completing sign-in…';
        }
        ignoreAuthEvents = true;
        const { data, error } = await verifyOtpFromParams(url.searchParams, statusEl);
        ignoreAuthEvents = false;
        clearAuthCallbackFromUrl();
        if (error) {
            if (statusEl) {
                statusEl.textContent = formatAuthError(error);
            }
            return false;
        }
        if (data?.session) {
            applySession(data.session);
            return true;
        }
    }

    const hashParams = new URLSearchParams(url.hash.replace(/^#/, '?'));
    if (hashParams.get('token_hash')) {
        if (statusEl) {
            statusEl.textContent = 'Completing sign-in…';
        }
        ignoreAuthEvents = true;
        const { data, error } = await verifyOtpFromParams(hashParams, statusEl);
        ignoreAuthEvents = false;
        clearAuthCallbackFromUrl();
        if (error) {
            if (statusEl) {
                statusEl.textContent = formatAuthError(error);
            }
            return false;
        }
        if (data?.session) {
            applySession(data.session);
            return true;
        }
    }

    const accessToken = hashParams.get('access_token');
    const refreshToken = hashParams.get('refresh_token');
    if (accessToken && refreshToken) {
        if (statusEl) {
            statusEl.textContent = 'Completing sign-in…';
        }
        ignoreAuthEvents = true;
        const { data, error } = await supabaseClient.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken,
        });
        ignoreAuthEvents = false;
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
        ignoreAuthEvents = true;
        const { data, error } = await supabaseClient.auth.exchangeCodeForSession(code);
        ignoreAuthEvents = false;
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
    document.getElementById('billingPortalButton')?.addEventListener('click', (event) => {
        event.preventDefault();
        void handleBillingPortal();
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

    supabaseClient = window.supabase.createClient(
        window.IGIARI_SUPABASE_URL,
        window.IGIARI_SUPABASE_ANON_KEY,
        {
            auth: {
                autoRefreshToken: true,
                detectSessionInUrl: false,
                persistSession: true,
                flowType: 'pkce',
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
    handleCheckoutReturn();
    void loadBillingProducts();
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
    if (!data?.session) {
        if (statusEl) {
            statusEl.textContent = 'Sign-in succeeded but no session was returned. Try again.';
        }
        return;
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

async function fetchBillingProducts() {
    try {
        const response = await fetchWithTimeout(`${apiBase()}/api/billing/products`);
        if (!response.ok) {
            return [];
        }
        const data = await response.json();
        return data.products || [];
    } catch (_error) {
        return [];
    }
}

async function startCheckout(productKey) {
    const statusEl = document.getElementById('pricingStatus');
    const token = getAccessToken();
    if (!token) {
        if (statusEl) {
            statusEl.textContent = 'Sign in to purchase scans.';
        }
        return;
    }

    if (statusEl) {
        statusEl.textContent = 'Opening checkout…';
    }

    try {
        const response = await fetchWithTimeout(`${apiBase()}/api/billing/checkout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ product_key: productKey }),
        });

        let data = {};
        try {
            data = await response.json();
        } catch (_error) {
            data = {};
        }

        if (!response.ok) {
            const detail = data.detail || {};
            const message = typeof detail === 'string'
                ? detail
                : (detail.message || 'Could not start checkout.');
            if (statusEl) {
                statusEl.textContent = message;
            }
            return;
        }

        if (data.url) {
            window.location.href = data.url;
        }
    } catch (error) {
        if (statusEl) {
            statusEl.textContent = error.name === 'AbortError'
                ? 'Checkout timed out. Try again.'
                : 'Could not reach the server.';
        }
    }
}

async function handleBillingPortal() {
    const statusEl = document.getElementById('pricingStatus');
    const token = getAccessToken();
    if (!token) {
        return;
    }

    if (statusEl) {
        statusEl.textContent = 'Opening billing portal…';
    }

    try {
        const response = await fetchWithTimeout(`${apiBase()}/api/billing/portal`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        let data = {};
        try {
            data = await response.json();
        } catch (_error) {
            data = {};
        }

        if (!response.ok) {
            const detail = data.detail || {};
            const message = typeof detail === 'string'
                ? detail
                : (detail.message || 'Could not open billing portal.');
            if (statusEl) {
                statusEl.textContent = message;
            }
            return;
        }

        if (data.url) {
            window.location.href = data.url;
        }
    } catch (error) {
        if (statusEl) {
            statusEl.textContent = 'Could not reach the server.';
        }
    }
}

function renderPricingProducts() {
    const container = document.getElementById('pricingOptions');
    if (!container) {
        return;
    }

    container.innerHTML = '';

    if (!billingProducts.length) {
        container.innerHTML = '<p class="pricing-card-detail">Paid plans are not available yet.</p>';
        return;
    }

    billingProducts.forEach((product) => {
        const card = document.createElement('div');
        card.className = 'pricing-card';

        const buttonLabel = product.mode === 'subscription' ? 'Subscribe' : 'Buy';

        card.innerHTML = `
            <div class="pricing-card-name">${escapeHtml(product.name)} · ${escapeHtml(product.amount_display)}</div>
            <div class="pricing-card-detail">${escapeHtml(product.description)}</div>
            <button type="button" class="btn btn-secondary pricing-buy-btn">${buttonLabel}</button>
        `;

        card.querySelector('.pricing-buy-btn')?.addEventListener('click', () => {
            void startCheckout(product.key);
        });

        container.appendChild(card);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

function updatePricingUI(account) {
    const section = document.getElementById('pricingSection');
    const portalBtn = document.getElementById('billingPortalButton');
    const balanceEl = document.getElementById('creditBalance');

    if (!section || !account) {
        section?.classList.add('hidden');
        return;
    }

    const showPricing = Boolean(account.payments_enabled);
    section.classList.toggle('hidden', !showPricing);

    const label = section.querySelector('.pricing-label');
    if (label) {
        label.textContent = account.credit_balance <= 0
            ? 'Need more scans?'
            : 'Buy more scans';
    }

    if (balanceEl) {
        balanceEl.classList.toggle('no-credits', account.credit_balance <= 0);
    }

    if (portalBtn) {
        const showPortal = Boolean(
            account.payments_enabled && account.stripe_customer_id,
        );
        portalBtn.classList.toggle('hidden', !showPortal);
    }

    if (showPricing && billingProducts.length === 0) {
        void loadBillingProducts();
    } else if (showPricing) {
        renderPricingProducts();
    }
}

async function loadBillingProducts() {
    billingProducts = await fetchBillingProducts();
    renderPricingProducts();
}

function showPricingPanel() {
    const section = document.getElementById('pricingSection');
    section?.classList.remove('hidden');
    section?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    if (billingProducts.length === 0) {
        void loadBillingProducts();
    } else {
        renderPricingProducts();
    }
}

function handleCheckoutReturn() {
    const url = new URL(window.location.href);
    const checkout = url.searchParams.get('checkout');
    if (!checkout) {
        return;
    }

    url.searchParams.delete('checkout');
    window.history.replaceState({}, document.title, url.pathname + url.search + url.hash);

    const statusEl = document.getElementById('pricingStatus');
    if (checkout === 'success') {
        if (statusEl) {
            statusEl.textContent = 'Payment received. Credits may take a few seconds to appear.';
        }
        void updateAuthUI();
    } else if (checkout === 'cancel' && statusEl) {
        statusEl.textContent = 'Checkout canceled.';
    }
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
        lastAccount = null;
        signedOut?.classList.remove('hidden');
        signedIn?.classList.add('hidden');
        document.getElementById('pricingSection')?.classList.add('hidden');
        if (balanceEl) {
            balanceEl.textContent = '';
            balanceEl.classList.remove('no-credits');
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
        lastAccount = result.account;
        balanceEl.textContent = `${result.account.credit_balance} scans left`;
        updatePricingUI(result.account);
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
window.showPricingPanel = showPricingPanel;
window.getAccountBalance = () => lastAccount?.credit_balance;
