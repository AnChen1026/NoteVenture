# NoteAdventure

音樂練習 RPG 管理系統。

## 專案介紹

NoteAdventure 是一套提供一對一音樂老師使用的學生練習管理系統。

老師可以建立學生帳號、設計與指派任務；學生透過上傳練習錄音累積任務進度、XP 與金幣，並讓寵物成長。

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

## 技術堆疊

- Python 3.12
- Flask
- Streamlit
- MySQL
- PyMySQL
- bcrypt
- Git / GitHub
- Python venv

## 專案結構

```text
NoteAdventure/
├── app.py                 # Flask Application Factory 入口
├── streamlit_app.py       # Streamlit 網頁 UI（HTTP 呼叫 Flask）
├── main.py                # Console 程式入口
├── db.py
├── config.ini
├── requirements.txt
├── teacher_menu.py
├── student_menu.py
│
├── api/                   # Flask Blueprint（路由與 session）
│   ├── auth.py
│   ├── students.py
│   ├── quests.py
│   ├── practice.py
│   ├── shop.py
│   ├── pet.py
│   ├── health.py
│   └── guards.py
│
├── docs/
│   ├── NoteAdventure_MVP.md
│   ├── NoteAdventure_PROJECT_CONTEXT.md
│   ├── DATABASE_SCHEMA.md
│   └── README.md
│
├── services/
├── utils/
├── sql/
├── uploads/
│
├── .streamlit/
│   └── config.toml
│
└── .cursor/
    └── rules/
```

網頁開發時需同時啟動 Flask（預設 `:5000`）與 Streamlit。

## 安裝方式

### 1. Clone

```bash
git clone <repository-url>
cd NoteAdventure
```

### 2. 建立虛擬環境

Windows：

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安裝套件

```bash
pip install -r requirements.txt
```

### 4. 建立資料庫

執行：

```text
sql/music_rpg_schema_v2.sql
```

### 5. 建立 `config.ini`

```ini
[DB]
host=localhost
user=root
password=your_password
port=3306
database=music_rpg_v2
```

`config.ini` 不應上傳 GitHub。

## 執行方式

Console：

```bash
python main.py
```

Flask API（先啟動，預設 port 5000）：

```bash
flask --app app run --port 5000
```

Streamlit（另開一個終端機）：

```bash
streamlit run streamlit_app.py
```

## MVP 功能

下列為 MVP 目標功能。實際完成範圍請見「目前進度」（Console 與網頁覆蓋範圍不完全相同）。

- 老師註冊與登入
- 建立與查看學生
- 重設學生密碼
- 學生首次登入強制改密碼
- 任務 CRUD
- 任務啟用／停用
- 任務指派
- 學生查看任務
- 練習錄音上傳
- 老師查看學生上傳紀錄
- 任務進度
- XP 與金幣獎勵
- 寵物階段顯示
- 商品建立與查看
- 學生購買商品
- 實體商品兌換

## 文件

- [MVP](./NoteAdventure_MVP.md)
- [Project Context](./NoteAdventure_PROJECT_CONTEXT.md)
- [Database Schema](./DATABASE_SCHEMA.md)

## 開發原則

1. 每次只完成一個小功能。
2. 完成功能後建立 Git commit。
3. 修改資料表時同步更新 Schema。
4. 不任意重構已完成且正常運作的程式。
5. AI Agent 開發前先閱讀 `NoteAdventure_PROJECT_CONTEXT.md`。
6. 核心流程需自行測試與理解。

## 目前進度

已完成：

- MySQL Schema、Git 版本控制
- Console：老師註冊／登入、學生建立與查看、密碼重設、首次登入改密碼
- Console：任務建立／查看／修改／刪除、啟用／停用、指派與期限
- Console：練習上傳、老師查看上傳、進度（`PRACTICE_COUNT`／`DISTINCT_SONGS`）、獎勵、寵物、商店與兌換
- Flask 核心 API（health、登入／登出、改密碼、學生、任務建立／指派、練習上傳、商店、寵物）
- Streamlit 串接 Flask（老師：學生／任務建立與指派／上傳紀錄／商品／兌換；學生：任務／上傳／商店／寵物／強制改密碼）

進行中：

- 期中展示流程演練

尚未完成：

- 網頁端：老師註冊、任務修改／刪除／啟停、商品修改／刪除／上下架
- 其他任務條件（`PRACTICE_DAYS`、`CONSECUTIVE_DAYS`、`TOTAL_UPLOADS`、`RETURN_AFTER_GAP`）
- 學生查看自己的購買紀錄
- Dashboard
- 自動化測試

下一步：

- 期中 Demo 完整跑通
- （可選）補齊網頁端任務／商品進階管理
- Dashboard

## 專題定位

本專案為個人期中展示作品，重點是完成可操作的 MVP 與核心資料流程，而非一次完成完整商業產品。
