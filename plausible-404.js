(function () {
  // The last non-404 page visited in this SPA session. On a client-side
  // navigation `document.referrer` doesn't update, so this is how we know which
  // page held the dead link the user just clicked.
  var lastGoodPath = null

  function isNotFound() {
    return document.title === 'Page Not Found'
  }

  function track404() {
    if (typeof window.plausible !== 'function') return
    if (track404.last === location.pathname) return
    track404.last = location.pathname

    // "The page the click came from." On a soft navigation that's the last
    // in-app page (the one holding the dead link). On a hard load (typed URL,
    // refresh, external inbound) there's no prior in-app page, so fall back to
    // the document referrer, then to '(direct)'.
    var referrer = lastGoodPath
      ? location.origin + lastGoodPath
      : document.referrer || '(direct)'

    window.plausible('404', {
      props: {
        path: location.pathname,
        referrer: referrer,
      },
    })
  }

  function onNavigation() {
    if (isNotFound()) {
      track404()
    } else {
      lastGoodPath = location.pathname
    }
  }

  // Initial hard load.
  if (document.readyState === 'complete') onNavigation()
  else window.addEventListener('load', onNavigation)

  // Client-side route changes: Mintlify is a Next.js SPA, so a dead internal
  // link is a soft navigation that never re-fires `load`. The <title> flips on
  // every route change — to "Page Not Found" on a 404, and to the real page
  // title otherwise (which is how we remember where we came from).
  var titleEl = document.querySelector('title')
  if (titleEl) {
    new MutationObserver(onNavigation).observe(titleEl, {
      childList: true,
      characterData: true,
      subtree: true,
    })
  }
})()
