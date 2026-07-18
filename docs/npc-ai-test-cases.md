# NPC AI 測試案例集 (docs/npc-ai-test-cases.md)

以下是開發與營運團隊驗收此功能的技術測試案例。

| 案例 ID | 測試情境 | 測試步驟 | 預期結果 | 驗收狀態 |
|---|---|---|---|---|
| **TC-001** | AI 正常對話 | 玩家向張猛傳送問候訊息。 | Polling 後 5 秒內收到符合人設的繁體回覆，不含 HTML 標籤。 | [Pending] |
| **TC-002** | Message ID 唯一性 | 發送訊息並故意快速連續重複點擊「傳送」。 | 資料庫 `ai_tasks` 中針對同一個 `message_id` 只有一筆 pending 記錄，不重複產生任務。 | [Pending] |
| **TC-003** | 雙 Worker 併發競爭 | 啟動兩個 AI Worker 實例，發送多條待處理任務。 | 兩條任務被不同的 `worker_id` 獨佔鎖定並處理，無死鎖，且無重複回覆。 | [Pending] |
| **TC-004** | Process 崩潰恢復 | 當任務正在 `processing` 且 API 剛呼叫完畢但尚未標記 `completed` 時，手動強行重啟服務。 | 重啟後，因事務原子性，DB 未殘留半完成回覆；過期超時（60s）後該任務被置回 `pending` 並重新處理，且有且僅有一次回覆寫入。 | [Pending] |
| **TC-005** | API 異常降級 (Fallback) | 將環境變數中的 API Key 設為無效字串，並發送私訊。 | 任務重試 3 次失敗後，自動寫入預設的 fallback 人設台詞，且任務標記為 `failed`，伺服器不崩潰。 | [Pending] |
| **TC-006** | 跨幕次知識隔離 | 遊戲在 Act 1 狀態，玩家詢問「張猛你被誰殺了？」。 | 即使玩家輸入此引導，AI 亦絕對無法說出 Act 2（劇毒茶靈）的劇情，因為其 context whitelist 中只有 Act 1 內容。 | [Pending] |
| **TC-007** | Staging 與正式 DB 隔離 | 啟動 Staging 容器 (Port 8788)，發送多條測試訊息。 | 測試訊息只寫入 `kou_xia_staging.db`，生產環境 `kou_xia.db` 保持完好。 | [Pending] |
| **TC-008** | 身分偽造防禦 | 使用 Postman 呼叫 `/api/kou-xia/send-private-message`，不帶 `X-Session-Token` 或帶無效 Token。 | 伺服器拒絕請求，並回傳 `401 Unauthorized` 訊息，且不會將垃圾任務塞入 `ai_tasks` 表。 | [Pending] |
