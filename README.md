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

## 🤖 AI NPC (張猛) 智能扮演與背景服務

本專案支援使用 **Gemini API** 自動扮演「張猛」NPC。當玩家在私訊系統中與張猛對話時，後端背景 Worker 定期輪詢並非同步呼叫 AI 產生回覆，前端免改代碼即能享有高沉浸感的互動。

### 1. 核心技術特點
*   **非同步持久化佇列 (SQLite Job Queue)**：私訊寫入時，後端原子性地在 `ai_tasks` 表寫入 pending 任務並立即返回成功。背景單一 Worker 執行緒依序處理並呼叫 Gemini，避免前端請求卡死或阻塞 Web 伺服器。
*   **安全認證與防偽造 (X-Session-Token)**：後端完全由 Token 逆向推導真實身分，徹底防止偽造與越權。前端 `auth.js` 自動攔截 Fetch 請求並注入 `X-Session-Token` header。
*   **SQLite 執行緒安全與併發 (WAL Mode)**：資料庫初始化時會自動啟用 WAL 模式並設定 `PRAGMA busy_timeout=5000`（5秒等待），確保背景 Worker 執行緒與 Web 請求執行緒安全併發寫入。
*   **分幕次知識白名單隔離**：根據 `game_state` 解鎖進度（如 `act1_unlocked`, `act2_unlocked`）動態讀取分幕知識庫（如 `act1_knowledge.md`），物理隔離未來劇情，防範 any 劇透與 System Prompt 注入。
*   **過期任務重新申領與 Fallback 降級**：具備 `locked_at` 狀態，當任務因 worker 當機遺失超過 60 秒後，自動重新 pending。API 失敗重試 3 次後，自動寫入一則人設定義的 Fallback 系統提示私訊，任務標為 `failed`。

### 2. 環境變數配置
AI NPC 的金鑰與參數皆透過環境變數管理。請先複製範例設定檔並填入您的 Gemini API Key：
```bash
# 複製範例設定檔 (.env 已在 .gitignore 中，切勿 commit)
cp .env.example .env
```
編輯 `.env` 並填入您的金鑰與自訂配置：
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_THINKING_BUDGET=0
GEMINI_API_TIMEOUT_SECONDS=10
GEMINI_MAX_OUTPUT_TOKENS=300
NPC_AI_ENABLED=true
NPC_AI_POLL_INTERVAL_SECONDS=1
NPC_AI_STALE_TASK_SECONDS=60
NPC_AI_HISTORY_LIMIT=10
```

### 3. 資料庫自動升級 (Auto-Migration)
當啟動新版 `server.py` 時，系統的 `init_db()` 方法會**自動執行增量升級**，無須手動跑 migration 腳本：
*   自動建立 `user_sessions` 與 `ai_tasks` 資料表。
*   自動執行 `PRAGMA journal_mode=WAL` 及設定超時鎖定。
*   此程序完全向下相容，原有玩家的註冊、答題與對話資料將**完整保留**。

### 4. 🔄 舊版升級至新版 AI NPC 步驟
若您的伺服器上正運行舊版容器（如 v1.1.8），請執行以下四步驟完成無損升級與 AI 啟用：

1. **建立並設定環境變數**：
   ```bash
   cp .env.example .env
   nano .env # 填入您的真實 GEMINI_API_KEY
   ```
2. **停止與刪除舊版容器**：
   ```bash
   docker rm -f larp-server
   ```
3. **重建 Docker 映像檔** (因引入了新版 google-genai 依賴)：
   ```bash
   docker build -t larp-script-archive:latest -f Dockerfile .
   ```
4. **啟動新版 AI 容器** (套用安全持久化掛載與環境變數載入)：
   ```bash
   docker run -d \
     --name larp-server \
     --restart always \
     --env-file .env \
     -p 8787:8000 \
     -v "${PWD}/kou_xia.db:/workspace/kou_xia.db" \
     -v "${PWD}/materials:/workspace/materials" \
     larp-script-archive:latest
   ```

---

## 本地端測試與託管 (Local Hosting)

當您在本地修改或新增劇本後，本專案支援以兩種方式在本地端區域網路 (LAN) 啟動一個輕量的 Web 伺服器，使本機電腦、手機、平板皆可連入測試。

---

### 💻 方式一：使用 Docker (生產與 Staging 推薦)

為了避免整個 repository 的 bind-mount 覆蓋容器（Container）內部的程式碼（導致 Rollback 降版時容器內仍執行 Host 上新代碼的問題），**正式部署與測試應優先僅掛載必要持久化資料與設定檔**。

#### 1. 建置 Docker 映像檔
進入專案根目錄，執行以下指令重新 Build 最新 Image：
```bash
docker build -t larp-script-archive:latest -f Dockerfile .
```

#### 2. 一鍵啟動容器 (正式/測試環境)

啟動新版容器前，請先停止並刪除舊有容器：
```bash
# 停止並刪除舊容器
docker rm -f larp-server || true
```

使用以下指令啟動，指定掛載環境變數檔、資料庫及 `materials/`，程式碼本體則直接打包並運行於 Image 內部：
```bash
docker run -d \
  --name larp-server \
  --restart always \
  --env-file .env \
  -p 8787:8000 \
  -v "${PWD}/kou_xia.db:/workspace/kou_xia.db" \
  -v "${PWD}/materials:/workspace/materials" \
  larp-script-archive:latest
