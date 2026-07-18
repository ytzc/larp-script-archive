# NPC AI 架構設計文件 (docs/npc-ai-architecture.md)

## 1. 系統概覽
本設計引入了一個非阻塞、高可靠、基於 SQLite 任務佇列的 AI NPC (張猛) 扮演系統，整合於《寇俠》劇本殺網站。

### 核心架構元件
```text
[ 瀏覽器 (Polling 5s) ]
        │ ▲
        │ │ (私訊讀取)
        ▼ │
┌─────────────────────────────────────────────────────────┐
│ server.py (ThreadingHTTPServer)                         │
│   ├─ 處理 POST /send-private-message                     │
│   │   ├─ 驗證 X-Session-Token                           │
│   │   ├─ 寫入私訊表                                      │
│   │   └─ 原子性寫入任務表 (ai_tasks)                     │
│   │                                                     │
│   └─ Background Worker Thread (tools/npc_ai.py)         │
│       └─ 輪詢 ai_tasks, 呼叫 Gemini, 原子性寫入回覆並完成      │
└───────────┬─────────────────────────────────────────────┘
            ▼
       [ SQLite ]
 (WAL 模式, 5s busy_timeout)
```

## 2. 資料庫 Schema
新增 `ai_tasks` 任務表，並新增 `user_sessions` 表用來進行後端安全身分驗證。

### ai_tasks 表
- `id` INTEGER (PK, 遞增)
- `message_id` INTEGER (UNIQUE, FK to `private_messages(id)`)
- `status` TEXT (pending, processing, completed, failed)
- `attempts` INTEGER (預設 0)
- `error` TEXT
- `locked_at` TEXT (鎖定時間戳)
- `worker_id` TEXT (處理此任務的 Worker 標識)
- `reply_message_id` INTEGER (FK to `private_messages(id)`)
- `created_at` TEXT
- `processed_at` TEXT

### user_sessions 表
- `token` TEXT (PK, 16進制隨機 Token)
- `character_id` TEXT NOT NULL
- `created_at` TEXT NOT NULL

## 3. SQLite 執行緒安全設計
- 啟用 SQLite WAL 模式（`PRAGMA journal_mode=WAL`）以提升高併發讀寫效能。
- 設定 `PRAGMA busy_timeout=5000` 讓衝突的連線等待 5 秒而非立即拋出 `locked` 異常。
- 所有背景 Worker 與 Web Thread 連線**完全獨立**，不共用 Connection 或 Cursor，且在發生異常時執行 rollback。

## 4. 故障轉移與可靠性 (Crash Recovery)
- **防重複回覆**：使用 `message_id UNIQUE` 索引與原子 `UPDATE` 鎖定機制（`rowcount == 1`），避免多 Worker 搶占或重複呼叫。
- **事務一致性**：寫入張猛 NPC 的私訊回覆與將任務標記為 `completed` 包裝在同一個 SQLite 交易（Transaction）中。如果發生 Process 崩潰，該交易完全不生效，絕無「寫入回覆但任務未標完成」的狀態。
- **超時恢復**：凡是處於 `processing` 狀態且鎖定時間超過 `NPC_AI_STALE_TASK_SECONDS` 的任務，將被其他 Worker 或重啟後的 Worker 自動重置並重新申領，確保沒有死任務。
- **Fallback 降級**：重試 3 次失敗後，自動寫入一則人設定義的 Fallback 系統提示私訊，任務標為 `failed`。
