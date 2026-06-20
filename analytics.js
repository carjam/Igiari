(function () {
    var token = window.IGIARI_CF_ANALYTICS_TOKEN;
    if (!token) {
        return;
    }

    var script = document.createElement('script');
    script.defer = true;
    script.src = 'https://static.cloudflareinsights.com/beacon.min.js';
    script.setAttribute('data-cf-beacon', JSON.stringify({ token: token }));
    document.head.appendChild(script);
})();
