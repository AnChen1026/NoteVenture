# NoteAdventure

音樂練習 RPG 管理系統。

## 專案介紹

NoteAdventure 是一套給一對一音樂老師使用的學生練習管理系統。

老師建立學生與任務；學生上傳練習錄音，累積任務進度、XP 與金幣，並讓寵物成長。

## 核心流程

```text
老師建立學生
→ 建立並指派任務
→ 學生登入
→ 上傳練習錄音
→ 更新任務進度
→ 完成任務
→ 獲得 XP 與金幣
→ 寵物成長
```

## 正式兩條線

兩者共用同一套 Flask API：

| 角色 | 介面 | 進入方式 |
|------|------|----------|
| 老師 | Streamlit（僅老師） | `streamlit run streamlit_app.py` |
| 學生 | Flask HTML 一頁版 | `/student/app` |

分層概要：`前端` → `api/` → `services/` → MySQL。  
開啟步驟見 [啟動說明](./啟動說明.md)。

## 技術堆疊

- Python 3.12
- Flask（API + 學生 HTML）
- Streamlit（老師端）
- HTML／CSS／JS
- MySQL、PyMySQL、bcrypt
- Git／GitHub、venv

## 專案結構（精簡）

```text
NoteAdventure/
├── app.py                 # Flask（API + 學生一頁版）
├── streamlit_app.py       # 老師管理後台
├── templates/             # 學生 HTML（SPA 殼 + 內頁）
├── static/web/            # 學生 CSS／JS
├── material/              # 學生正式素材
├── api/                   # HTTP／session
├── services/              # 商業邏輯
├── sql/                   # Schema
├── archive/               # 舊版／備援（非正式）
└── docs/                  # 本目錄文件
```

## 文件（僅此五份）

| 文件 | 說明 |
|------|------|
| [啟動說明](./啟動說明.md) | 本機開啟＋雲端 Flask 開啟 |
| [MVP](./NoteAdventure_MVP.md) | 最小可行性產品定義 |
| [專案上下文](./NoteAdventure_PROJECT_CONTEXT.md) | 給開發／AI 的專案規則與現況 |
| [資料庫 Schema](./DATABASE_SCHEMA.md) | 資料表說明（以 SQL 為準） |
| [README](./README.md) | 本頁：總覽與索引 |

舊版網頁結構、期中串接地圖、部署草稿等已移至 `archive/docs/`。

## 開發原則

1. 每次只完成一個小功能。
2. 完成功能後建立 Git commit。
3. 修改資料表時同步更新 Schema；不得捏造欄位。
4. 不任意重構已完成且正常運作的程式。
5. AI／開發前先讀 `NoteAdventure_PROJECT_CONTEXT.md`。
6. 不得提交 `config.ini`、密碼、Token。

## 目前進度（摘要）

已完成：

- MySQL Schema、Flask API、`services/` 商業邏輯
- 老師 Streamlit：註冊／登入、學生、任務、上傳試聽、商店／兌換
- 學生一頁版 `/student/app`：登入、主頁、琴房、任務、寵物、商店、背包、教室、設定
- 舊 Console／Streamlit 學生備援整理至 `archive/`

尚未完成（舉例）：

- 老師網頁端：任務修改／刪除／啟停、商品進階管理
- 部分任務條件類型
- 自動化測試、音檔雲端持久化

## 專題定位

個人專題／展示作品，重點是可操作的 MVP 與核心資料流程。
