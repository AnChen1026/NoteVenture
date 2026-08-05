# Melody Quest

音樂練習 RPG 管理系統。

## 專案介紹

Melody Quest 是一套提供一對一音樂老師使用的學生練習管理系統。

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
NoteVenture/
├── app.py
├── main.py
├── db.py
├── config.ini
├── requirements.txt
├── MVP.md
├── PROJECT_CONTEXT.md
├── DATABASE_SCHEMA.md
├── services/
├── utils/
├── sql/
├── uploads/
├── teacher_menu.py
└── student_menu.py
```

## 安裝方式

### 1. Clone

```bash
git clone <repository-url>
cd NoteVenture
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

Streamlit：

```bash
streamlit run app.py
```

Flask API：

```bash
flask run
```

## MVP 功能

- 老師註冊與登入
- 建立與查看學生
- 重設學生密碼
- 任務 CRUD
- 任務啟用／停用
- 任務指派
- 學生查看任務
- 練習錄音上傳
- 任務進度
- XP 與金幣獎勵
- 寵物階段顯示

## 文件

- [MVP](./MVP.md)
- [Project Context](./PROJECT_CONTEXT.md)
- [Database Schema](./DATABASE_SCHEMA.md)

## 開發原則

1. 每次只完成一個小功能。
2. 完成功能後建立 Git commit。
3. 修改資料表時同步更新 Schema。
4. 不任意重構已完成且正常運作的程式。
5. AI Agent 開發前先閱讀 `PROJECT_CONTEXT.md`。
6. 核心流程需自行測試與理解。

## 目前進度

已完成：

- 老師註冊與登入
- 建立與查看學生
- 密碼重設
- 任務建立、查看、修改、刪除
- 任務啟用／停用
- MySQL Schema
- Git 版本控制

進行中：

- 任務指派
- 學生任務查詢

下一步：

- Flask API
- 練習上傳
- 任務進度
- XP、金幣與寵物
- Streamlit 串接

## 專題定位

本專案為個人期中展示作品，重點是完成可操作的 MVP 與核心資料流程，而非一次完成完整商業產品。
