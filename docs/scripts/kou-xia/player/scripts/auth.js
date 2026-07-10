/**
 * CharAuth — 角色登入與註冊工具 (SQLite API Backend Version)
 *
 * sessionStorage key: kou-xia-char-session
 */
(function (global) {
  'use strict';

  var SESSION_KEY = 'kou-xia-char-session';

  var CharAuth = {
    /**
     * 登入：呼叫後端 API 驗證，成功後寫入 sessionStorage。
     * 回傳 Promise，resolve 角色 ID (string) 或 reject 錯誤。
     */
    login: function (username, password) {
      var STATIC_CHARS = {
        'wang-si-han': '王思涵',
        'jia-san-niang': '賈三娘',
        'diao-wu-er': '刁五兒',
        'yan-yi': '嚴逸',
        'yan-shi': '嚴氏',
        'wang-shun': '王順',
        'nong-sou': '農叟',
        'jin-si-dao': '金四刀',
        'zhang-meng': '張猛'
      };

      return fetch('/api/kou-xia/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: username,
          password: password
        })
      })
      .then(function (res) {
        if (!res.ok) { throw new Error('Static Fallback'); }
        return res.json();
      })
      .catch(function (err) {
        console.warn('Backend API unavailable. Falling back to static mode.', err);
        if (username === 'gm' && password === 'gm') {
          return { success: true, is_gm: true, session: { characterId: 'gm', characterName: 'GM', playerName: 'GM' } };
        }
        if (STATIC_CHARS[username]) {
          return { success: true, session: { characterId: username, characterName: STATIC_CHARS[username], playerName: 'Static Player' } };
        }
        return { success: false, message: '靜態模式：帳號或密碼錯誤' };
      })
      .then(function (data) {
        if (data.success && data.session) {
          data.session.loginTime = Date.now();
          if (data.is_gm) {
            data.session.is_gm = true;
          }
          try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(data.session)); } catch (e) {}
          return data.session.characterId;
        } else {
          throw new Error(data.message || '帳號或密碼錯誤');
        }
      });
    },

    /**
     * 註冊：呼叫後端 API 註冊角色並直接登入，成功後寫入 sessionStorage。
     * 回傳 Promise，resolve 角色 ID (string) 或 reject 錯誤。
     */
    register: function (characterId, playerName, password) {
      var STATIC_CHARS = {
        'wang-si-han': '王思涵',
        'jia-san-niang': '賈三娘',
        'diao-wu-er': '刁五兒',
        'yan-yi': '嚴逸',
        'yan-shi': '嚴氏',
        'wang-shun': '王順',
        'nong-sou': '農叟',
        'jin-si-dao': '金四刀',
        'zhang-meng': '張猛'
      };

      return fetch('/api/kou-xia/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          characterId: characterId,
          playerName: playerName,
          password: password
        })
      })
      .then(function (res) {
        if (!res.ok) { throw new Error('Static Fallback'); }
        return res.json();
      })
      .catch(function (err) {
        console.warn('Backend API unavailable. Falling back to static mode.', err);
        if (STATIC_CHARS[characterId]) {
          return { success: true, session: { characterId: characterId, characterName: STATIC_CHARS[characterId], playerName: playerName } };
        }
        return { success: false, message: '靜態模式：註冊失敗' };
      })
      .then(function (data) {
        if (data.success && data.session) {
          data.session.loginTime = Date.now();
          try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(data.session)); } catch (e) {}
          return data.session.characterId;
        } else {
          throw new Error(data.message || '註冊失敗');
        }
      });
    },

    /** 登出：清除 session。 */
    logout: function () {
      try { sessionStorage.removeItem(SESSION_KEY); } catch (e) {}
    },

    /** 取得目前 session，未登入回 null。 */
    getSession: function () {
      try {
        var raw = sessionStorage.getItem(SESSION_KEY);
        return raw ? JSON.parse(raw) : null;
      } catch (e) { return null; }
    },

    /** 是否已登入。 */
    isLoggedIn: function () {
      return !!this.getSession();
    },

    /**
     * 在角色劇本頁呼叫：確認目前登入的角色符合此頁。
     * @param {string} expectedId  此頁的角色 ID（如 'wang-si-han'）
     * @param {string} [loginUrl]  未登入時跳轉的登入頁路徑
     */
    requireCharacter: function (expectedId, loginUrl) {
      var session = this.getSession();
      loginUrl = loginUrl || '../login.html';
      if (!session) {
        window.location.href = loginUrl;
        return null;
      }
      // If GM is logged in, they can view any character's script page!
      if (session.is_gm) {
        return session;
      }
      if (session.characterId !== expectedId) {
        window.location.href = loginUrl + '?mismatch=1';
        return null;
      }
      return session;
    },

    /** 在頁面插入登入狀態列（呼叫後自動插入 body 最前）。 */
    renderStatusBar: function (loginUrl) {
      loginUrl = loginUrl || '../login.html';
      var session = this.getSession();
      var bar = document.createElement('div');
      bar.id = 'char-auth-bar';

      if (!document.getElementById('char-auth-bar-style')) {
        var css = [
          '#char-auth-bar {',
          '  position: fixed;',
          '  top: 36px;',
          '  left: 0;',
          '  right: 0;',
          '  z-index: 9998;',
          '  background: #1a1510;',
          '  color: #7a6a52;',
          '  font-size: .78rem;',
          '  padding: .38rem 1rem;',
          '  display: flex;',
          '  justify-content: space-between;',
          '  align-items: center;',
          '  gap: 1rem;',
          '  border-bottom: 1px solid #3a2e22;',
          '  font-family: sans-serif;',
          '  box-shadow: 0 2px 10px rgba(0,0,0,0.45);',
          '}',
          '#char-auth-bar a {',
          '  color: #c49a38;',
          '  text-decoration: underline;',
          '  font-weight: bold;',
          '}',
          '#char-auth-bar a:hover {',
          '  color: #f0c060;',
          '}',
          'body.authbar-mounted {',
          '  padding-top: 72px !important;',
          '}',
          'body.authbar-mounted main {',
          '  padding-top: 0 !important;',
          '}',
          '@media (max-width: 600px) {',
          '  #char-auth-bar {',
          '    flex-direction: column;',
          '    align-items: flex-start;',
          '    gap: .25rem;',
          '    padding: .45rem .8rem;',
          '  }',
          '  body.authbar-mounted {',
          '    padding-top: 92px !important;',
          '  }',
          '}',
          '@media (max-width: 400px) {',
          '  body.authbar-mounted {',
          '    padding-top: 108px !important;',
          '  }',
          '}'
        ].join('\n');
        var se = document.createElement('style');
        se.id = 'char-auth-bar-style';
        se.textContent = css;
        document.head.appendChild(se);
      }

      if (session) {
        var isPlayerIndex = (loginUrl.indexOf('..') === -1);
        var myScriptUrl;
        if (session.is_gm) {
          myScriptUrl = isPlayerIndex ? 'gm/index.html' : '../gm/index.html';
        } else {
          myScriptUrl = isPlayerIndex ? ('scripts/' + session.characterId + '.html') : (session.characterId + '.html');
        }
        var roleText = session.is_gm ? '🎲 <strong style="color:#c49a38;">GM</strong>' : '🎭 <strong style="color:#c49a38;">' + session.characterName + '</strong> (' + session.playerName + ')';
        
        var scriptLink = ' &nbsp; <a href="' + myScriptUrl + '" style="color:#c49a38;text-decoration:underline;font-weight:bold;margin-left:0.5rem;">[進入我的劇本 →]</a>';
        var entranceLink = '';

        bar.innerHTML =
          '<span>' + roleText + scriptLink + entranceLink + '</span>' +
          '<button id="char-auth-logout-btn" style="background:none;border:1px solid #3a2e22;color:#7a6a52;padding:.18rem .65rem;border-radius:2px;cursor:pointer;font-size:.75rem;">登出</button>';
      } else {
        bar.innerHTML =
          '<span style="color:#7a6a52;">未登入角色帳號</span>' +
          '<a href="' + loginUrl + '" style="color:#c49a38;font-size:.75rem;">前往登入 →</a>';
      }
      var body = document.body;
      if (body.firstChild) { body.insertBefore(bar, body.firstChild); }
      else { body.appendChild(bar); }
      document.body.classList.add('authbar-mounted');

      var logoutBtn = bar.querySelector('#char-auth-logout-btn');
      if (logoutBtn) {
        logoutBtn.addEventListener('click', function () {
          CharAuth.logout();
          location.reload();
        });
      }
    }
  };

  // Background heartbeat polling (only active when logged in as a normal player)
  (function () {
    function sendHeartbeat() {
      var session = CharAuth.getSession();
      if (session && !session.is_gm && session.characterId) {
        fetch('/api/kou-xia/heartbeat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ characterId: session.characterId })
        }).catch(function (err) {
          // Fail silently in static/offline fallback mode
        });
      }
    }
    // Start heartbeat: immediately, then every 8 seconds
    document.addEventListener('DOMContentLoaded', function () {
      sendHeartbeat();
      setInterval(sendHeartbeat, 8000);
    });
  }());

  global.CharAuth = CharAuth;
}(window));
