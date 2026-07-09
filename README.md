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

當您在本地修改或新增劇本後，本專案支援以兩種方式在本地端區域網路 (LAN) 啟動一個輕量的 Web 伺服器，使本機電腦、手機、平板皆可連入測試。

---

### 💻 方式一：使用 Docker Desktop for Windows (Windows 平台最佳推薦)

在 Windows 系統下，使用 **Docker Desktop for Windows** 搭配 WSL2 是最簡便、最穩定的本地部署方式。**它會自動處理 Windows 與 WSL 之間的 Port Forwarding 網路轉發，完全免去複雜的 `netsh` 網路指令設定！**

#### 1. 建置 Docker 映像檔 (僅需在專案修改後執行)
打開 PowerShell 並進入專案根目錄，執行以下指令：
```powershell
docker build -t larp-script-archive -f Dockerfile .
```

#### 2. 一鍵啟動容器 (推薦使用環境變數或設定檔)

為了避免每次都要在指令最後手動輸入 `8787 docs`，我們已將系統升級為 **「智慧環境變數與預設值」** 機制。您可以使用以下兩種更優雅的方式啟動：

##### 👍 推薦作法 A：使用環境設定檔 (`.env`) ── 最輕鬆、免打長指令
在專案根目錄（`larp-script-archive/`）下建立一個名為 **`.env`** 的文字檔案，內容填入您的個人設定：
```ini
PORT=8787
WEB_DIR=docs
HOST_IP=10.0.0.78
```
之後啟動容器時，**只需在 PowerShell 輸入這一行**，Docker 就會自動載入所有設定並在日誌輸出手機連線網址：
```powershell
docker run -it --rm --env-file .env -p 0.0.0.0:8787:8787 -v "${PWD}:/workspace" larp-script-archive
```
*(注意：`-p 0.0.0.0:8787:8787` 中的兩個 Port 號碼，請與您 `.env` 檔案中的 `PORT` 保持一致。)*

##### 作法 B：使用行內環境變數 (Inline Env)
若不想建立 `.env` 檔案，也可以直接在指令中用 `-e` 帶入變數：
```powershell
docker run -it --rm -e PORT=8787 -e HOST_IP=10.0.0.78 -p 0.0.0.0:8787:8787 -v "${PWD}:/workspace" larp-script-archive
```

##### 💡 傳統相容作法（CLI 參數）
系統依然支援舊有參數方式。如果指令最後有帶參數，將會優先覆蓋環境變數與預設值：
```powershell
docker run -it --rm -e HOST_IP=10.0.0.78 -p 0.0.0.0:8787:8787 -v "${PWD}:/workspace" larp-script-archive 8787 docs
```
*(如果完全不帶任何參數與環境變數，系統將自動套用安全預設值：Port `8000` 與 `docs` 目錄。)*

> **💡 參數解析：**
> - `-it`：允許您在終端機中看到即時的登入、註冊日誌，並可隨時按 `Ctrl + C` 停止伺服器。
> - `-v "${PWD}:/workspace"`：將當前資料夾掛載進容器中，任何網頁或資料庫修改（`kou_xia.db`）皆會同步與持久化保存在本地。

#### 3. 如何改在「背景執行」？(Detached Mode)

如果您希望伺服器持續在背景執行，不佔用 PowerShell 視窗，可以將前述指令中的 `-it --rm` 改成 **`-d`** (Detached) 並加上 **`--name larp-server`** (命名容器為 `larp-server`)。

##### 🚀 背景啟動指令（行內變數範例）：
```powershell
docker run -d --name larp-server -e PORT=8787 -e HOST_IP=10.0.0.78 -p 0.0.0.0:8787:8787 -v "${PWD}:/workspace" larp-script-archive
```

##### 📂 如果是使用 `.env` 檔案啟動：
```powershell
docker run -d --name larp-server --env-file .env -p 0.0.0.0:8787:8787 -v "${PWD}:/workspace" larp-script-archive
```

##### 📊 背景管理實用指令：
當容器在背景執行時，您可以透過以下三個超好用指令進行控管：

* **看即時日誌（查誰登入、誰註冊）**：
  ```powershell
  docker logs -f larp-server
  ```
  *(按 `Ctrl + C` 可以隨時退出日誌畫面，背景服務依然在跑)*

* **停止背景伺服器**：
  ```powershell
  docker stop larp-server
  ```

* **手動再次啟動（若之前被停止）**：
  ```powershell
  docker start larp-server
  ```

* **徹底刪除背景容器（更換 Port 或重置設定時需執行）**：
  ```powershell
  docker rm -f larp-server
  ```

---

### 🐧 方式二：使用 `serve.sh` 腳本 (Linux / macOS / WSL2 本地環境)

如果您身處 Linux、macOS 或是在 WSL2 原生 Linux 環境中，可以使用內建的 `serve.sh` 腳本：

```bash
# 給予執行權限（僅需執行一次）
chmod +x serve.sh

# 啟動本地伺服器，預設使用 port 8000
./serve.sh

# 或是指定其他 Port 啟動
./serve.sh 8080
```

執行後，腳本會自動偵測並印出您的本機 IP 網址。
同時，任何玩家註冊帳號和 GM 存取狀態均會自動持久化保存在本地目錄的 `kou_xia.db` 中。

---

### 🌐 跨裝置連線設定 (手機/平板連入測試)

當伺服器啟動成功後，同個 Wi-Fi 網路底下的玩家設備即可直接連入：

