# LARP Script Archive

A personal archive for LARP scripts, story settings, character profiles, and session notes.

**GitHub Pages：[https://ytzc.github.io/larp-script-archive/](https://ytzc.github.io/larp-script-archive/)**

---

## 用途

整理劇本殺 / LARP / scripted roleplay 的劇本資料，並透過 GitHub Pages 發佈整理後的版本。

---

## 目錄結構

```
larp-script-archive/
├── docs/                         # GitHub Pages 網站來源（只部署此資料夾）
│   ├── index.html
│   ├── assets/
│   │   ├── css/style.css
│   │   └── js/password-gate.js  # Client-side 密碼 gate（非強安全機制）
│   └── scripts/
│       └── kou-xia/             # 劇本：寇侠
│           ├── index.html        # 劇本首頁（三個入口卡片）
│           ├── scripts/          # 整理稿 Markdown（含來源備註）
│           ├── player/           # 🎭 玩家區，需要玩家密碼
│           └── gm/               # 🎲 GM 區，需要 GM 密碼
├── materials/                    # 原始資料與外部素材索引
│   └── kou-xia/
│       ├── input-text/          # ✅ 原始劇本 Source of Truth（繁體化整理稿，納入版控）
│       ├── external-links.md    # 外部連結（iCloud、百度網盤等）
│       ├── inventory.md         # 素材清單
│       └── notes.md             # 整理筆記
├── .github/workflows/
│   └── deploy-pages-on-tag.yml  # 只部署 ./docs
└── .gitignore
```

---

## 每個劇本的三種區域

每本劇本分為三個區域：

| 區域 | 資料夾 | 密碼 | 用途 |
|------|--------|------|------|
| Public | `public/` | 不需要 | 無劇透公開資訊：簡介、世界觀、角色公開身份 |
| Player | `player/` | 玩家密碼 | 玩家說明、規則、玩家版角色資訊、線索整理 |
| GM | `gm/` | GM 密碼 | 主持人筆記、完整真相、時間軸、spoilers |

### ⚠️ 密碼保護不是強安全機制

`player/` 與 `gm/` 使用 `docs/assets/js/password-gate.js` 的 client-side 密碼保護。

> **密碼可見於頁面原始碼。** 這只防止隨機瀏覽，不防止有心人。
> 若需要真正的存取控制，請使用 **private repo**。

---

## materials/ 的用途

`materials/` 存放劇本原始資料與外部素材索引，**不部署到 GitHub Pages**。

- `materials/*/input-text/` — **正式原始劇本來源（Source of Truth）**，繁體化人工整理稿，納入 Git 版控。
- `materials/*/external-links.md` — 外部素材連結索引（PDF、音樂等大型檔案仍保存在個人 iCloud）。

---

## 不要放進 repo 的東西

> **請勿將以下檔案直接 commit 到 GitHub：**
>
> - PDF（角色劇本、組織手冊）
> - 音樂 / BGM / 音效
> - 圖片 / 插圖（除非確認授權與公開意願）
> - ZIP 壓縮檔
>
> 上述資料請保存在個人 iCloud 或本地端，透過 `materials/*/external-links.md` 以外部連結索引。

**納入版控的例外：**

- `materials/*/input-text/` — 劇本文字整理稿（.md），為 Source of Truth，應 commit。

---

## ⚠️ Public Repo 安全提醒

若此 repo 為 **public**：

- `docs/` 所有頁面對外公開，Player / GM 的密碼可見於頁面原始碼。
- `materials/` 的外部連結（含 iCloud 連結、百度提取碼）也對外公開。
- `gm/` 的 Markdown 文件即使有密碼保護 HTML，直接存取 .md URL 仍可繞過。

---

## OCR 補拍流程（寇俠 / 其他劇本通用）

當劇本 PDF 掃描因裝訂陰影或印刷品質導致部分頁面無法讀取時，需要補拍後重新提取文字。

### 補拍操作步驟

1. **拍攝補拍頁面**
   - 解析度 ≥ 300 DPI（印刷字體過小的頁面建議 600 DPI 或 2× 縮放）
   - 拍攝時盡量壓平書本內側，減少裝訂陰影
   - 命名格式：`角色拼音-pXXX-retake.png`（例：`jia-san-niang-p007-retake.png`）
   - 存放位置：`local-private/<劇本>/retake-photos/`（已 gitignore）

2. **執行 OCR 提取**（在 Claude Code 中）

   **通用 Prompt 模板：**
   ```
   請閱讀這張劇本掃描圖片，提取其中的所有文字內容。

   背景說明：
   - 這是《[劇本名稱]》LARP劇本，角色：[角色名稱]，頁碼：[頁碼]
   - 先前的OCR提取此頁因裝訂陰影遮蔽無法讀取，請盡力提取可見文字

   輸出格式：
   - Markdown，保留段落結構（方框內容用 blockquote 或 code block 呈現）
   - 原文語言保留（簡/繁體不互轉）
   - 不確定詞語加 [需要人工確認：說明原因]
   - 無法讀取的部分加 [需要補拍：說明原因]
   - 不要腦補或改寫任何劇情內容
   - GM隔頁說明（紅色橫幅文字）不需要輸出
   ```

   更多模板（跨頁比對、印刷過淡頁面等）請見 GM 區的 [OCR 提示詞指引](docs/scripts/kou-xia/gm/ocr-prompt-guide.html)。

3. **整合進 md 整理稿**
   - 找到對應角色 `docs/scripts/<劇本>/scripts/角色名.md` 中的 `[需要補拍]` 段落
   - 用新提取的文字替換，保留低信心詞語的 `[需要人工確認]` 標記
   - 同步更新 `local-private/<劇本>/clean-md/script-book/角色名.md`

4. **重新生成角色 HTML**
   ```
   根據更新後的 xxx.md 重新生成 player/scripts/xxx.html
   ```

### 補拍優先順序（寇俠）

| 優先級 | 角色 | 頁面 | 原因 |
|--------|------|------|------|
| 🔴 高 | 賈三娘 | 頁2–9 | 整個劇本幾乎不可讀；感情線對象不明 |
| 🔴 高 | 王思涵 | 頁2–10 | 除封面外全部缺失 |
| 🔴 高 | 嚴氏 | 頁6、頁8 | 凶手行動指令頁遮蔽（案件核心） |
| 🔴 高 | 農叟 | 頁7 | 特殊技能規則方框（搏殺關鍵） |
| 🟡 中 | 刁五兒 | 頁7 | HP/武力數值未確認 |
| 🟡 中 | 王順 | 頁3–9 | 核心抉擇段落多行遮蔽 |
| 🟡 中 | 張猛（NPC） | 頁4–6 | GM指引印刷過淡（NPC互動說明） |

完整清單見 [gm/rephotograph.html](docs/scripts/kou-xia/gm/rephotograph.html)（需 GM 密碼）。

---

## 新增一本劇本

```bash
# 建立素材索引資料夾
cp -r materials/kou-xia materials/<new-script-slug>

# 建立公開網站資料夾
cp -r docs/scripts/kou-xia docs/scripts/<new-script-slug>
```

再到 `docs/index.html` 加入新的劇本卡片。

---

## Release

This repository deploys GitHub Pages when a version tag is pushed.
Use `release.sh` to automate version bumping, tagging, and pushing.

```bash
# Bump patch version:  v0.1.0 → v0.1.1
./release.sh patch

# Bump minor version:  v0.1.0 → v0.2.0
./release.sh minor

# Bump major version:  v0.1.0 → v1.0.0
./release.sh major

# Release a specific version:
./release.sh v0.2.0
```

The script will:

1. Check you are on `main` with a clean working tree (or prompt to auto-commit).
2. Compute the next version from the latest tag.
3. Ask for confirmation before doing anything.
4. Run `git push origin main`, create the tag, and push it.

The tag push triggers the GitHub Pages deployment workflow (`.github/workflows/deploy-pages-on-tag.yml`), which deploys only the `./docs` folder.

> **First-time setup:** In the GitHub repo go to **Settings → Pages** and set Source to `GitHub Actions`.

---

## 授權

本 repo 為個人私用資料整理，劇本內容版權歸原作者（K 的遊戲工作室等）所有。
