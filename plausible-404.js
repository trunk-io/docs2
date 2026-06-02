(function () {
  if (document.documentElement.id !== '__next_error__') return;

  window.addEventListener('load', function () {
    if (typeof plausible === 'function') {
      plausible('404', { props: { path: document.location.pathname } });
    }
  });
})();
