# NPC AI 退版與故障恢復指南 (docs/npc-ai-rollback.md)

本指南用於說明在新版 AI NPC 系統發生故障、卡死或系統不相容時，如何安全、無損地回滾（Rollback）到上一個穩定版本。

## 1. 回退原則 (Data-First Preservation)
*   **不遺失新私訊**：正式環境的 `kou_xia.db` 包含了新系統上線後玩家產生的真實對話。**絕對不能無條件直接覆蓋/還原舊資料庫備份**。
*   **相容性設計**：本架構中，`ai_tasks` 與 `user_sessions` 皆為純增量、解耦的擴充資料表。舊版 `server.py`（如 v1.1.8）完全不認識這兩張表，直接退版執行舊版程式碼時，系統會無視這兩張表，並保持對 `private_messages` 的正常讀寫。
*   **警告損失**：只有在資料庫發生嚴重的 SQLite schema 損毀或資料庫檔案損毀時，才允許還原 `.db.bak` 備份。

## 2. 正常回滾步驟 (Code-Only Rollback)
當 AI 行為異常或服務當機，但資料庫完好時：

```bash
# 1. 停止並刪除新版 AI 容器
docker stop larp-server
docker rm larp-server

# 2. 直接啟動舊版穩定映像檔 (例如 v1.1.8)
# 注意：舊版會使用 host 上的相同 db 檔案，玩家在 AI 期間發送的所有私訊仍會保留
docker run -d \
  --name larp-server \
  --restart always \
  -p 8787:8000 \
  -v "$PWD/kou_xia.db:/workspace/kou_xia.db" \
  -v "$PWD/materials:/workspace/materials" \
  larp-script-archive:v1.1.8
```

## 3. 災難還原步驟 (DB Restoration)
若 SQLite 資料庫發生物理損毀，或資料寫入出現嚴重錯亂：

1.  **停止服務**：`docker stop larp-server`。
2.  **存檔損毀資料**：`mv kou_xia.db kou_xia_corrupted.db` (保留以便後續嘗試手動救援數據)。
3.  **還原備份**：`cp kou_xia.db.bak kou_xia.db`。
4.  **警告**：此操作將損失**自備份時間點起至當下**的所有玩家答題、註冊、與私訊資料！
5.  **啟動服務**：`docker start larp-server`。
