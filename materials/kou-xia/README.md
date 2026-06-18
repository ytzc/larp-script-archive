# 《寇俠》— 素材資料夾

這個資料夾存放《寇俠》的**原始劇本資料與外部素材索引**。

## 資料夾結構

| 路徑 | 說明 |
|------|------|
| `source/` | **正式原始劇本來源（Source of Truth）**，繁體化整理稿，納入 Git 版控 |
| `external-links.md` | 外部素材來源連結（iCloud、百度網盤等） |
| `inventory.md` | 素材清單與整理進度追蹤 |
| `notes.md` | 整理筆記、待辦、public / private 區分 |

## source/ 說明

`source/` 存放全部 9 個角色的劇本文字，為**本 repo 最高優先的原始資料**。

- 來源：iPhone 拍攝 OCR → 人工校對 → 簡體轉繁體整理
- 檔案命名採角色拼音 slug（如 `yan-shi.md`、`diao-wu-er.md`）
- 每個檔案開頭含 YAML Front Matter（角色 metadata）
- 所有劇本修訂、繁體修正、OCR 勘誤應直接在此資料夾維護
- `docs/` 下的網頁版本均以此為底本

### Front Matter 欄位說明

```yaml
---
name: "角色名"            # 顯示在卡片上的名稱
slug: "slug-name"         # 對應 HTML 檔名（如 yan-shi）
type: "player"            # player 或 npc
identity_label: "真名"    # 真名 / 化名 / 代號 / 幼名
identity: "身份文字"       # 實際身份
extra_identity: "..."     # 選填，如「幼名：丁典」
age: "22歲"               # 年齡
cover_quote: "封面詩句"    # 角色卡片上的封面句
status: "已以 source 補強" # badge 顯示文字
---
```

### 修改角色資訊

修改角色封面句、身份、年齡時，**只改 Front Matter**，然後執行 build script：

```bash
python3 tools/build-player-script-index.py
```

這會自動更新 `docs/scripts/kou-xia/player/scripts/index.html`。

> **不要手動修改** `index.html` 中的 `<div class="char-card">` 卡片內容。

## 外部素材

| 來源 | 類型 | 說明 |
|------|------|------|
| iCloud Drive | 個人素材資料夾 | 原始劇本 PDF（已刪除本地副本，2026-06-17） |
| 百度網盤 | 官方開本資料 | 開本音樂、主持說明 |

詳細連結請見 [external-links.md](external-links.md)。

## ⚠️ 不 commit 的類型

以下類型仍然不 commit 至 GitHub：

- 原始 PDF（角色劇本、GM手冊）
- 音樂 / BGM / 音效
- 圖片 / 插圖（除非確認授權）
- ZIP 壓縮檔
