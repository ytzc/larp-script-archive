/**
 * password-gate.js
 *
 * IMPORTANT SECURITY NOTICE:
 * - This is a simple client-side password gate for casual access control only.
 * - Do not treat this as strong security.
 * - Passwords passed to initPasswordGate() are visible in page source to anyone.
 * - Do not publish truly sensitive or copyrighted full scripts directly to GitHub Pages.
 * - This gate only prevents casual visitors from stumbling into spoilers.
 * - Anyone who views page source or opens DevTools can bypass this gate trivially.
 */

(function () {

  /**
   * Initialise a password gate for the current page.
   *
   * @param {object} config
   * @param {string} config.role      - Unique role key, e.g. 'kou-xia-player'
   * @param {string} config.password  - The plaintext password (visible in source)
   * @param {string} [config.icon]    - Emoji icon shown on the gate
   * @param {string} [config.title]   - Gate heading
   * @param {string} [config.desc]    - Gate subtitle / instruction
   * @param {string} [config.back]    - Relative URL for the "back" link
   */
  function initPasswordGate(config) {
    var STORAGE_KEY = 'larp-gate-' + config.role;
    var gate        = document.getElementById('password-gate');
    var content     = document.getElementById('protected-content');

    if (!gate || !content) {
      console.warn('password-gate.js: #password-gate or #protected-content not found.');
      return;
    }

    // Already unlocked this browser session?
    if (sessionStorage.getItem(STORAGE_KEY) === '1') {
      _unlock(gate, content);
      return;
    }

    // Render the gate UI
    gate.innerHTML = _buildHTML(config);
    gate.style.display = 'flex';
    content.style.display = 'none';

    var input = gate.querySelector('#gate-input');
    var form  = gate.querySelector('#gate-form');

    if (input) input.focus();

    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var val = input ? input.value : '';
        if (val === config.password) {
          sessionStorage.setItem(STORAGE_KEY, '1');
          _unlock(gate, content);
        } else {
          var err = gate.querySelector('#gate-error');
          if (err) err.style.display = 'block';
          if (input) { input.value = ''; input.focus(); }
        }
      });
    }
  }

  function _unlock(gate, content) {
    gate.style.display   = 'none';
    content.style.display = 'block';
  }

  function _buildHTML(c) {
    var icon  = c.icon  || '🔒';
    var title = c.title || 'Protected Area';
    var desc  = c.desc  || 'Enter the password to access this section.';
    var back  = c.back  || '../index.html';
    return (
      '<div class="gate-box">' +
        '<div class="gate-icon">' + icon + '</div>' +
        '<h2 class="gate-title">' + title + '</h2>' +
        '<p class="gate-desc">' + desc + '</p>' +
        '<form id="gate-form" autocomplete="off">' +
          '<div class="gate-row">' +
            '<input type="password" id="gate-input" class="gate-input" placeholder="Password" spellcheck="false" />' +
            '<button type="submit" class="gate-button">Unlock</button>' +
          '</div>' +
        '</form>' +
        '<p id="gate-error" class="gate-error" style="display:none;">Incorrect password — please try again.</p>' +
        '<p class="gate-back"><a href="' + back + '">← Back</a></p>' +
      '</div>'
    );
  }

  window.initPasswordGate = initPasswordGate;

}());
