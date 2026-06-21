#!/usr/bin/env python3
"""
Build GM character HTML pages from docs/scripts/kou-xia/gm/characters/*.md files.
Run whenever a character md is updated.
"""
import os, re, html as html_mod

BASE     = '/home/fiducia/larp-script-archive'
CHAR_DIR = os.path.join(BASE, 'docs/scripts/kou-xia/gm/characters')

# Ordered list for prev/next navigation
CHAR_ORDER = [
    ('jin-si-ren',    '金四刀'),
    ('yan-yi',        '嚴逸'),
    ('yan-shi',       '嚴氏'),
    ('jia-san-niang', '賈三娘'),
    ('wang-si-han',   '王思涵'),
    ('nong-sou',      '農叟'),
    ('wang-shun',     '王順'),
    ('diao-wu-er',    '刁五兒'),
    ('zhang-meng',    '張猛'),
]

# Faction color theme: (primary, light_bg, hero_gradient, table_th)
THEMES = {
    'jin-si-ren':    ('#8b0000', '#fff0f0', '#3d0000, #8b0000', '#8b0000'),
    'yan-yi':        ('#003399', '#eef0ff', '#001a4a, #003399', '#003399'),
    'yan-shi':       ('#7a0030', '#fff0f5', '#2a0010, #7a0030', '#7a0030'),
    'jia-san-niang': ('#003399', '#eef0ff', '#001a4a, #003399', '#003399'),
    'wang-si-han':   ('#5a1a7a', '#f5eeff', '#1a003a, #5a1a7a', '#5a1a7a'),
    'nong-sou':      ('#2d5a1a', '#f0fff0', '#1a2a0a, #2d5a1a', '#2d5a1a'),
    'wang-shun':     ('#664400', '#fffae0', '#2a1a00, #664400', '#664400'),
    'diao-wu-er':    ('#1a5050', '#f0ffff', '#0a2020, #1a6060', '#1a5050'),
    'zhang-meng':    ('#444444', '#f5f5f5', '#222222, #555555', '#444444'),
}

# GM banner lines — concise key fact for each character
BANNERS = {
    'jin-si-ren':    '壓軸彩蛋核心：嚴氏（何乃清）即為金四刀失散妹妹，絕對不能提前洩露',
    'yan-yi':        '主謀殘手（綉衣使一號）：指使嚴氏殺冷降塵，目標消滅金四刀',
    'yan-shi':       '凶手：嚴氏（何乃清）受嚴逸指使殺冷降塵，兄妹壓軸彩蛋另一半',
    'jia-san-niang': '歸雪（綉衣使二號）：陣營固定無感情線，移動了冷降塵屍體至庫房',
    'wang-si-han':   '玄甲軍統師旭敏芝：雇用了殺兄凶手王順，本人陣營選擇最靈活',
    'nong-sou':      '大夏武將丁崧：HP 全場最高（40），冷降塵之父，王順是出賣他的叛徒',
    'wang-shun':     '龐萬金：出賣丁崧的叛徒、殺旭晨的凶手，設庫房赤霞香圈套針對農叟',
    'diao-wu-er':    '冷鈺（女扮男裝）：冷佛林之女，復仇者，真實性別是輕鬆彩蛋',
    'zhang-meng':    'NPC 冷降塵（幼名丁典）：農叟之子，屍體藏 3 張線索卡 + 1 封書信',
}


# ── Parsing ───────────────────────────────────────────────────────────────────

