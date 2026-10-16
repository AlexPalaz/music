// Meta Pixel + click tracking for every release page.
// Reads the pixel id and the release title from <html data-pixel-id data-release>.
(function () {
  var root = document.documentElement;
  var PIXEL_ID = root.getAttribute('data-pixel-id');
  var RELEASE = root.getAttribute('data-release') || document.title;
  if (!PIXEL_ID) return;

  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  document,'script','https://connect.facebook.net/en_US/fbevents.js');
  // Traffic source from UTM parameters (utm_source=meta&utm_medium=paid&utm_campaign=…&utm_content=…).
  // Remembered for the session so hub → release navigation keeps the original source.
  var UTM = (function () {
    var keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
    var q = {}, found = false;
    try {
      var p = new URLSearchParams(location.search);
      keys.forEach(function (k) { var v = p.get(k); if (v) { q[k] = v.slice(0, 80); found = true; } });
      if (found) sessionStorage.setItem('ap_utm', JSON.stringify(q));
      else q = JSON.parse(sessionStorage.getItem('ap_utm') || '{}');
    } catch (err) { q = {}; }
    if (!q.utm_source) q.utm_source = document.referrer ? 'referral' : 'direct';
    return q;
  })();
  var SRC = { source: UTM.utm_source, medium: UTM.utm_medium || '', campaign: UTM.utm_campaign || '', ad: UTM.utm_content || '' };

  fbq('init', PIXEL_ID);
  fbq('track', 'PageView');
  fbq('track', 'ViewContent', { content_name: RELEASE, content_type: 'song', source: SRC.source, medium: SRC.medium, campaign: SRC.campaign, ad: SRC.ad });

  // ?debug=1 → small badge saying whether Meta's script actually loaded on this device.
  if (/[?&]debug=1/.test(location.search)) {
    document.addEventListener('DOMContentLoaded', function () {
      var b = document.createElement('div');
      b.style.cssText = 'position:fixed;left:12px;bottom:12px;z-index:9;padding:10px 14px;border-radius:10px;font:12px/1.4 monospace;background:#222;color:#fff;max-width:80vw';
      b.textContent = 'pixel: attendo…';
      document.body.appendChild(b);
      var tries = 0;
      var check = function () {
        tries++;
        var ok = window.fbq && fbq.instance && typeof fbq.instance.pixelsByID !== 'undefined';
        if (ok) { b.textContent = 'pixel OK · id ' + PIXEL_ID + ' · PageView + ViewContent inviati'; b.style.background = '#1DB954'; b.style.color = '#000'; return; }
        if (tries > 20) { b.textContent = 'pixel BLOCCATO su questo dispositivo (script di Meta non caricato: VPN, blocco tracker o DNS)'; b.style.background = '#ff1a1a'; return; }
        setTimeout(check, 250);
      };
      check();
      document.querySelectorAll('a[data-platform]').forEach(function (a) {
        a.addEventListener('click', function () { b.textContent += ' · click ' + a.getAttribute('data-platform') + ' → Lead inviato'; }, true);
      });
    });
  }

  // Each platform click = standard "Lead" (for ad optimisation) + custom "Listen".
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('a[data-platform]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var platform = a.getAttribute('data-platform');
        var href = a.href;
        if (typeof fbq !== 'function') return;
        e.preventDefault();
        var done = false;
        var go = function () { if (!done) { done = true; window.location.href = href; } };
        try {
          fbq('track', 'Lead', { content_name: RELEASE, content_category: platform, source: SRC.source, medium: SRC.medium, campaign: SRC.campaign, ad: SRC.ad }, { eventID: platform + '-' + Date.now() });
          fbq('trackCustom', 'Listen', { platform: platform, track: RELEASE, source: SRC.source, medium: SRC.medium, campaign: SRC.campaign, ad: SRC.ad });
        } catch (err) {}
        setTimeout(go, 250);
      });
    });
  });
})();
