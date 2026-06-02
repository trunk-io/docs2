(function () {
  var lastFiredPath = null;

  function check404() {
    var path = document.location.pathname;
    if (
      document.title === 'Page Not Found' &&
      typeof plausible === 'function' &&
      path !== lastFiredPath
    ) {
      lastFiredPath = path;
      plausible('404', { props: { path: path } });
    }
  }

  // Watch for React updating the title asynchronously after hydration,
  // and on subsequent SPA navigations.
  var titleEl = document.querySelector('title');
  if (titleEl) {
    new MutationObserver(check404).observe(titleEl, { childList: true });
  }

  // Fallback for the rare case the title is set before the observer attaches.
  window.addEventListener('load', check404);
})();
