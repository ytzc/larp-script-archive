#!/usr/bin/env python3
"""
Build player HTML scripts from corrected source md files.
Also does global 金四刀 → 金四刀 rename across the repo.
"""
import os, re, html as html_mod

# ── Config ─────────────────────────────────────────────────────────────────
BASE = '/home/fiducia/larp-script-archive'
SOURCE_DIR = os.path.join(BASE, 'materials/kou-xia/source')
OUTPUT_DIR = os.path.join(BASE, 'docs/scripts/kou-xia/player/scripts')

# ── Step 1: Global rename 金四刀 → 金四刀 ──────────────────────────────────
print('=== Step 1: Global rename 金四刀 → 金四刀 ===')
EXTS = ('.md', '.html', '.py', '.txt')
renamed = 0
for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for f in files:
        if not f.endswith(EXTS):
            continue
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            if '金四刀' in content:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(content.replace('金四刀', '金四刀'))
                print(f'  renamed: {path.replace(BASE+"/", "")}')
                renamed += 1
        except Exception as e:
            print(f'  skip {path}: {e}')
print(f'Renamed {renamed} files.\n')

# ── Step 2: Build player HTML from source md ────────────────────────────────
print('=== Step 2: Build player HTML from source md ===')

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
    """Strip OCR notes, escape HTML, apply bold."""
    text = re.sub(r'\[待人工確認[：:][^\]]*\]', '', text)
    text = html_mod.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    return text

def md_to_body(body_text):
    lines = body_text.split('\n')
    out = []
    in_chapter = False
    in_section = False
    para = []

    def flush_para():
        nonlocal para
        if para:
            content = '\n'.join(l for l in para if l)
            if content.strip():
                out.append(f'    <p>{content}</p>')
        para = []

    def close_section():
        nonlocal in_section
        flush_para()
        if in_section:
            out.append('  </div>')
            out.append('')
            in_section = False

    def close_chapter():
        nonlocal in_chapter
        close_section()
        if in_chapter:
            out.append('  </div><!-- /script-chapter -->')
            out.append('')
            in_chapter = False

    skip_first_h1 = True

    for line in lines:
        stripped = line.rstrip()

        if stripped.startswith('# '):
            title = stripped[2:].strip()
            # Skip the document title line like "# 【角色名】文字劇本"
            if skip_first_h1 and ('文字劇本' in title or title.startswith('【')):
                skip_first_h1 = False
                continue
            skip_first_h1 = False
            close_chapter()
            out.append('  <div class="script-chapter">')
            out.append(f'  <h2>{html_mod.escape(title)}</h2>')
            out.append('')
            in_chapter = True

        elif stripped.startswith('## '):
            title = stripped[3:].strip()
            close_section()
            out.append('  <div class="script-section">')
            out.append(f'    <h3>{html_mod.escape(title)}</h3>')
            in_section = True

        elif stripped.startswith('### ') or stripped.startswith('#### '):
            flush_para()
            title = re.sub(r'^#{3,5} ', '', stripped).strip()
            out.append(f'    <h4>{html_mod.escape(title)}</h4>')

        elif stripped == '' or stripped == '---':
            flush_para()

        else:
            cleaned = process_inline(stripped)
            if cleaned.strip():
                para.append(cleaned)

    close_chapter()
    return '\n'.join(out)

