window.addEventListener('load', function () {
  if (document.title.indexOf('Page Not Found') !== -1 && typeof plausible === 'function') {
    plausible('404', { props: { path: document.location.pathname } });
  }
});
