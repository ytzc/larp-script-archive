// Site version — updated automatically by release.sh before each tag push.
const SITE_VERSION = 'v0.4.6';

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.site-version').forEach(function (el) {
    el.textContent = SITE_VERSION;
  });
});
