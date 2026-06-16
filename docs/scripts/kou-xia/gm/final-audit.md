---
visibility: gm-only
spoiler_level: high
---

# 寇侠 GM Reference — Final Audit Report

> ⚠️ **GM ONLY — SPOILER WARNING**
> This document is for the host only. Do not share with players.
> Client-side password gate does NOT prevent direct URL access to this file.

## Audit Date

2026-06-16

## Git Version

v0.1.11 (commit af8487a) + minor fix commit (final-audit)

## Checked Files

| File | Status |
|------|--------|
| `gm/index.html` | ✓ Present, password gate active |
| `gm/relationship-map.html` | ✓ Present, all 9 character links added |
| `gm/host-notes.html` | ✓ Present |
| `gm/spoilers.html` | ✓ Present |
| `gm/todo.html` | ✓ Present, updated to 5 high-priority items |
| `gm/characters/index.html` | ✓ Present, all 9 cards linked |
| `gm/characters/yan-shi.html` | ✓ Present |
| `gm/characters/yan-yi.html` | ✓ Present |
| `gm/characters/jin-si-ren.html` | ✓ Present |
| `gm/characters/jia-san-niang.html` | ✓ Present |
| `gm/characters/wang-si-han.html` | ✓ Present |
| `gm/characters/nong-sou.html` | ✓ Present |
| `gm/characters/wang-shun.html` | ✓ Present |
| `gm/characters/diao-wu-er.html` | ✓ Present |
| `gm/characters/zhang-meng.html` | ✓ Present |
| `gm/characters/*.md` (9 files) | ✓ Present, all with gm-only frontmatter |

## Character Coverage

All 9 characters complete (8 player + 1 NPC):

| 角色 | slug | HTML | MD | OCR 品質 |
|------|------|:----:|:--:|---------|
| 金四刃 | jin-si-ren | ✓ | ✓ | ★★☆☆☆ 差 |
| 嚴逸 | yan-yi | ✓ | ✓ | ★★★☆☆ 中 |
| 嚴氏 | yan-shi | ✓ | ✓ | ★★★☆☆ 中 |
| 賈三娘 | jia-san-niang | ✓ | ✓ | ★★★☆☆ 中 |
| 王思涵 | wang-si-han | ✓ | ✓ | ★★★☆☆ 中 |
| 農叟 | nong-sou | ✓ | ✓ | ★★★☆☆ 中 |
| 王順 | wang-shun | ✓ | ✓ | ★★★☆☆ 中 |
| 刁五兒 | diao-wu-er | ✓ | ✓ | ★★★☆☆ 中 |
| 張猛（NPC） | zhang-meng | ✓ | ✓ | ★★★☆☆ 中 |

## GM Pages

- `gm/index.html` links to `characters/index.html` ✓
- `characters/index.html` links to all 9 character pages ✓
- All character pages have back link to `characters/index.html` ✓
- `relationship-map.html` has links to all 9 character pages ✓
- No public/player pages link directly to GM spoiler content ✓
- `docs/scripts/kou-xia/index.html` links to `gm/index.html` with visible GM-Only badge — correct and expected ✓

## Markdown Notes

- All 9 `characters/*.md` files have `visibility: gm-only` and `spoiler_level: high` in frontmatter ✓
- Content is organized summary/tables — no raw PDF transcription ✓
- OCR quality noted with ★ ratings ✓
- Human review items flagged in each MD ✓

## Security / Publishing Notes

- GM pages use client-side password gate (password: "gm") — visible in page source
- **This is not strong security.** Anyone with the URL can access `.html` or `.md` files directly.
- All GM HTML pages have sticky red `.gm-banner` with GM-only notice ✓
- `gm/index.html` and `gm/characters/index.html` have explicit player-warning notices ✓
- If the repo is public, all GM content is publicly accessible by direct URL

## Git Ignore Status

`.gitignore` covers:
- `local-private/` ✓
- `*.pdf` (with exception `!docs/scripts/kou-xia/gm/pdf/DM手册.pdf`) ✓
- `*.mp3`, `*.wav`, `*.aac`, `*.zip`, `*.rar`, `*.7z` ✓
- Node, Python, OS artifacts ✓

## Sensitive Files Check

```
git ls-files | grep -E 'local-private|\.pdf$|\.mp3$|\.wav$|\.zip$|\.rar$|\.7z$|extracted-text'
```

Result: **CLEAN** — no sensitive files tracked.

Only tracked PDF: `docs/scripts/kou-xia/gm/pdf/DM手册.pdf` (explicitly approved).

## Broken Link Check

- All 9 character HTML pages: present ✓
- `characters/index.html`: links to all 9 character slugs ✓
- `relationship-map.html`: links to all 9 `characters/*.html` slugs ✓
- `gm/index.html`: links to `characters/index.html` ✓
- Character pages: all have `href="index.html"` back link ✓

Note: No prev/next sequential navigation between character pages (back-to-index only). This is by design for this version.

## Remaining Manual Review Items (Before Hosting)

Ordered by priority:

1. **賈三娘感情線對象** — 頁7 OCR complete failure. HIGHEST PRIORITY, affects faction balance.
2. **金四刃「復盤專用」頁** — 可能有隱藏 GM 揭露指引。需人工確認。
3. **農叟搏殺特殊規則** — 頁7特殊規則方框遮擋，農叟全場最高HP的規則影響戰鬥結局。
4. **各角色個人勝利條件** — 頁7/8 普遍受限，所有角色需人工核對。
5. **農叟↔金四刃「差錯」具體內容** — 頁2下半裝訂遮擋。
6. **張猛 NPC 行動序列** — 頁5-6 嚴重過曝，NPC 指令不完整。
7. **王思涵真名** — 旭敏芝 or 阳敏芝？需實體手冊確認。

## Push Instructions

All local commits are at v0.1.11 (or one minor fix commit ahead). To deploy to GitHub Pages:

```bash
git push origin main
git push origin v0.1.11
```

If a new commit was created during final audit:
```bash
git push origin main
# tag and push if desired:
# git tag v0.1.12
# git push origin v0.1.12
```

## Final Status

| Check | Result |
|-------|--------|
| Sensitive files in git | ✅ None |
| .gitignore complete | ✅ Yes |
| All 15 GM pages present | ✅ Yes |
| All 9 character pages | ✅ Yes |
| All 9 character MDs | ✅ Yes |
| GM-only warnings | ✅ All pages |
| Navigation links | ✅ Back links, relationship-map |
| Public pages leaking GM | ✅ No (only expected GM entry card) |
| todo.html up to date | ✅ 5 high-priority items |
| Ready to push | ✅ Yes (manual push required) |