def parse_front_matter(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' in line and not line.strip().startswith('-') and not line.startswith('  '):
            k, _, v = line.partition(':')
            fm[k.strip()] = v.strip().strip('"')
    return fm, text[m.end():]


def esc(t):
    return html_mod.escape(str(t), quote=False)


def process_inline(text):
    """HTML-escape, then apply **bold** and `code` Markdown."""
    text = esc(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Strip bare markdown links → just the label
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text


def convert_table(tbl_lines):
    rows = []
    past_sep = False
    for line in tbl_lines:
        line = line.strip()
        if not line.startswith('|'):
            continue
        if re.match(r'^\|[-: |]+\|$', line):
            past_sep = True
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if not past_sep:
            rows.append('<tr>' + ''.join(f'<th>{process_inline(c)}</th>' for c in cells) + '</tr>')
        else:
            rows.append('<tr>' + ''.join(f'<td>{process_inline(c)}</td>' for c in cells) + '</tr>')
    if not rows:
        return ''
    return '<table>\n' + '\n'.join(rows) + '\n</table>'


def section_to_html(lines):
    """Convert lines within an H2 section to HTML."""
    out = []
    i = 0
    n = len(lines)

    while i < n:
        s = lines[i].rstrip()

        # H4
        if s.startswith('#### '):
            out.append(f'<h4>{esc(s[5:].strip())}</h4>')
            i += 1

        # H3
        elif s.startswith('### '):
            out.append(f'<h3>{esc(s[4:].strip())}</h3>')
            i += 1

        # Blockquote → notice-tip
        elif s.startswith('> '):
            bq = []
            while i < n and lines[i].rstrip().startswith('> '):
                bq.append(process_inline(lines[i].rstrip()[2:]))
                i += 1
            out.append('<div class="notice n-tip">' + '<br>'.join(bq) + '</div>')

        # Table
        elif s.startswith('| ') or s.startswith('|--'):
            tbl = []
            while i < n and lines[i].rstrip().startswith('|'):
                tbl.append(lines[i].rstrip())
                i += 1
            t = convert_table(tbl)
            if t:
                out.append(t)

        # Unordered list
        elif s.startswith('- ') or s.startswith('* '):
            items = []
            while i < n and (lines[i].rstrip().startswith('- ') or lines[i].rstrip().startswith('* ')):
                items.append(f'<li>{process_inline(lines[i].rstrip()[2:])}</li>')
                i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')

        # Ordered list
        elif re.match(r'^\d+\. ', s):
            items = []
            while i < n and re.match(r'^\d+\. ', lines[i].rstrip()):
                items.append(f'<li>{process_inline(re.sub(r"^\d+\. ", "", lines[i].rstrip()))}</li>')
                i += 1
            out.append('<ol>' + ''.join(items) + '</ol>')

        # Skip horizontal rules and empty lines
        elif s == '' or s == '---':
            i += 1

        # Paragraph
        else:
            para = []
            while i < n:
                l = lines[i].rstrip()
                if not l or l == '---':
                    break
                if l.startswith(('### ', '#### ', '| ', '> ', '- ', '* ')):
                    break
                if re.match(r'^\d+\. ', l):
                    break
                para.append(process_inline(l))
                i += 1
            if para:
                out.append('<p>' + ' '.join(para) + '</p>')

    return '\n'.join(out)


def parse_sections(body_text):
    """Split md body into [(h2_title_or_None, [lines])] sections."""
    sections = []
    cur_title = None
    cur_lines = []
    skip_h1 = True

    for raw in body_text.split('\n'):
        s = raw.rstrip()

        # Skip the document H1 title line
        if s.startswith('# ') and skip_h1:
            skip_h1 = False
            continue

        if s.startswith('## '):
            sections.append((cur_title, cur_lines))
            cur_title = s[3:].strip()
            cur_lines = []
        else:
            cur_lines.append(raw)

    sections.append((cur_title, cur_lines))
    return sections


# ── HTML template ─────────────────────────────────────────────────────────────

def build_page(fm, body_text, prev_ch, next_ch):
    slug    = fm.get('slug', '')
    name    = fm.get('character', slug)
    updated = fm.get('last_updated', fm.get('review_status', '—'))
    src_pdf = fm.get('source_pdf', '—')
    src_txt = fm.get('source_text', fm.get('source_text_input', '—'))

    primary, light, grad, th = THEMES.get(slug, THEMES['zhang-meng'])
    banner  = BANNERS.get(slug, f'{name} — GM Only')

    sections = parse_sections(body_text)

    # Separate preamble (title=None, before first H2) from content sections
    preamble_lines = []
    content_sections = []
    for title, lines in sections:
        if title is None:
            preamble_lines = lines
        else:
            content_sections.append((title, lines))

    # Extract preamble blockquotes → GM summary notice
    preamble_bq = []
    for line in preamble_lines:
        s = line.rstrip()
        if s.startswith('> '):
            preamble_bq.append(process_inline(s[2:]))

    gm_notice = ''
    if preamble_bq:
        gm_notice = (
            '\n  <div class="notice n-dark">\n'
            '    <strong>GM Summary：</strong><br>\n'
            '    ' + '<br>\n    '.join(preamble_bq) + '\n'
            '  </div>'
        )

    # Build section cards
    cards = []
    for title, lines in content_sections:
        inner = section_to_html(lines)
        if not inner.strip():
            continue
        cards.append(
            f'\n  <h2>{esc(title)}</h2>\n'
            f'  <div class="section">\n'
            f'{inner}\n'
            f'  </div>'
        )
    cards_html = '\n'.join(cards)

    # Prev / Next nav links
    prev_link = f'<a href="{prev_ch[0]}.html">← {esc(prev_ch[1])}</a>' if prev_ch else '<span></span>'
    next_link = f'<a href="{next_ch[0]}.html">{esc(next_ch[1])} →</a>' if next_ch else '<span></span>'

    return f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(name)} GM 筆記 — 寇侠</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI','Microsoft JhengHei','PingFang TC',sans-serif;font-size:15px;line-height:1.75;color:#1c1c1c;background:#faf6ef}}
a{{color:{primary};text-decoration:none}}a:hover{{text-decoration:underline}}
h2{{font-size:1.2em;color:{primary};border-bottom:2px solid {primary};padding-bottom:.3em;margin:2em 0 .7em}}
h3{{font-size:1em;color:#333;margin:1em 0 .4em;font-weight:600}}
h4{{font-size:.93em;color:#555;margin:.8em 0 .2em}}
ul,ol{{margin:.4em 0 .8em 1.4em}}li{{margin-bottom:.3em}}
p{{margin-bottom:.8em}}
code{{background:#f0f0f0;padding:.1em .4em;border-radius:3px;font-size:.88em}}
strong{{font-weight:700}}
.gm-banner{{position:sticky;top:0;z-index:999;background:#8b0000;color:#fff;padding:.5em 1em;text-align:center;font-weight:700;font-size:.88em;letter-spacing:.3px;border-bottom:3px solid #ff4444}}
.top-nav{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5em;padding:.6em 1.2em;background:#fff3e8;border-bottom:1px solid #e0d0c0;font-size:.85em}}
.top-nav .nav-links,.top-nav .page-nav{{display:flex;gap:1em;align-items:center}}
.top-nav a{{color:{primary}}}
.wrapper{{max-width:960px;margin:0 auto;padding:1.5em 1em 5em}}
.section{{background:#fff;padding:1.3em 1.6em;margin-bottom:1.4em;border-radius:4px;box-shadow:0 1px 5px rgba(0,0,0,.1)}}
.notice{{padding:.75em 1em;margin:.7em 0;border-radius:4px;border-left:4px solid}}
.n-tip{{background:#fff8e0;border-color:#e0a800}}
.n-dark{{background:#1a1a1a;color:#eee;border-color:#888;padding:1em 1.4em}}
.n-dark strong{{color:#fff}}
table{{width:100%;border-collapse:collapse;margin:.8em 0;font-size:.88em}}
th{{background:{th};color:#fff;padding:.5em .8em;text-align:left;font-weight:600}}
td{{padding:.45em .8em;border-bottom:1px solid #e8ddd0;vertical-align:top}}
tr:nth-child(even) td{{background:{light}}}
.char-hero{{background:linear-gradient(135deg,{grad});color:#fff;border-radius:6px;padding:1.5em 2em;margin:1em 0}}
.hero-name{{font-size:2em;font-weight:700;margin-bottom:.2em}}
.hero-sub{{font-size:.88em;color:rgba(255,255,255,.72);margin:.2em 0}}
.hero-src{{font-size:.82em;color:rgba(255,255,255,.6);margin-top:.5em}}
.footer-nav{{margin-top:2em;font-size:.85em;color:#666;display:flex;gap:1em;flex-wrap:wrap}}
@media(max-width:600px){{.top-nav{{flex-direction:column;align-items:flex-start}}.section{{padding:1rem 1.1rem}}}}
</style>
</head>
<body>
<div class="gm-banner">🔒 GM Only — {esc(banner[:90])}</div>
<nav class="top-nav">
  <div class="nav-links">
    <a href="../../../../index.html">首頁</a> ›
    <a href="../../index.html">寇侠</a> ›
    <a href="../index.html">GM Area</a> ›
    <a href="index.html">角色筆記</a> ›
    {esc(name)}
  </div>
  <div class="page-nav">{prev_link} {next_link}</div>
</nav>
<div class="wrapper">

  <div class="char-hero">
    <div class="hero-name">{esc(name)}</div>
    <div class="hero-sub">GM 專用筆記 · 最後更新：{esc(updated)}</div>
    <div class="hero-src">來源：{esc(src_pdf)} &nbsp;·&nbsp; {esc(src_txt)}</div>
  </div>
{gm_notice}
{cards_html}

  <div class="footer-nav">
    {prev_link} &nbsp;|&nbsp;
    <a href="index.html">角色列表</a> &nbsp;|&nbsp;
    {next_link}
  </div>
</div>
</body>
</html>
'''


# ── Main ──────────────────────────────────────────────────────────────────────

print('=== Build GM character HTML pages ===')
built = 0
order_slugs = [s for s, _ in CHAR_ORDER]

for idx, (slug, name) in enumerate(CHAR_ORDER):
    md_path = os.path.join(CHAR_DIR, f'{slug}.md')
    if not os.path.exists(md_path):
        print(f'  SKIP {slug}.md (not found)')
        continue

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fm, body = parse_front_matter(content)
    if not fm:
        fm['character'] = name
        fm['slug'] = slug

    prev_ch = CHAR_ORDER[idx - 1] if idx > 0 else None
    next_ch = CHAR_ORDER[idx + 1] if idx < len(CHAR_ORDER) - 1 else None

    html = build_page(fm, body, prev_ch, next_ch)

    out_path = os.path.join(CHAR_DIR, f'{slug}.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    sec_count = len([s for s, _ in parse_sections(body) if s])
    print(f'  built: {slug}.html ({name}) — {sec_count} sections')
    built += 1

print(f'\nBuilt {built} GM character HTML files.')