```
*(本指令會將本地的資料庫 `kou_xia.db` 及劇本庫掛載進容器中，確保資料庫更新及劇本修改能持久化保存到本機，且不覆蓋容器內運行的 python 程式碼，完美支援 Image 回滾。)*

##### 📊 容器管理實用指令：
*   **查看即時日誌（查誰登入、誰註冊、AI 對話日誌）**：
    ```bash
    docker logs -f larp-server
    ```
*   **停止背景伺服器**：
    ```bash
    docker stop larp-server
    ```
*   **手動再次啟動**：
    ```bash
    docker start larp-server
    ```
*   **徹底刪除背景容器**：
    ```bash
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

##### 🖥️ Windows 平台安裝
使用 **winget** 是最推薦且快速的方式。請在 PowerShell 輸入：
```powershell
winget install --id Cloudflare.cloudflared
```
安裝完成後，**關閉目前的 PowerShell 並重新打開一個**，即可開始使用。

##### 🐧 Ubuntu / Debian 平台安裝 (AMD64 系統)
在 Ubuntu 上，您可以透過官方的 `.deb` 安裝套件快速安裝最新版。請在終端機輸入：
```bash
# 下載最新官方 Debian 軟體包 (AMD64 晶片架構)
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

# 安裝軟體包 (需要 sudo 權限)
sudo dpkg -i cloudflared.deb

# 清除下載的暫存安裝檔
rm cloudflared.deb
```
*(如果是 ARM 晶片架構（例如樹莓派），只需將上述指令中的 `amd64` 改成 `arm64` 即可。)*

##### ✅ 驗證安裝
安裝完成後，請在終端機輸入以下指令測試：
```bash
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
1. **本機代管性質**：Cloudflare Tunnel 就像是「在雲端幫你開了一個公開門牌」，但所有的網頁服務、玩家註冊資料庫（`kou_xia.db`）依然安全地存在您本機電腦。
2. **連線生命週期**：當你電腦關機、Docker 關閉、或者在終端機按 `Ctrl + C` 停掉 `cloudflared`，外面就會立刻斷開連線，安全無虞。
3. **固定專屬網域 (進階)**：透過 `trycloudflare.com` 建立的臨時網址在每次關閉重開後都會改變。若您希望能固定網址（例如 `https://kouxia.yourdomain.com`），您可以申請一個免費的 Cloudflare 帳戶，並綁定您自己的網域，在 Cloudflare 控制台（Zero Trust）設定永久的 Custom Host Tunnel。

#### 3. 如何將 Cloudflare Tunnel 運行於背景？(Background Running)

當您使用 `-d` 將 Docker 容器放在背景執行後，通常也會希望 `cloudflared` 的臨時 Tunnel 也能一併在背景執行，這樣就可以關閉終端機（PowerShell / SSH）且連線不中斷。

您可以使用以下兩種主流方式將 `cloudflared` 跑在背景：

##### 方式 A：使用 Linux `nohup` (極力推薦，最輕量簡便)
在 Linux / WSL2 環境下，您可以使用 `nohup` 搭配 `&` 將程序放到背景執行：
```bash
nohup cloudflared tunnel --url http://localhost:8787 > cloudflared.log 2>&1 &
```
*這會在背景開啟 Tunnel，並將所有的輸出日誌（包含隨機生成的臨時網址）導向到專案根目錄底下的 `cloudflared.log` 檔案中。*

