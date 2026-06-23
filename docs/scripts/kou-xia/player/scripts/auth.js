/**
 * CharAuth — 角色登入工具
 *
 * sessionStorage key: kou-xia-char-session
 * 後端接入點：將 _callApi() 中的 fetch 換成真實 API 即可，
 *             其餘 login / logout / getSession 不需修改。
 */
(function (global) {
  'use strict';

  var SESSION_KEY = 'kou-xia-char-session';

  /* ── 後端接入點 ─────────────────────────────────
     TODO: 當後端完成後，將 DEMO_ACCOUNTS 移除，
           並在 _callApi() 改為實際 fetch 呼叫。
  ──────────────────────────────────────────────── */
  var DEMO_ACCOUNTS = {
    'wang-si-han':   { characterId: 'wang-si-han',   characterName: '王思涵', playerName: 'Luna',   password: 'demo-luna'   },
    'jia-san-niang': { characterId: 'jia-san-niang', characterName: '賈三娘', playerName: 'Peggy',  password: 'demo-peggy'  },
    'diao-wu-er':    { characterId: 'diao-wu-er',    characterName: '刁五兒', playerName: '佩璇',   password: 'demo-px'     },
    'yan-yi':        { characterId: 'yan-yi',        characterName: '嚴逸',   playerName: '健元',   password: 'demo-jy'     },
    'yan-shi':       { characterId: 'yan-shi',       characterName: '嚴氏',   playerName: '媛媛',   password: 'demo-yy'     },
    'wang-shun':     { characterId: 'wang-shun',     characterName: '王順',   playerName: '宣毅',   password: 'demo-xy'     },
    'nong-sou':      { characterId: 'nong-sou',      characterName: '農叟',   playerName: '佩妏',   password: 'demo-pw'     },
    'jin-si-dao':    { characterId: 'jin-si-dao',    characterName: '金四刀', playerName: '建翔',   password: 'demo-jx'     },
    'zhang-meng':    { characterId: 'zhang-meng',    characterName: '張猛',   playerName: '子擎',   password: 'demo-zq'     }
  };

  /**
   * 驗證帳號密碼。
   * 後端完成後將此函式改為 fetch('/api/login', { method:'POST', body:... })
   * 並 return 後端回傳的 { characterId, characterName, playerName } 物件（失敗回 null）。
   */
  function _callApi(username, password) {
    var acct = DEMO_ACCOUNTS[username.trim().toLowerCase()];
    if (acct && acct.password === password) {
      return { characterId: acct.characterId, characterName: acct.characterName, playerName: acct.playerName };
    }
    return null;
  }

  var CharAuth = {
    /** 登入：驗證後寫入 sessionStorage，回傳 characterId 或 null。 */
    login: function (username, password) {
      var data = _callApi(username, password);
      if (data) {
        data.loginTime = Date.now();
        try { sessionStorage.setItem(SESSION_KEY, JSON.stringify(data)); } catch (e) {}
      }
      return data ? data.characterId : null;
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
      bar.style.cssText = 'background:#1a1510;color:#7a6a52;font-size:.78rem;padding:.38rem 1rem;display:flex;justify-content:space-between;align-items:center;gap:1rem;border-bottom:1px solid #3a2e22;font-family:sans-serif;';
      if (session) {
        bar.innerHTML =
          '<span>🎭 <strong style="color:#c49a38;">' + session.characterName + '</strong> (' + session.playerName + ')</span>' +
          '<button onclick="CharAuth.logout();location.reload();" style="background:none;border:1px solid #3a2e22;color:#7a6a52;padding:.18rem .65rem;border-radius:2px;cursor:pointer;font-size:.75rem;">登出</button>';
      } else {
        bar.innerHTML =
          '<span style="color:#7a6a52;">未登入角色帳號</span>' +
          '<a href="' + loginUrl + '" style="color:#c49a38;font-size:.75rem;">前往登入 →</a>';
      }
      var body = document.body;
      if (body.firstChild) { body.insertBefore(bar, body.firstChild); }
      else { body.appendChild(bar); }
    }
  };

  global.CharAuth = CharAuth;
}(window));