#### 1. 查詢 Windows 電腦區域網路 IP (ipconfig)
請在 Windows 開啟一個新的 PowerShell 或命令提示字元 (CMD)，輸入以下指令：
```powershell
ipconfig
```
在輸出的一大堆資訊中，尋找名稱為 **「無線區域網路介面卡 Wi-Fi」** (如果是英文版 Windows 請找 `Wireless LAN adapter Wi-Fi`) 的區段，並記下它的 **「IPv4 位址」**：

```text
無線區域網路介面卡 Wi-Fi:

   連線專用 DNS 伺服器尾碼 . . . . . . . :
   連結-本機 IPv6 位址 . . . . . . . . . : fe80::81b7:6bb2:8b85:4d91%18
   IPv4 位址 . . . . . . . . . . . . . . : 10.0.0.78  <--- 就是這個！記下它
   子網路遮罩 . . . . . . . . . . . . . : 255.255.255.0
   預設閘道 . . . . . . . . . . . . . . : 10.0.0.1
```

#### 2. 外部設備（手機/平板）連線網址：
確保手機與您的主機連接在**同一個 Wi-Fi** 中，在手機瀏覽器輸入：
- 📱 **玩家登入端**：`http://<您的電腦IP>:8787/scripts/kou-xia/player/login.html` (例如 `http://10.0.0.78:8787/scripts/kou-xia/player/login.html`)
- 🎲 **主持人 (GM) 端**：`http://<您的電腦IP>:8787/scripts/kou-xia/gm/index.html` (例如 `http://10.0.0.78:8787/scripts/kou-xia/gm/index.html`)

*(備註：若手機連不上，請確保 Windows Defender 防火牆在 Docker 啟動時有勾選允許「私人」與「公用」網路存取。)*

---

### 🌌 方式三：使用 Cloudflare Tunnel 讓外部玩家安全連線 (免開 IP / 免設定防火牆)

如果您不想開啟 Windows 防火牆、或者玩家與您**不在同一個 Wi-Fi 底下**（例如跨縣市線上跑、或使用手機行動網路），最安全且推薦的做法是使用 **Cloudflare Tunnel (cloudflared)**。

這會將您的本機 Port 轉發成一個免費、高安全性的 **HTTPS 加密網址**，任何外部設備都能直接連線，完全不需洩漏您的真實 IP。

#### 1. 安裝 Cloudflare CLI (`cloudflared`)
在 Windows 上，使用 **winget** 安裝是最推薦且快速的方式。請在 PowerShell 輸入：
```powershell
winget install --id Cloudflare.cloudflared
```
安裝完成後，**關閉目前的 PowerShell 並重新打開一個**，測試是否安裝成功：
```powershell
cloudflared --version
```
*如果有正常顯示版本號（例如 `cloudflared version 2026.x.x`），即代表安裝成功！*

#### 2. 啟動臨時 Tunnel 測試
確保您的 Docker 容器已經在 `8787` Port 啟動（正在執行中），接著在 PowerShell 輸入：
```powershell
cloudflared tunnel --url http://localhost:8787
```

##### 實測成功終端機日誌對照：
當啟動成功後，您會在畫面上看到類似以下的日誌（注意其中產生的 `trycloudflare.com` 網址）：

```text
PS C:\WINDOWS\system32> cloudflared tunnel --url http://localhost:8787
INF Requesting new quick Tunnel on trycloudflare.com...
INF +--------------------------------------------------------------------------------------------+
INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
INF |  https://www-cute-found-highland.trycloudflare.com                                         |
INF +--------------------------------------------------------------------------------------------+
INF Settings: map[ha-connections:1 protocol:quic url:http://localhost:8787]
INF Registered tunnel connection connIndex=0 connection=6a37a411-0e64-4149-9ebb-4e8460318bb0 event=0 ip=198.41.192.7 location=khh01 protocol=quic
INF SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.
```

這時候，畫面中產生的 **`https://www-cute-found-highland.trycloudflare.com`**（每次重開會不同）就是您的專屬外部 HTTPS 網址！

您可以直接把這個網址分享給玩家，他們就可以在任何地方（不需 Wi-Fi、用手機 4G/5G 也可以）透過安全 HTTPS 連入您的網頁：
- 📱 **玩家登入端**：`https://www-cute-found-highland.trycloudflare.com/scripts/kou-xia/player/login.html`
- 🎲 **主持人 (GM) 端**：`https://www-cute-found-highland.trycloudflare.com/scripts/kou-xia/gm/index.html`

#### 💡 Tunnel 機制的重要提醒：
1. **本機代管性質**：Cloudflare Tunnel 就像是「在雲端幫你開了一個公開門牌」，但所有的網頁服務、玩家註冊資料庫（`kou_xia.db`）依然安全地存在你本機電腦。
2. **連線生命週期**：當你電腦關機、Docker 關閉、或者在 PowerShell 按 `Ctrl + C` 停掉 `cloudflared`，外面就會立刻斷開連線，安全無虞。
3. **固定專屬網域 (進階)**：透過 `trycloudflare.com` 建立的臨時網址在每次關閉重開後都會改變。若您希望能固定網址（例如 `https://kouxia.yourdomain.com`），您可以申請一個免費的 Cloudflare 帳戶，並綁定您自己的網域，在 Cloudflare 控制台（Zero Trust）設定永久的 Custom Host Tunnel。

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
