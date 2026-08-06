# NoteAdventure｜PROJECT_CONTEXT

> 本文件提供 Cursor Agent 與其他 AI 工具專案上下文。開發前必須先閱讀本文件。
> 

## 1. 專案目的

> NoteAdventure 是一套提供一對一音樂老師管理學生練習的 RPG 遊戲化系統；老師建立學生與任務，學生透過練習錄音累積任務進度、XP 與金幣，並讓寵物成長。
> 

## 2. 技術堆疊

### 必須使用

- Python 3.12
- Flask
- Streamlit
- MySQL
- PyMySQL
- bcrypt
- Git / GitHub
- Python venv

### 未經要求不得改用

- Django
- FastAPI
- SQLAlchemy
- SQLite
- React
- Vue
- Node.js

## 3. 專案結構

```
NoteAdventure/
├── app.py
├── main.py
├── db.py
├── config.ini
├── requirements.txt
├── teacher_menu.py
├── student_menu.py
│
├── docs/
│   ├── NoteAdventure_MVP.md
│   ├── NoteAdventure_PROJECT_CONTEXT.md
│   ├── DATABASE_SCHEMA.md
│   └── README.md
│
├── services/
│   ├── dashboard_service.py
│   ├── pet_service.py
│   ├── practice_service.py
│   ├── quest_service.py
│   ├── reward_service.py
│   ├── shop_service.py
│   ├── student_service.py
│   └── teacher_service.py
│
├── utils/
│   ├── password_utils.py
│   └── username_utils.py
│
├── sql/
│   └── music_rpg_schema_v2.sql
│
├── uploads/
│   └── audio/
│
└── .cursor/
    └── rules/

```

## 4. 分層責任

- `main.py`：Console 程式入口，負責登入選單與角色流程。
- `teacher_menu.py`：老師 Console 選單與輸入輸出流程。
- `student_menu.py`：學生 Console 選單與輸入輸出流程。
- `app.py`：預留作為未來 Streamlit 網頁入口，目前尚未完成。
- `services/`：負責商業邏輯與資料庫操作。
- `db.py`：負責資料庫連線、查詢、執行 SQL、commit、rollback 與關閉連線。
- `utils/`：負責密碼處理、學生帳號與臨時密碼產生等共用工具。

選單檔案只負責接收輸入、顯示結果與呼叫 Service，不應直接放大量 SQL。

## 5. 資料庫

資料庫名稱：

```
music_rpg_v2
```

核心資料表：

```
teacher
student
pet_stage
pet
practice_upload
quest_list
student_quest
shop_item
purchase_record
xp_source
coin_transaction
```

欄位以 `DATABASE_SCHEMA.md` 與 `sql/music_rpg_schema_v2.sql` 為準，不得捏造欄位。

## 6. 核心設計決策

1. 老師使用 email 登入。
2. 學生帳號由系統隨機產生。
3. 密碼使用 bcrypt。
4. 每位學生只屬於一位老師。
5. 每位學生只有一隻寵物。
6. 任務模板綁定老師。
7. 學生與任務透過 `student_quest` 關聯。
8. 任務期限自指派時間起算，每日任務一天、每週任務七天，隱藏任務無期限。
9. 任務歷史不得歸零或覆蓋。
10. 重新指派時新增一筆 `student_quest`。
11. 資料庫存英文代碼，介面顯示中文。
12. 隱藏任務完成前不顯示。
13. 錄音檔只存路徑，不存 MySQL BLOB。
14. XP 與金幣同時保存總額與異動紀錄。
15. 任務完成不得重複發獎。
16. 多步驟獎勵更新應使用 transaction。

## 7. 任務代碼

`quest_type`：

```
DAILY
WEEKLY
HIDDEN
```

`condition_type`：

```
PRACTICE_COUNT
PRACTICE_DAYS
DISTINCT_SONGS
CONSECUTIVE_DAYS
TOTAL_UPLOADS
RETURN_AFTER_GAP
```

MVP 第一版只實作：

```
PRACTICE_COUNT
DISTINCT_SONGS
```

## 8. 已完成進度

### 已完成並測試

- MySQL Schema
- `SqlUtils`
- `query_one()`
- `query_all()`
- `execute()`
- `execute_transaction()`
- bcrypt hash／verify
- 老師註冊與登入
- 老師選單
- 建立與查看學生
- 重設學生密碼
- 修改老師密碼
- 學生首次登入改密碼
- 任務查看、建立、修改、刪除
- 任務啟用／停用
- 任務指派
- 任務期限
- `period_key`
- 學生查看被指派任務
- 練習錄音上傳
- 老師查看學生上傳紀錄
- 任務進度計算（`PRACTICE_COUNT`、`DISTINCT_SONGS`）
- 任務完成與 XP／金幣發放（transaction）
- 防止重複發獎
- 寵物階段更新與查看
- 老師建立與查看商品
- 學生查看商店與購買商品
- 老師處理實體商品兌換

### 進行中

- 期中展示流程演練

### 尚未完成

- Flask API
- Streamlit 串 Flask API
- 其他任務條件判斷（`PRACTICE_DAYS`、`CONSECUTIVE_DAYS`、`TOTAL_UPLOADS`、`RETURN_AFTER_GAP`）
- 商品修改、刪除與上下架
- 學生查看自己的購買紀錄
- Dashboard
- 自動化測試

## 9. 核心流程

```
老師登入
→ 建立學生
→ 建立任務
→ 指派任務
→ 學生登入
→ 查看任務
→ 上傳練習
→ 更新任務進度
→ 任務完成
→ 發放 XP 與金幣
→ 更新寵物階段
```

## 10. 開發規則

1. 每次只完成一個小功能。
2. 不修改無關檔案。
3. 不重寫已正常運作的功能。
4. 修改前先讀本文件、`NoteAdventure_MVP.md`、`DATABASE_SCHEMA.md`。
5. 修改資料表時同步更新 SQL 與文件。
6. SQL 值使用 `%s` 綁定。
7. 動態欄位只能來自固定白名單。
8. 更新與刪除任務使用 `quest_id`。
9. 老師查詢學生、任務、商品時必須限制 `teacher_id`。
10. 學生只能查看自己的資料。
11. 密碼不得明文儲存。
12. 任務完成不得重複發獎。
13. 商品購買、扣款與紀錄必須放在同一個 transaction。
14. 未經要求不要大規模重構。
15. 完成後需列出修改檔案、函式、SQL、測試方式與 Git commit message。
16. 程式碼精簡不複雜，與原有程式碼風格一致

## 11. Agent 工作流程

```
1. 讀取 NoteAdventure_PROJECT_CONTEXT.md
2. 讀取 NoteAdventure_MVP.md
3. 讀取 DATABASE_SCHEMA.md
4. 檢查現有程式
5. 只完成本次指定功能
6. 不修改無關程式
7. 說明變更與測試方式
8. 提供 Git commit message
```

## 12. 下一步

```
完成期中展示流程演練
```

完成條件：

- 依 `NoteAdventure_MVP.md` 5.4 的展示腳本從老師註冊跑到學生購買
- 每個步驟都有中文提示，查無資料時不報錯
- 準備展示用的測試老師、學生、任務、商品與音檔
- 記錄流程中發現的問題與待修項目