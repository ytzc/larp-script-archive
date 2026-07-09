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
│       ├── source/              # ✅ 原始劇本 Source of Truth（繁體化整理稿，納入版控）
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

### 🔓 寇俠玩家腳本解鎖碼（GM 用）

每位玩家的腳本分情景一/二/三，玩家不能自行翻到下一情景，需由 GM 宣布並提供解鎖碼：

| 情景 | 解鎖碼 | 時機 |
|------|--------|------|
| 情景一 | （自動開放） | 發本後直接閱讀 |
| 情景二 | **`act2`** | GM 宣布進入情景二時口頭或 DM 通知全體玩家 |
| 情景三 | **`act3`** | GM 宣布進入情景三時口頭或 DM 通知全體玩家 |

> 解鎖碼嵌入在玩家頁面的前端 JavaScript 中（可由頁面原始碼看到）。這是輕度防劇透機制，非強安全機制。

### ⚠️ 密碼保護不是強安全機制

`player/` 與 `gm/` 使用 `docs/assets/js/password-gate.js` 的 client-side 密碼保護。

> **密碼可見於頁面原始碼。** 這只防止隨機瀏覽，不防止有心人。
> 若需要真正的存取控制，請使用 **private repo**。

---

## materials/ 的用途

`materials/` 存放劇本原始資料與外部素材索引，**不部署到 GitHub Pages**。

- `materials/*/source/` — **正式原始劇本來源（Source of Truth）**，繁體化人工整理稿，以角色拼音 slug 命名，含 YAML Front Matter，納入 Git 版控。
- `materials/*/external-links.md` — 外部素材連結索引（PDF、音樂等大型檔案仍保存在個人 iCloud）。

修改角色封面句、身份等 metadata 時，只改 `source/*.md` 的 Front Matter，再執行：

```bash
python3 tools/build-player-script-index.py
```

`docs/scripts/kou-xia/player/scripts/index.html` 的角色卡片由 build script 自動產生，**不應手動修改**。

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

- `materials/*/source/` — 劇本文字整理稿（.md），為 Source of Truth，應 commit。

---

## ⚠️ Public Repo 安全提醒

若此 repo 為 **public**：

- `docs/` 所有頁面對外公開，Player / GM 的密碼可見於頁面原始碼。
- `materials/` 的外部連結（含 iCloud 連結、百度提取碼）也對外公開。
- `gm/` 的 Markdown 文件即使有密碼保護 HTML，直接存取 .md URL 仍可繞過。



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

## 本地端測試與託管 (Local Hosting)

當您在本地修改或新增劇本後，可以使用本專案提供的 `serve.sh` 腳本，直接以 Docker 在本地端區域網路 (LAN) 啟動一個輕量的 Web 伺服器：

```bash
# 給予執行權限（僅需執行一次）
chmod +x serve.sh

# 啟動本地伺服器，預設使用 port 8000
./serve.sh

# 或是指定其他 Port 啟動
./serve.sh 8080
```

執行後，腳本會自動偵測並印出您的本機 IP 網址（例如 `http://localhost:8000/`）。
同時，任何玩家註冊帳號和 GM 存取狀態均會自動持久化保存在本地目錄的 `kou_xia.db` 中。

---

### 🌐 跨裝置連線設定 (特別是使用 WSL2 環境)

如果您的執行環境在 Windows 的 **WSL2** 底下，由於 WSL2 採虛擬化 NAT 網路架構，同個 Wi-Fi 下的手機或平板（通常為 `192.168.x.x` 或 `10.0.0.x`）無法直接連入 WSL 的虛擬 IP。

請依照以下實測成功的方式進行連線與轉發：

1. **查詢 Windows 實體 IP**：
   在 Windows 執行 `ipconfig`，找到「無線區域網路介面卡 Wi-Fi」下的 **IPv4 位址**（例如：`10.0.0.78`）。

2. **設定連接埠轉發 (Port Forwarding)**：
   以 **系統管理員身分 (Administrator)** 開啟 Windows PowerShell，設定 Windows 將對外 8000 埠流量轉發至本機 WSL。請執行：
   ```powershell
   netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=127.0.0.1
   ```
   *(請確保 Windows 防火牆允許 8000 連接埠。)*

3. **外部設備連線**：
   此時，只要手機或平板與您的主機連接在**同一個 Wi-Fi** 中，即可直接在瀏覽器輸入：
   - 📱 **玩家入口**：`http://<您的Windows實體IP>:8000/scripts/kou-xia/player/index.html` (例如 `http://10.0.0.78:8000/scripts/kou-xia/player/index.html`)
   - 🎲 **GM 入口**：`http://<您的Windows實體IP>:8000/scripts/kou-xia/gm/index.html`

4. **關閉轉發（當您不需要使用時）**：
   若想取消 8000 埠的轉發，可以在管理員權限的 Windows PowerShell 執行：
   ```powershell
   netsh interface portproxy delete v4tov4 listenport=8000 listenaddress=0.0.0.0
   ```

---

## Release (發布更新)

⚠️ **重要：發布 Release 與更新，現在開始都必須透過 `release.sh` 進行自動化發布。** 請不要手動設定或推送 Git Tag，以避免本機版本與 Git Pages / Actions 的部署流程發生不一致。

### 自動化發布步驟

```bash
# 升級修訂版本 (Patch):  v1.1.0 → v1.1.1 (適用於 bug 修正、局部微調)
./release.sh patch

# 升級次要版本 (Minor):  v1.1.0 → v1.2.0 (適用於功能新增、新角色)
./release.sh minor

# 升級主要版本 (Major):  v1.1.0 → v2.0.0 (適用於系統重構、大版本更新)
./release.sh major

# 發布指定版本號:
./release.sh v1.2.0
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
