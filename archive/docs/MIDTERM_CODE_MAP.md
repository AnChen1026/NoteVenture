# 期中報告｜程式串接地圖（誰連誰）
#
# 目的：報告被問「前端怎麼連後端？資料庫誰在動？」時，照這張圖回答。
# 網頁入口細節另見 WEB_STRUCTURE.md；資料表見 DATABASE_SCHEMA.md。

## 1. 一句話架構

```text
老師 Streamlit  ─┐
                 ├──HTTP──►  Flask(app.py) ──► api/*.py ──► services/* ──► MySQL
學生 HTML／JS  ─┘              │
                               ├── 回傳 JSON（/api/...）
                               └── 回傳 HTML（/student/...）＋素材（/assets/material/...）
```

重點：**老師與學生前端不同，但 API 同一套。** `services/` 是真正改資料庫的地方。

---

## 2. 分層責任（口試常用）

| 層 | 資料夾／檔案 | 做什麼 | 不做什麼 |
|----|--------------|--------|----------|
| 老師 UI | `streamlit_app.py` | 表單、按鈕、顯示表格；用 `requests` 打 API | 不直接寫 SQL |
| 學生 UI | `templates/` + `static/web/` | 畫面與 `fetch` 打 API | 不直接寫 SQL |
| 路由／HTTP | `app.py` + `api/` | 路徑、參數、session 登入檢查、回傳 JSON／HTML | 少放複雜商業規則 |
| 商業邏輯 | `services/` | 建立學生、上傳、任務進度、發獎、商店… | 不管畫面怎麼畫 |
| 資料庫工具 | `db.py` | 連線、query、execute、transaction | 不管業務規則 |
| 密碼工具 | `utils/` | bcrypt hash／驗證、產生帳號 | — |

登入守衛：`api/guards.py` 的 `get_login_teacher()`／`get_login_student()`  
→ 讀 Flask `session`，確認角色後再允許打受保護 API。

---

## 3. Flask 檔案 ↔ 功能 ↔ Service

| API 檔案 | 主要路徑（舉例） | 主要呼叫的 service | 誰在用 |
|----------|------------------|--------------------|--------|
| `api/health.py` | `GET /api/health` | （無） | 部署自測 |
| `api/auth.py` | 老師／學生登入、登出、改密碼、註冊、`/api/me` | `teacher_service`、`student_service` | 兩邊 |
| `api/students.py` | 學生列表、建立、重設密碼 | `student_service` | 老師 Streamlit |
| `api/quests.py` | 任務列表、建立、指派、學生任務 | `quest_service` | 兩邊 |
| `api/practice.py` | 上傳練習、老師看上傳、聽音檔 | `practice_service` → 再叫 `quest_service`、`reward_service` | 兩邊 |
| `api/shop.py` | 商品、購買、背包、待兌換、標記兌換 | `shop_service` | 兩邊 |
| `api/pet.py` | 寵物狀態 | `pet_service` | 學生 HTML |
| `api/dashboard.py` | 老師／學生首頁摘要 | `dashboard_service` | 兩邊 |
| `api/class_board.py` | 兩廳院節目 | `ntch_service` | 學生教室頁 |

---

## 4. 核心示範流程（最常被問）

學生在琴房上傳錄音後發生什麼？

```text
學生 JS（student_practice.js）
  POST /api/students/<id>/practice-uploads   （含音檔）
    → api/practice.py
        1) 存檔（practice_service.save_audio_file / create_practice_upload）
        2) 更新任務進度（quest_service.update_quest_progress）
        3) 若任務完成 → 發 XP／金幣（reward_service.give_quest_rewards）
           （獎勵邏輯內通常也會連動寵物階段）
    → JSON 回傳訊息、進度、獎勵
  學生畫面更新；老師可在「上傳紀錄」聽音檔
```

老師建立學生：

```text
Streamlit「建立學生」
  POST /api/students
    → api/students.py → student_service.create_student
    → 回傳帳號＋臨時密碼（畫面顯示給老師抄給學生）
```

登入狀態怎麼維持？

```text
登入成功 → api/auth.py 寫入 session（role、teacher_id 或 student_id）
之後請求帶 cookie → guards 檢查 session → 允許或 401
登出 → session.clear()
```

---

## 5. 學生一頁版（不要講成「很多套網頁」）

```text
瀏覽器開 /student/app
  → app.py 回傳 student_spa.html（殼）
  → iframe 再向 /student/login、/home… 要 HTML
  → 各頁 JS fetch /api/...
```

頂層若誤開 `/student/login`，`student_viewport.js` 會導回 `/student/app#login`。

---

## 6. 舊東西在哪（被問到再說）

| 位置 | 說明 |
|------|------|
| `archive/console/` | 早期文字選單 |
| `archive/streamlit_student/` | 舊版 Streamlit 也含學生頁 |
| `archive/docs/midterm_ppt/` | 期中簡報素材 |
| `archive/material/` | 未使用草稿圖 |

正式報告路徑：**學生 `/student/app` + 老師 `streamlit_app.py` + Flask API**。
