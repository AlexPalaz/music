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
  fbq('init', PIXEL_ID);
  fbq('track', 'PageView');
  fbq('track', 'ViewContent', { content_name: RELEASE, content_type: 'song' });

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
          fbq('track', 'Lead', { content_name: RELEASE, content_category: platform }, { eventID: platform + '-' + Date.now() });
          fbq('trackCustom', 'Listen', { platform: platform, track: RELEASE });
        } catch (err) {}
        setTimeout(go, 250);
      });
    });
  });
})();
