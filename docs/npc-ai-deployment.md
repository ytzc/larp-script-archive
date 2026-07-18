# NPC AI 部署指南 (docs/npc-ai-deployment.md)

## 1. 環境變數配置
在專案根目錄下建立一個名為 **`.env`** 的環境變數設定檔（該檔案已被 `gitignore` 排除，切勿 commit 提交）：

```ini
# Gemini API Key (必要)
GEMINI_API_KEY=AIzaSy...

# 指定的模型 ID (正式推薦：gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash

# API 參數
GEMINI_TEMPERATURE=0.7
GEMINI_THINKING_BUDGET=0
GEMINI_API_TIMEOUT_SECONDS=10
GEMINI_MAX_OUTPUT_TOKENS=300

# NPC 功能與 Worker 開關
NPC_AI_ENABLED=true
NPC_AI_WORKER_COUNT=1
NPC_AI_POLL_INTERVAL_SECONDS=1
NPC_AI_STALE_TASK_SECONDS=60
```

## 2. 依賴管理 (requirements.txt)
本專案的依賴版本已鎖定，由 `requirements.txt` 管理：
```text
google-genai>=1.0.0,<3.0.0
python-dotenv>=1.0.1,<2.0.0
```

## 3. Docker 部署規範

為了避免宿主機（Host）上的程式碼在 Rollback 時覆蓋 Image 內的舊版程式碼，我們**不再掛載整個目錄**，改為僅掛載必要持久化資料：

### 正式啟動命令
```bash
docker run -d \
  --name larp-server \
  --restart always \
  --env-file .env \
  -p 8787:8000 \
  -v "$PWD/kou_xia.db:/workspace/kou_xia.db" \
  -v "$PWD/materials:/workspace/materials" \
  larp-script-archive:latest
```

## 4. Staging 測試部署
在部署至正式環境前，必須先啟動 staging 獨立容器進行完整測試：

```bash
# 1. 備份正式 DB 做為 staging DB 副本
cp kou_xia.db kou_xia_staging.db

# 2. 建立 Staging 配置
cp .env .env.staging

# 3. 建置 Staging Image
docker build -t larp-script-archive:staging -f Dockerfile .

# 4. 啟動隔離 Staging 容器 (改為 Port 8788 且掛載 staging DB)
docker run -d \
  --name larp-staging \
  --env-file .env.staging \
  -p 8788:8000 \
  -v "$PWD/kou_xia_staging.db:/workspace/kou_xia.db" \
  -v "$PWD/materials:/workspace/materials" \
  larp-script-archive:staging

# 5. 連線測試 Staging 入口: http://<IP>:8788/scripts/kou-xia/player/login.html
```
