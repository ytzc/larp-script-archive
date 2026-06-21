#!/usr/bin/env python3
"""
build-player-script-index.py
─────────────────────────────
讀取 materials/kou-xia/source/*.md 的 YAML Front Matter，
自動產生 docs/scripts/kou-xia/player/scripts/index.html。

用法：
    python3 tools/build-player-script-index.py

只有角色卡片區塊（<h2>玩家角色</h2> 到 <hr /> 之間）會被替換。
其餘 HTML（header、password-gate、CSS、footer、script）保持不變。
"""

import os, re, glob

# ── 路徑設定 ─────────────────────────────────────────────────────
SOURCE_DIR   = 'materials/kou-xia/source'
INDEX_HTML   = 'docs/scripts/kou-xia/player/scripts/index.html'

# ── 玩家角色的顯示順序（依遊戲慣例） ──────────────────────────────
PLAYER_ORDER = [
    'diao-wu-er', 'jia-san-niang', 'jin-si-dao',
    'nong-sou', 'wang-shun', 'wang-si-han',
    'yan-shi', 'yan-yi',
]


# ── Front Matter 解析 ─────────────────────────────────────────────
def parse_front_matter(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if not content.startswith('---'):
        return {}
    end = content.find('\n---\n', 3)
    if end == -1:
        return {}
    fm_block = content[3:end].strip()
    meta = {}
    for line in fm_block.splitlines():
        if ':' not in line:
            continue
        key, _, val = line.partition(':')
        meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta


# ── 卡片 HTML 產生 ────────────────────────────────────────────────
def render_card(m, is_npc=False):
    slug      = m.get('slug', '')
    name      = m.get('name', slug)
    label     = m.get('identity_label', '真名')
    identity  = m.get('identity', '')
    extra     = m.get('extra_identity', '')
    age       = m.get('age', '')
    quote     = m.get('cover_quote', '')
    status    = m.get('status', '已以 source 補強')

    npc_class  = ' npc-card' if is_npc else ''
    npc_suffix = '（NPC）' if is_npc else ''
    alias_parts = [f'{label}：{identity}']
    if extra:
        alias_parts.append(extra)
    alias_parts.append(age)
    alias_str = ' · '.join(p for p in alias_parts if p)

    return (
        f'    <a class="char-card{npc_class}" href="{slug}.html">\n'
        f'      <div class="char-name">{name}{npc_suffix}</div>\n'
        f'      <div class="char-alias">{alias_str}</div>\n'
        f'      <div class="char-cover">{quote}</div>\n'
        f'      <span class="ocr-badge ocr-good">{status}</span>\n'
        f'    </a>'
    )


# ── 載入所有 source ──────────────────────────────────────────────
all_meta = {}
for path in glob.glob(f'{SOURCE_DIR}/*.md'):
    m = parse_front_matter(path)
    slug = m.get('slug')
    if slug:
        all_meta[slug] = m

# ── 分類：player / npc ────────────────────────────────────────────
players = []
for slug in PLAYER_ORDER:
    if slug in all_meta:
        players.append(all_meta[slug])
# 未在順序清單中的 player 型別附加到最後
for slug, m in sorted(all_meta.items()):
    if m.get('type') == 'player' and slug not in PLAYER_ORDER:
        players.append(m)

npcs = [m for slug, m in sorted(all_meta.items()) if m.get('type') == 'npc']


# ── 產生卡片區塊 HTML ─────────────────────────────────────────────
def render_section(title, cards, is_npc=False):
    lines = [f'  <h2>{title}</h2>', '  <div class="char-grid">', '']
    for m in cards:
        lines.append(render_card(m, is_npc=is_npc))
        lines.append('')
    lines.append('  </div>')
    return '\n'.join(lines)

player_block = render_section('玩家角色', players, is_npc=False)
npc_block    = render_section('NPC', npcs, is_npc=True)
cards_html   = player_block + '\n\n' + npc_block


# ── 讀取原始 index.html，替換卡片區塊 ────────────────────────────
with open(INDEX_HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# 替換 <h2>玩家角色</h2> ... <hr /> 之間的內容
pattern = r'(  <h2>玩家角色</h2>.*?)(?=\n  <hr />)'
replacement = cards_html
new_html = re.sub(pattern, replacement, html, flags=re.DOTALL)

if new_html == html:
    print('⚠️  找不到替換標記，index.html 未修改。')
    print('   請確認 index.html 中有 <h2>玩家角色</h2> 和 <hr /> 標記。')
else:
    # 同步更新 notice 中的路徑說明
    new_html = new_html.replace(
        '各角色劇本均已以人工整理版文字（input-text）核對補強，正文忠實呈現原始劇本。',
        '各角色劇本均已以 source 人工整理版核對補強，正文忠實呈現原始劇本。'
    )
    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'✅ {INDEX_HTML} 已更新')
    print(f'   玩家角色：{len(players)} 個')
    print(f'   NPC：{len(npcs)} 個')
    print()
    for m in players + npcs:
        print(f'   {m["name"]} ({m["slug"]}.html)')
