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
- Flask（API + 學生 HTML 頁面）
- Streamlit（老師端網頁）
- HTML／CSS／JS（學生端素材 UI）
- MySQL
- PyMySQL
- bcrypt
- Git / GitHub
- Python venv

期中將**老師與學生拆成兩套登入介面**，共用同一套 Flask API：

| 角色 | 介面 | 進入方式 |
|---|---|---|
| 老師 | Streamlit | `streamlit run streamlit_app.py` |
| 學生 | Flask HTML／CSS／JS | `http://127.0.0.1:5000/student/login` |

## 專案結構

```text
NoteAdventure/
├── app.py                 # Flask Application Factory（API + 學生頁）
├── streamlit_app.py       # 老師端 Streamlit UI（HTTP 呼叫 Flask）
├── main.py                # Console 程式入口
├── db.py
├── config.ini
├── requirements.txt
├── teacher_menu.py
├── student_menu.py
│
├── templates/             # 學生 HTML 頁面
├── static/web/            # 學生前端 CSS／JS
├── material/              # 學生端美術素材
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

網頁開發時：Flask 一定要啟動；老師另開 Streamlit；學生開瀏覽器進 `/student/login`。

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

### 1. Flask（後端，一定要先啟動）

```bash
flask --app app run --port 5000
```

### 2. 老師端（Streamlit，另開終端機）

```bash
streamlit run streamlit_app.py
```

瀏覽器通常開啟 `http://localhost:8501`。

### 3. 學生端（HTML，用瀏覽器開啟）

```text
http://127.0.0.1:5000/student/login
```

登入成功後進入主頁地圖（`/student/home`）。

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
- **老師端 Streamlit**：學生／任務建立與指派／上傳紀錄／商品／兌換
- **學生端 HTML**：登入、主頁地圖、商店、任務欄、寵物、琴房錄音上傳

進行中：

- 期中展示流程演練
- 學生 HTML：背包、設定改密碼

尚未完成：

- 網頁端老師：註冊、任務修改／刪除／啟停、商品修改／刪除／上下架
- 學生 HTML：背包、設定改密碼、教室
- 其他任務條件（`PRACTICE_DAYS`、`CONSECUTIVE_DAYS`、`TOTAL_UPLOADS`、`RETURN_AFTER_GAP`）
- 學生查看自己的購買紀錄
- Dashboard
- 自動化測試

下一步：

- 補齊學生 HTML 剩餘頁面
- 期中 Demo 完整跑通（老師 Streamlit + 學生 HTML）
- （可選）補齊老師端任務／商品進階管理
- Dashboard

## 專題定位

本專案為個人期中展示作品，重點是完成可操作的 MVP 與核心資料流程，而非一次完成完整商業產品。
