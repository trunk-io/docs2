(function () {
  function track404() {
    if (document.title !== 'Page Not Found') return
    if (typeof window.plausible !== 'function') return
    if (track404.last === location.pathname) return
    track404.last = location.pathname
    window.plausible('404', {
      props: {
        path: location.pathname,
        referrer: document.referrer || '(direct)',
      },
    })
  }

  // Initial hard load: typed URL, refresh, or external inbound link.
  if (document.readyState === 'complete') track404()
  else window.addEventListener('load', track404)

  // Client-side route changes: Mintlify is a Next.js SPA, so clicking a dead
  // internal link is a soft navigation that never re-fires `load`. Watch the
  // <title> instead — it flips to "Page Not Found" on every 404, hard or soft.
  var titleEl = document.querySelector('title')
  if (titleEl) {
    new MutationObserver(track404).observe(titleEl, { childList: true })
  }
})()
