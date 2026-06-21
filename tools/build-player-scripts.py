#!/usr/bin/env python3
"""
Build player HTML scripts from corrected source md files.
Each character script is split into per-情景 pages with GM-unlock gating.

GM unlock codes (change these before each game):
  情景二: 幕二
  情景三: 幕三

Non-情景 H1 sections (小劇場環節, 引蛇出洞私聊環節, etc.) are grouped
into the preceding 情景 page automatically.
"""
import os, re, html as html_mod

BASE       = '/home/fiducia/larp-script-archive'
SOURCE_DIR = os.path.join(BASE, 'materials/kou-xia/source')
OUTPUT_DIR = os.path.join(BASE, 'docs/scripts/kou-xia/player/scripts')

SCENE_CODES = {1: 'act2', 2: 'act3', 3: 'act4'}  # page-index → unlock code


# ── Parsing ──────────────────────────────────────────────────────────────────

def parse_front_matter(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, _, v = line.partition(':')
            fm[k.strip()] = v.strip().strip('"')
    return fm, text[m.end():]


def process_inline(text):
    """Strip OCR notes, escape HTML, apply **bold**."""
    text = re.sub(r'\[待人工確認[：:][^\]]*\]', '', text)
    text = html_mod.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    return text


# ── Md → Pages ───────────────────────────────────────────────────────────────

class PageBuilder:
    """Groups md body content into scene pages split by '# 情景X' headings."""

    def __init__(self):
        self.pages        = []       # [{'title': str, 'html': str}]
        self._title       = None
        self._parts       = []
        self._in_chapter  = False
        self._in_section  = False
        self._para        = []
        self._list_mode   = None     # None | 'ol' | 'ul' | 'question' | 'prop'
        self._list_items  = []

    # ── flushing helpers ──────────────────────────────────────────────────────

    def _flush_list(self):
        if not self._list_items:
            self._list_mode = None
            return
        if self._list_mode == 'question':
            self._parts.append('    <ol class="question-list">')
        elif self._list_mode == 'prop':
            self._parts.append('    <ul class="prop-list">')
        elif self._list_mode == 'ul':
            self._parts.append('    <ul>')
        else:
            self._parts.append('    <ol>')
        for item in self._list_items:
            self._parts.append(f'      <li>{item}</li>')
        close = 'ul' if self._list_mode in ('prop', 'ul') else 'ol'
        self._parts.append(f'    </{close}>')
        self._list_items = []
        self._list_mode  = None

    def _flush_para(self):
        self._flush_list()
        if self._para:
            txt = '\n'.join(l for l in self._para if l)
            if txt.strip():
                self._parts.append(f'    <p>{txt}</p>')
        self._para = []

    def _close_sec(self):
        self._flush_para()
        if self._in_section:
            self._parts.append('  </div><!-- /script-section -->')
            self._parts.append('')
            self._in_section = False

    def _close_ch(self):
        self._close_sec()
        if self._in_chapter:
            self._parts.append('  </div><!-- /script-chapter -->')
            self._parts.append('')
            self._in_chapter = False

    def _commit(self):
        self._close_ch()
        if self._title is not None:
            self.pages.append({'title': self._title,
                               'html':  '\n'.join(self._parts)})
        self._title      = None
        self._parts      = []
        self._in_chapter = False
        self._in_section = False

    # ── main processing ───────────────────────────────────────────────────────

    def process(self, body_text):
        skip = True
        for raw in body_text.split('\n'):
            s = raw.rstrip()

            if s.startswith('# '):
                title = s[2:].strip()
                # Skip doc-title line like "# 【角色名】文字劇本"
                if skip and ('文字劇本' in title or title.startswith('【')):
                    skip = False
                    continue
                skip = False

                if title.startswith('情景'):
                    self._commit()      # new page per 情景
                    self._title = title
                else:
                    if self._title is None:
                        self._title = title   # edge case: non-情景 first H1
                    self._close_ch()          # new chapter div within same page

                self._parts.append('  <div class="script-chapter">')
                self._parts.append(f'  <h2>{html_mod.escape(title)}</h2>')
                self._parts.append('')
                self._in_chapter = True

            elif s.startswith('## '):
                title = s[3:].strip()
                self._close_sec()
                self._parts.append('  <div class="script-section">')
                self._parts.append(f'    <h3>{html_mod.escape(title)}</h3>')
                self._in_section = True

            elif s.startswith('### ') or s.startswith('#### '):
                self._flush_para()
                title = re.sub(r'^#{3,5} ', '', s).strip()
                self._parts.append(f'    <h4>{html_mod.escape(title)}</h4>')

            elif s == '' or s == '---':
                self._flush_para()

            else:
                cleaned = process_inline(s)
                if not cleaned.strip():
                    continue
                m_num    = re.match(r'^(\d+)[\.。．]\s*(.*)', s)
                m_q      = re.match(r'^(問題\s*\d+)\s*[：:]\s*(.*)', s)
                is_prop  = (s.lstrip().startswith('【') or
                            bool(re.match(r'^\d+\s*兩', s)))
                is_bullet    = bool(re.match(r'^-\s+\S', s))
                is_scene_info = s.lstrip().startswith('◎')

                if is_scene_info:
                    self._flush_para()
                    self._parts.append(f'    <p class="scene-info">{cleaned}</p>')
                elif m_num:
                    if self._list_mode != 'ol':
                        self._flush_para()
                        self._list_mode = 'ol'
                    self._list_items.append(process_inline(m_num.group(2).strip()))
                elif m_q:
                    if self._list_mode != 'question':
                        self._flush_para()
                        self._list_mode = 'question'
                    label = html_mod.escape(m_q.group(1)) + '：'
                    rest  = process_inline(m_q.group(2).strip())
                    self._list_items.append(
                        f'<strong>{label}</strong>　{rest}' if rest
                        else f'<strong>{label}</strong>')
                elif is_prop:
                    if self._list_mode != 'prop':
                        self._flush_para()
                        self._list_mode = 'prop'
                    self._list_items.append(cleaned)
                elif is_bullet:
                    m_b = re.match(r'^-\s+(.*)', s)
                    if self._list_mode != 'ul':
                        self._flush_para()
                        self._list_mode = 'ul'
                    self._list_items.append(process_inline(m_b.group(1)))
                elif self._list_mode == 'ol' and self._list_items:
                    # Continuation lines of last numbered item
                    self._list_items[-1] += ' ' + cleaned
                elif self._list_mode == 'question':
                    # Trailing note after question block
                    self._flush_para()
                    self._para.append(cleaned)
                else:
                    if self._list_mode:
                        self._flush_para()
                    self._para.append(cleaned)

        self._commit()
        return self.pages


# ── HTML generation ───────────────────────────────────────────────────────────

def _tabs_html(pages):
    lines = []
    for i, page in enumerate(pages):
        cls = 'tab-btn active' if i == 0 else 'tab-btn locked'
        label = html_mod.escape(page['title'])
        lines.append(f'    <button class="{cls}" role="tab" data-page="{i}" onclick="switchPage({i})">{label}</button>')
    return '\n'.join(lines)


def _pages_html(pages):
    parts = []
    for i, page in enumerate(pages):
        body = page['html']
        if i == 0:
            parts.append(
                f'  <div class="chapter-page active" data-page="0">\n'
                f'    <div class="chapter-content">\n'
                f'{body}\n'
                f'    </div>\n'
                f'  </div>'
            )
        else:
            t = html_mod.escape(page['title'])
            parts.append(
                f'  <div class="chapter-page" data-page="{i}">\n'
                f'    <div class="chapter-lock" id="chl-{i}">\n'
                f'      <div class="lock-inner">\n'
                f'        <div class="lock-icon">&#x1F512;</div>\n'
                f'        <p class="lock-title">{t} — 尚未解鎖</p>\n'
                f'        <p class="lock-hint">等待主持人宣布進入{t}，並向主持人取得解鎖碼。</p>\n'
                f'        <div class="unlock-row">\n'
                f'          <input type="password" class="unlock-input" id="uinp-{i}" placeholder="輸入解鎖碼">\n'
                f'          <button class="unlock-btn" onclick="tryUnlock({i})">解鎖</button>\n'
                f'        </div>\n'
                f'        <p class="unlock-err" id="uerr-{i}">解鎖碼不正確，請向主持人確認</p>\n'
                f'      </div>\n'
                f'    </div>\n'
                f'    <div class="chapter-content" id="chc-{i}" hidden>\n'
                f'{body}\n'
                f'    </div>\n'
                f'  </div>'
            )
    return '\n'.join(parts)


def _codes_json(pages):
    entries = []
    for i in range(1, len(pages)):
        code = SCENE_CODES.get(i, f'幕{i}')
        entries.append(f'"{i}":"{code}"')
    return '{' + ','.join(entries) + '}'


# ── Template ──────────────────────────────────────────────────────────────────

TEMPLATE = '''\
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{name} &#8212; 角色劇本 &#8212; 寇侠</title>
  <link rel="stylesheet" href="../../../../assets/css/style.css" />
  <style>
    /* ── Page base ────────────────────────────── */
    body{{background:#f4eadc;color:#2f261f}}
    /* ── Layout ───────────────────────────────── */
    .script-body{{max-width:780px;margin:0 auto}}
    /* ── Cover ────────────────────────────────── */
    .script-cover{{background:linear-gradient(150deg,#6b2a14 0%,#8c3c24 100%);color:#f5e6d3;border:2px solid #a06840;border-radius:10px;padding:2.5rem 2rem;margin-bottom:1.5rem;text-align:center}}
    .script-cover h1{{font-size:2.4rem;margin:0 0 .3rem;letter-spacing:.18em;color:#fdf0e0;border:none;text-shadow:0 1px 4px rgba(0,0,0,.28)}}
    .script-cover .char-meta{{color:#e8c898;font-size:.9rem;margin:.3rem 0;letter-spacing:.04em}}
    .script-cover .cover-poem{{font-style:italic;color:#dbb87a;margin-top:.9rem;font-size:.88rem;border-top:1px solid rgba(255,255,255,.28);padding-top:.8rem;letter-spacing:.03em}}
    /* ── Chapter tabs ─────────────────────────── */
    .chapter-tabs{{display:flex;gap:.5rem;margin-bottom:1rem;flex-wrap:wrap;padding:.3rem 0;align-items:center}}
    .tab-btn{{background:#fff;border:2px solid #c8b89a;border-radius:6px;padding:.45rem 1.1rem;font-size:.9rem;cursor:pointer;color:#5a3a1a;font-family:inherit;letter-spacing:.04em;transition:background .15s,border-color .15s,color .15s;white-space:nowrap}}
    .tab-btn.active{{background:#8b0000;border-color:#8b0000;color:#fff;font-weight:700}}
    .tab-btn.locked{{color:#bbb;border-color:#e0d4c0}}
    .tab-btn.locked::after{{content:' 🔒';font-size:.8em}}
    /* ── PDF button ───────────────────────────── */
    .pdf-btn-row{{display:flex;justify-content:flex-end;margin-bottom:1.2rem}}
    .btn-pdf{{background:#8b0000;color:#fff;border:none;padding:.55rem 1.3rem;border-radius:5px;cursor:pointer;font-size:.88rem;font-family:inherit;letter-spacing:.04em;transition:background .15s}}
    .btn-pdf:hover{{background:#5a0000}}
    /* ── Chapter pages ────────────────────────── */
    .chapter-page{{display:none}}
    .chapter-page.active{{display:block}}
    /* ── Lock overlay ─────────────────────────── */
    .chapter-lock{{display:flex;justify-content:center;align-items:center;min-height:260px;background:#faf5ee;border-radius:8px;border:1px dashed #c8b89a;margin:1rem 0}}
    .lock-inner{{text-align:center;max-width:400px;padding:2rem}}
    .lock-icon{{font-size:3rem;margin-bottom:.5rem}}
    .lock-title{{font-size:1.1rem;color:#5a3a1a;font-weight:700;margin:.3rem 0}}
    .lock-hint{{color:#888;font-size:.88rem;margin:.4rem 0 1.1rem;line-height:1.55}}
    .unlock-row{{display:flex;gap:.5rem;justify-content:center;flex-wrap:wrap;margin:.5rem 0}}
    .unlock-input{{border:1px solid #c8b89a;border-radius:5px;padding:.5rem .8rem;font-size:.95rem;font-family:inherit;width:140px;text-align:center;letter-spacing:.06em}}
    .unlock-btn{{background:#8b0000;color:#fff;border:none;border-radius:5px;padding:.5rem 1.1rem;font-size:.9rem;cursor:pointer;font-family:inherit}}
    .unlock-btn:hover{{background:#5a0000}}
    .unlock-err{{color:#c00;font-size:.85rem;margin:.5rem 0 0;display:none}}
    /* ── Script content ───────────────────────── */
    .script-chapter{{margin-bottom:2rem}}
    .script-chapter > h2{{color:#5f2f18;border-bottom:2px solid #b98b5b;padding-bottom:.5rem;font-size:1.3rem;margin-top:0;margin-bottom:1.2rem;letter-spacing:.06em}}
    .script-section{{background:#fffaf2;color:#2f261f;border:1px solid #dcc8a8;border-radius:12px;padding:1.5rem 1.8rem;margin-bottom:1.25rem;box-shadow:0 2px 10px rgba(80,50,20,.06)}}
    .script-section h3{{color:#6f3f1d;margin-top:0;border-bottom:1px solid #dcc8a8;padding-bottom:.4rem;font-size:1rem;letter-spacing:.04em}}
    .script-section p{{color:#2f261f;margin:.9rem 0;line-height:1.95;text-align:justify;text-indent:2em}}
    .script-section strong{{color:#8a4b16;font-weight:800}}
    .script-section h4{{color:#5c421f;background:#f5ead8;font-size:.96rem;margin:1.1rem 0 .45rem;font-weight:800;border-left:4px solid #b98b5b;padding:.35rem .6rem;border-radius:6px}}
    .script-section ol,.script-section ul{{margin:.75rem 0 1rem 0;padding-left:1.2rem;line-height:1.9}}
    .script-section li{{margin:.45rem 0;color:#2f261f}}
    .script-section .question-list{{list-style:none;padding-left:.2rem}}
    .script-section .question-list li{{margin-bottom:.55rem}}
    .script-section .scene-info{{color:#5a3a1a;font-size:.9em;margin:.2rem 0;padding:.1rem .6rem;border-left:3px solid #c8b89a;background:#faf5ee;text-indent:0}}
    .script-section .prop-list{{list-style:none;padding-left:.2rem}}
    .script-section .prop-list li::before{{content:'▫ ';color:#8b6040;font-size:.9em}}
    /* ── Mobile ───────────────────────────────── */
    @media(max-width:600px){{
      body{{background:#f4eadc}}
      main{{padding:.6rem}}
      .script-body{{max-width:100%}}
      .script-section{{padding:1rem 1rem;border-radius:10px;margin-bottom:1rem}}
      .script-section p{{line-height:1.9;text-align:left}}
      .script-section ol,.script-section ul{{margin-left:.6rem;padding-left:1.1rem}}
      .script-section li{{line-height:1.85;margin-bottom:.5rem}}
      .script-cover{{padding:1.6rem 1rem}}
      .script-cover h1{{font-size:1.9rem}}
      .tab-btn{{padding:.4rem .85rem;font-size:.85rem}}
      .script-section h4{{font-size:.98rem}}
    }}
    /* ── Print: show only the active chapter ─── */
    @page{{size:A4;margin:8mm}}
    @media print{{
      html,body{{background:#fffaf2!important;color:#1f1a16!important;font-size:12pt;line-height:1.75}}
      .site-header,.top-nav,.chapter-tabs,.pdf-btn-row,
      footer.site-footer,#password-gate,.notice,.chapter-lock{{display:none!important}}
      main{{padding:0!important;margin:0!important}}
      .script-body{{max-width:100%!important;width:100%!important;margin:0!important}}
      .chapter-page{{display:none!important}}
      .chapter-page.print-target{{display:block!important}}
      .chapter-page.print-target .chapter-content{{display:block!important}}
      .script-cover{{background:#f7ead8!important;color:#1f1a16!important;border:1px solid #c9a978!important;border-radius:8px!important;margin:0 0 8mm 0!important;padding:8mm 6mm!important;box-shadow:none!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
      .script-cover h1{{color:#3c2112!important;text-shadow:none!important}}
      .script-cover .char-meta,.script-cover .cover-poem{{color:#444!important}}
      .script-section{{background:#fffaf2!important;color:#1f1a16!important;border:1px solid #d8c4a3!important;border-radius:8px!important;padding:5mm!important;margin:0 0 5mm 0!important;box-shadow:none!important;break-inside:auto!important;page-break-inside:auto!important}}
      .script-section p,.script-section li{{color:#1f1a16!important;line-height:1.75!important}}
      .script-section strong{{color:#7a3f12!important;font-weight:800!important}}
      .script-section h3,.script-section h4,.script-chapter > h2{{color:#4a2a16!important;break-after:avoid;page-break-after:avoid}}
      a[href]::after{{content:none!important}}
    }}
  </style>
</head>
<body>
<header class="site-header">
  <a class="logo" href="../../../../index.html">&#128220; LARP Script Archive</a>
  <nav>
    <a href="../../../../index.html">首頁</a>
    <a href="../../index.html">寇侠</a>
    <a href="../index.html">Player</a>
    <a href="index.html">角色劇本</a>
  </nav>
</header>

<div id="password-gate" style="display:none;"></div>
<div id="protected-content" style="display:none;">
<main>
  <nav class="top-nav">
    <a href="../index.html">&#8592; Player Area</a> &#8250;
    <a href="index.html">角色劇本</a> &#8250;
    {name}
  </nav>

  <div class="script-body">

  <div class="script-cover">
    <h1>{name}</h1>
    <p class="char-meta">{identity_label}&#65306;{identity}&#12288;&#65372;&#12288;{age}</p>
{extra_identity_line}    <p class="cover-poem">{cover_quote}</p>
  </div>

  <div class="chapter-tabs" role="tablist">
{chapter_tabs}
  </div>

  <div class="pdf-btn-row">
    <button class="btn-pdf" onclick="printActive()">&#128196; 匯出 PDF（此幕）</button>
  </div>

{chapter_pages}

  </div><!-- /script-body -->
</main>
<footer class="site-footer">
  <a href="../index.html">&#8592; Player Area</a> &nbsp;|&nbsp; LARP Script Archive &nbsp;|&nbsp; <span class="site-version"></span>
</footer>
</div><!-- /protected-content -->

<script src="../../../../assets/js/version.js"></script>
<script src="../../../../assets/js/password-gate.js"></script>
<script>
  initPasswordGate({{
    role: 'kou-xia-player',
    password: 'player',
    icon: '\U0001F4DC',
    title: '{name} — 角色劇本',
    desc: '請輸入玩家密碼以查看角色劇本。',
    back: '../index.html'
  }});
</script>
<!-- GM: chapter unlock codes — 情景二: {code1}  情景三: {code2} -->
<script>
(function(){{
  var SLUG  = '{slug}';
  var CODES = {unlock_codes_json};
  var LSK   = 'kou-xia-' + SLUG + '-unlocked';
  var SSK   = 'kou-xia-' + SLUG + '-page';

  function getUnlocked(){{
    try{{ return JSON.parse(localStorage.getItem(LSK) || '[0]'); }}
    catch(e){{ return [0]; }}
  }}
  function setUnlocked(a){{
    try{{ localStorage.setItem(LSK, JSON.stringify(a)); }}catch(e){{}}
  }}

  function showPage(pi){{
    document.querySelectorAll('.chapter-page').forEach(function(p){{
      p.classList.toggle('active', parseInt(p.dataset.page) === pi);
    }});
    document.querySelectorAll('.tab-btn').forEach(function(b){{
      b.classList.toggle('active', parseInt(b.dataset.page) === pi);
    }});
    try{{ sessionStorage.setItem(SSK, String(pi)); }}catch(e){{}}
  }}

  function revealPage(pi){{
    var lock = document.getElementById('chl-' + pi);
    var body = document.getElementById('chc-' + pi);
    if(lock) lock.style.display = 'none';
    if(body) body.removeAttribute('hidden');
    var tab = document.querySelector('.tab-btn[data-page="' + pi + '"]');
    if(tab) tab.classList.remove('locked');
  }}

  window.tryUnlock = function(pi){{
    var inp = document.getElementById('uinp-' + pi);
    var err = document.getElementById('uerr-' + pi);
    var val = inp ? inp.value.trim() : '';
    if(CODES[pi] !== undefined && val === CODES[pi]){{
      var u = getUnlocked();
      if(u.indexOf(pi) === -1) u.push(pi);
      setUnlocked(u);
      revealPage(pi);
      showPage(pi);
    }} else {{
      if(err){{ err.style.display = ''; setTimeout(function(){{ err.style.display = 'none'; }}, 3000); }}
      if(inp){{ inp.value = ''; inp.focus(); }}
    }}
  }};

  window.switchPage = function(pi){{
    showPage(pi);
    var u = getUnlocked();
    if(u.indexOf(pi) === -1){{
      var inp = document.getElementById('uinp-' + pi);
      if(inp) setTimeout(function(){{ inp.focus(); }}, 50);
    }}
  }};

  window.printActive = function(){{
    var active = document.querySelector('.chapter-page.active');
    document.querySelectorAll('.chapter-page').forEach(function(p){{
      p.classList.toggle('print-target', p === active);
    }});
    window.print();
    setTimeout(function(){{
      document.querySelectorAll('.chapter-page').forEach(function(p){{
        p.classList.remove('print-target');
      }});
    }}, 1200);
  }};

  function initChapterPages(){{
    getUnlocked().forEach(function(pi){{ if(pi > 0) revealPage(pi); }});
    var last = 0;
    try{{ last = parseInt(sessionStorage.getItem(SSK) || '0') || 0; }}catch(e){{}}
    var u = getUnlocked();
    showPage(u.indexOf(last) !== -1 ? last : 0);
    document.querySelectorAll('.unlock-input').forEach(function(inp){{
      inp.addEventListener('keydown', function(e){{
        if(e.key === 'Enter'){{
          window.tryUnlock(parseInt(inp.id.replace('uinp-', '')));
        }}
      }});
    }});
  }}

  /* Init after gate opens (or immediately if already authenticated) */
  var pc = document.getElementById('protected-content');
  if(pc && pc.style.display === 'block'){{
    initChapterPages();
  }} else {{
    document.addEventListener('gate:unlocked', initChapterPages, {{once: true}});
  }}
}})();
</script>
</body>
</html>
'''


# ── Build ─────────────────────────────────────────────────────────────────────

def build_html(fm, pages):
    name           = html_mod.escape(fm.get('name', ''))
    slug           = fm.get('slug', '')
    identity_label = html_mod.escape(fm.get('identity_label', '真名'))
    identity       = html_mod.escape(fm.get('identity', ''))
    age            = html_mod.escape(fm.get('age', ''))
    cover_quote    = html_mod.escape(fm.get('cover_quote', ''))
    extra_identity = fm.get('extra_identity', '')

    extra_identity_line = ''
    if extra_identity:
        ei = html_mod.escape(extra_identity, quote=False)
        extra_identity_line = f'    <p class="char-meta">{ei}</p>\n'

    codes = _codes_json(pages)
    code1 = SCENE_CODES.get(1, '幕二')
    code2 = SCENE_CODES.get(2, '幕三')

    return TEMPLATE.format(
        name=name,
        slug=slug,
        identity_label=identity_label,
        identity=identity,
        age=age,
        cover_quote=cover_quote,
        extra_identity_line=extra_identity_line,
        chapter_tabs=_tabs_html(pages),
        chapter_pages=_pages_html(pages),
        unlock_codes_json=codes,
        code1=code1,
        code2=code2,
    )


print('=== Build player HTML from source md ===')
built = 0
for fname in sorted(os.listdir(SOURCE_DIR)):
    if not fname.endswith('.md'):
        continue
    fpath = os.path.join(SOURCE_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    fm, body = parse_front_matter(content)
    slug  = fm.get('slug', fname[:-3])
    name  = fm.get('name', slug)

    pages = PageBuilder().process(body)
    if not pages:
        print(f'  SKIP {slug} (no pages)')
        continue

    html_content = build_html(fm, pages)

    out_path = os.path.join(OUTPUT_DIR, f'{slug}.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    page_titles = [p['title'] for p in pages]
    print(f'  built: {slug}.html ({name}) — {len(pages)} pages: {page_titles}')
    built += 1

print(f'\nBuilt {built} player HTML files.')