TEMPLATE = '''\
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{name} &#8212; 角色劇本 &#8212; 寇侠</title>
  <link rel="stylesheet" href="../../../../assets/css/style.css" />
  <style>
    .script-body{{max-width:750px;margin:0 auto}}
    .script-cover{{background:linear-gradient(150deg,#2a0808 0%,#4a1515 100%);color:#f5e6d3;border:2px solid #8b6040;border-radius:10px;padding:2.5rem 2rem;margin-bottom:1.5rem;text-align:center}}
    .script-cover h1{{font-size:2.4rem;margin:0 0 .3rem;letter-spacing:.18em;color:#f5e6d3;border:none;text-shadow:0 1px 4px rgba(0,0,0,.4)}}
    .script-cover .char-meta{{color:#c4a87a;font-size:.9rem;margin:.3rem 0;letter-spacing:.04em}}
    .script-cover .cover-poem{{font-style:italic;color:#b89870;margin-top:.9rem;font-size:.88rem;border-top:1px solid rgba(255,255,255,.18);padding-top:.8rem;letter-spacing:.03em}}
    .pdf-btn-row{{display:flex;justify-content:flex-end;margin-bottom:1.2rem}}
    .btn-pdf{{background:#8b0000;color:#fff;border:none;padding:.55rem 1.3rem;border-radius:5px;cursor:pointer;font-size:.88rem;font-family:inherit;letter-spacing:.04em;transition:background .15s}}
    .btn-pdf:hover{{background:#5a0000}}
    .script-chapter{{margin-bottom:2rem}}
    .script-chapter > h2{{color:var(--red,#8b0000);border-bottom:2px solid #c8b89a;padding-bottom:.5rem;font-size:1.3rem;margin-top:0;margin-bottom:1.2rem;letter-spacing:.06em}}
    .script-section{{background:#fff;border:1px solid #e0d4c0;border-radius:6px;padding:1.4rem 1.8rem;margin-bottom:1.1rem}}
    .script-section h3{{color:var(--red,#8b0000);margin-top:0;border-bottom:1px solid #e0d4c0;padding-bottom:.4rem;font-size:1rem;letter-spacing:.04em}}
    .script-section p{{margin:.8rem 0;line-height:1.9;text-align:justify}}
    .script-section h4{{color:#4a3a2a;font-size:.92rem;margin:1rem 0 .3rem;font-weight:600}}
    @media(max-width:600px){{
      .script-section{{padding:1rem 1.1rem}}
      .script-cover{{padding:1.8rem 1.2rem}}
      .script-cover h1{{font-size:1.9rem}}
    }}
    @media print{{
      .site-header,.top-nav,.pdf-btn-row,footer.site-footer,#password-gate,.notice{{display:none!important}}
      body{{background:#fff;color:#000;font-size:11pt}}
      .script-body{{max-width:100%;margin:0}}
      .script-cover{{background:#f8f0e8!important;color:#000!important;border:1px solid #999!important;-webkit-print-color-adjust:exact;print-color-adjust:exact;page-break-after:always;border-radius:4px}}
      .script-cover h1{{color:#1a0000!important;font-size:2rem;text-shadow:none}}
      .script-cover .char-meta,.script-cover .cover-poem{{color:#333!important}}
      .script-chapter{{page-break-before:auto}}
      .script-chapter > h2{{color:#1a0000!important;border-color:#999!important}}
      .script-section{{page-break-inside:avoid;border:1px solid #ccc!important;padding:1rem 1.2rem}}
      a[href]:after{{content:none!important}}
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

  <div class="pdf-btn-row"><button class="btn-pdf" onclick="window.print()">&#128196; 匯出 PDF</button></div>

{body}
  </div><!-- /script-body -->
</main>
<footer class="site-footer">
  <a href="../index.html">&#8592; Player Area</a> &nbsp;|&nbsp; LARP Script Archive &nbsp;|&nbsp; <span class="site-version"></span>
</footer>
</div>

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
</body>
</html>
'''

def build_html(fm, body_html):
    name = html_mod.escape(fm.get('name', ''))
    identity_label = html_mod.escape(fm.get('identity_label', '真名'))
    identity = html_mod.escape(fm.get('identity', ''))
    age = html_mod.escape(fm.get('age', ''))
    cover_quote = html_mod.escape(fm.get('cover_quote', ''))
    extra_identity = fm.get('extra_identity', '')

    extra_identity_line = ''
    if extra_identity:
        ei = html_mod.escape(extra_identity, quote=False)
        extra_identity_line = f'    <p class="char-meta">{ei}</p>\n'

    return TEMPLATE.format(
        name=name,
        identity_label=identity_label,
        identity=identity,
        age=age,
        cover_quote=cover_quote,
        extra_identity_line=extra_identity_line,
        body=body_html,
    )

built = 0
for fname in sorted(os.listdir(SOURCE_DIR)):
    if not fname.endswith('.md'):
        continue
    fpath = os.path.join(SOURCE_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    fm, body = parse_front_matter(content)
    slug = fm.get('slug', fname[:-3])
    name = fm.get('name', slug)

    body_html = md_to_body(body)
    html_content = build_html(fm, body_html)

    out_path = os.path.join(OUTPUT_DIR, f'{slug}.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'  built: {slug}.html ({name})')
    built += 1

print(f'\nBuilt {built} player HTML files.')
print('Done.')
