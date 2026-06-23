/**
 * topbar.js — 全站固定頂部導覽列
 * 自動偵測所在區段，顯示麵包屑：首頁 › 寇俠 › 玩家入口 / GM入口
 */
(function () {
  'use strict';

  // 此專案的 GitHub Pages 根目錄（只有一個 repo）
  const BASE = location.origin + '/larp-script-archive/';

  const path = location.pathname;
  const inGm     = path.includes('/kou-xia/gm/');
  const inPlayer = path.includes('/kou-xia/player/') || path.includes('/kou-xia/public/');
  const inKouXia = path.includes('/kou-xia/');

  // 所有可能出現的麵包屑節點
  const CRUMBS = [
    { href: BASE + 'index.html',                         label: '📜 首頁',  show: true },
    { href: BASE + 'scripts/kou-xia/index.html',         label: '寇俠',    show: inKouXia },
    { href: BASE + 'scripts/kou-xia/player/index.html',  label: '玩家入口', show: inPlayer && !inGm },
    { href: BASE + 'scripts/kou-xia/gm/index.html',      label: 'GM 入口', show: inGm },
  ];

  const crumbs = CRUMBS.filter(function (c) { return c.show; });

  /* ── CSS ──────────────────────────────────────────────────────────────── */
  const css = [
    '#site-topbar{',
    '  position:fixed;top:0;left:0;right:0;height:36px;',
    '  background:#120a04;border-bottom:1px solid #3a2010;',
    '  display:flex;align-items:center;padding:0 .9rem;gap:.15rem;',
    '  z-index:9999;',
    '  font-size:.77rem;font-family:"Segoe UI","Microsoft JhengHei","PingFang TC",sans-serif;',
    '  box-shadow:0 2px 10px rgba(0,0,0,.45);',
    '}',
    '#site-topbar a{',
    '  color:#b88a48;text-decoration:none;white-space:nowrap;',
    '  padding:.22em .55em;border-radius:3px;',
    '  transition:background .15s,color .15s;',
    '}',
    '#site-topbar a:hover{background:#2a1808;color:#f0c060;}',
    '#site-topbar .tb-sep{color:#3a2010;margin:0 .05em;font-size:.85em;user-select:none;}',
    '#site-topbar a.tb-home{font-weight:600;}',
    '.topbar-mounted{padding-top:36px!important;}',
  ].join('\n');

  /* ── HTML ─────────────────────────────────────────────────────────────── */
  var html = crumbs.map(function (c, i) {
    var sep  = i > 0 ? '<span class="tb-sep">›</span>' : '';
    var cls  = i === 0 ? ' class="tb-home"' : '';
    var curr = location.href.includes(c.href.replace(location.origin, '')) ? ' aria-current="page"' : '';
    return sep + '<a href="' + c.href + '"' + cls + curr + '>' + c.label + '</a>';
  }).join('');

  /* ── Mount ────────────────────────────────────────────────────────────── */
  var se = document.createElement('style');
  se.textContent = css;
  document.head.appendChild(se);

  var bar = document.createElement('nav');
  bar.id = 'site-topbar';
  bar.setAttribute('aria-label', '全站導覽');
  bar.innerHTML = html;

  document.body.insertBefore(bar, document.body.firstChild);
  document.body.classList.add('topbar-mounted');
})();
