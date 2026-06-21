// Cloudflare Web Analytics — paste token from dash.cloudflare.com → Web Analytics → your site.
// Leave empty to disable the beacon (Cloudflare Pages dashboard analytics still works without this).
window.IGIARI_CF_ANALYTICS_TOKEN = '';

// Local dev: when served from localhost, talk to the backend on :8000
if (
    window.location.hostname === 'localhost'
    || window.location.hostname === '127.0.0.1'
) {
    window.API_BASE = 'http://127.0.0.1:8000';
    // Backend without Supabase env uses anonymous rate-limited scans (see backend/README.md).
    window.IGIARI_LOCAL_DEV = true;
}

// Supabase — Project Settings → API Keys (publishable key is safe in frontend code)
window.IGIARI_SUPABASE_URL = 'https://yvkrihgjcoyqytwoisgw.supabase.co';
window.IGIARI_SUPABASE_ANON_KEY = 'sb_publishable_pj2A2EDG-Gx2WP1Tzbuv5Q_uYMNz8D_';