###### 📊 背景 Tunnel 實用管理指令：
- **查看產生的外部安全網址**：
  由於是在背景執行，您需要讀取日誌來取得 Cloudflare 生成的 `trycloudflare.com` 網址：
  ```bash
  cat cloudflared.log | grep -oE "https://[a-zA-Z0-9.-]+\.trycloudflare\.com" | uniq
  ```
- **查看即時連線日誌**：
  ```bash
  tail -f cloudflared.log
  ```
- **關閉/停止背景 Tunnel**：
  ```bash
  pkill cloudflared
  ```

##### 方式 B：使用 `tmux` / `screen` 虛擬終端機
如果您習慣使用 Linux，可以用 `tmux` 或 `screen` 建立一個持久的會話：
```bash
# 建立一個名為 larp-tunnel 的會話
tmux new -s larp-tunnel

# 在裡面執行 cloudflared
cloudflared tunnel --url http://localhost:8787

# 按下 Ctrl + B，然後按 D 鍵 (Detach) 離開會話，Tunnel 會在背景持續運行
```
- **重新回到 Tunnel 畫面**：`tmux a -t larp-tunnel`
- **關閉 Tunnel**：回到畫面中按下 `Ctrl + C` 即可。

#### 4. 實戰：設定固定專屬網域並背景開機自動啟動 (以 `larp.tz-c.net` 為例)

如果您已經擁有自己的網域（例如 `larp.tz-c.net`），可以透過 Cloudflare 建立 **Named Tunnel**（具名隧道），將其設定為 Linux 系統服務，達到**開機自動在背景啟動**且**網址永久固定**的完美效果！

##### ① 登入並建立具名 Tunnel
首先，在伺服器上登入您的 Cloudflare 帳號：
```bash
cloudflared tunnel login
```
*這會提供一個驗證網址，請在瀏覽器打開並授權您的網域。*

接著，建立一個名為 `larp-script` 的 Tunnel：
```bash
cloudflared tunnel create larp-script
```
*建立成功後，系統會為您分配一個專屬的 Tunnel UUID（例如 `1731525f-b29e-47f8-bd12-85a05eb3c41c`）以及認證金鑰。*

##### ② 建立具名 Tunnel 設定檔
在 `/home/fiducia/.cloudflared/` 目錄下建立設定檔：
```bash
nano ~/.cloudflared/config.yml
```
寫入以下設定（請將 UUID 與檔案路徑替換成您的實際值）：
```yaml
tunnel: 1731525f-b29e-47f8-bd12-85a05eb3c41c
credentials-file: /home/fiducia/.cloudflared/1731525f-b29e-47f8-bd12-85a05eb3c41c.json

ingress:
  - hostname: larp.tz-c.net
    service: http://localhost:8787

  - service: http_status:404
```

##### ③ 綁定 DNS CNAME 記錄
將您的網域與 Tunnel 進行綁定（這會自動在 Cloudflare DNS 加上一筆 CNAME 記錄）：
```bash
cloudflared tunnel route dns larp-script larp.tz-c.net
```
*成功後，`larp.tz-c.net` 將會永久安全地轉發至您本機的 `8787` 服務！*

##### ④ 測試設定與手動啟動
測試您的 Ingress 規則是否正確：
```bash
cloudflared tunnel ingress validate
```
進行手動測試運行：
```bash
cloudflared tunnel run larp-script
```
*如果看到 `Registered tunnel connection`，此時透過任何設備瀏覽 `https://larp.tz-c.net` 即可成功連入！*

##### ⑤ 安裝為系統服務（開機自動於背景啟動）
手動測試成功後，按 `Ctrl + C` 退出。接著，將其安裝為 Linux 系統服務，使其完全常駐在背景：
```bash
# 安裝為系統服務 (明確指定設定檔路徑以避免權限問題)
sudo cloudflared --config /home/fiducia/.cloudflared/config.yml service install

# 啟動並設定開機自動載入
sudo systemctl enable --now cloudflared
```

##### 🛠️ 實用背景服務維護指令：
- **查看服務即時狀態**：`sudo systemctl status cloudflared`
- **查看即時運行日誌**：`sudo journalctl -u cloudflared -f`
- **重啟服務**：`sudo systemctl restart cloudflared`

> ⚠️ **安全警告：** 請務必確保 `~/.cloudflared/cert.pem` 以及您的私密 JSON 金鑰檔案（如 `1731525f-b29e-47f8-bd12-85a05eb3c41c.json`）**不被 commit 到 Git 倉庫中**，它們已自動包含在 `.gitignore` 中。

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
