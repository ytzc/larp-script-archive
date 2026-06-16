# LARP Script Archive

A personal archive for LARP scripts, story settings, character profiles, and session notes.

## 目錄說明

```
larp-script-archive/
├── docs/                        # GitHub Pages 部署根目錄
│   ├── index.html               # 網站首頁（劇本總覽）
│   ├── assets/css/style.css     # 共用樣式
│   └── scripts/                 # 所有劇本資料夾
│       └── kou-xia/             # 劇本：寇俠
│           ├── public/          # ✅ 可公開資料（世界觀、人物簡介等）
│           ├── characters/      # ⚠️  角色劇本（含 spoiler，請注意）
│           ├── organizations/   # ⚠️  組織資料（含 spoiler，請注意）
│           ├── gm/              # 🔒 GM / Host 專用（不建議公開）
│           └── sessions/        # 📝 場次記錄
├── .github/workflows/           # GitHub Actions
└── .gitignore
```

## 新增劇本

每一本新劇本放在 `docs/scripts/<script-slug>/` 底下，複製 `kou-xia/` 的結構後填入內容即可。

範例：
```bash
cp -r docs/scripts/kou-xia docs/scripts/new-script-name
```

## 部署

打上 tag 即自動觸發 GitHub Pages 部署：

```bash
git tag v0.1.0
git push origin main --tags
```

Pages 網址：`https://<username>.github.io/larp-script-archive/`

## ⚠️ 安全性提醒

> **GitHub Pages 是完全公開的靜態網站。**
>
> - `gm/` 資料夾包含主持人筆記、劇情 spoiler、幕後設定，**不建議部署到公開 Pages**。
> - `characters/` 內的個人角色劇本可能含有其他玩家不應知道的資訊，請確認後再公開。
> - 若有機密資料，請放在 private repo，或使用 `.gitignore` 排除後僅本地保存。

## 授權

本 repo 為個人私用資料整理，劇本內容版權歸原作者所有。
