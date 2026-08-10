# 學生端上線（方案 B）

目標：

- **雲端**：MySQL + Flask（學生 UI／API）
- **本機**：Streamlit 老師端，連到雲端 Flask

學生開啟：`https://你的網域/student/app`（或 `/student`）

> 舊連結 `/student/login` 會自動導向一頁版。

---

## 一、先準備雲端 MySQL

任選一家可對外連線的 MySQL（例如 Railway MySQL、Aiven、雲端 VM 自架）。

1. 建立資料庫（建議名稱 `music_rpg_v2`）
2. 用客戶端執行專案裡的：

```text
sql/music_rpg_schema_v2.sql
```

3. 記下連線資訊：`host`、`port`、`user`、`password`、`database`

---

## 二、部署 Flask（學生端）

以 **Railway** 或 **Render** 這類「連 GitHub 後自動部署」為例。

### 啟動指令

```bash
gunicorn -w 2 -b 0.0.0.0:$PORT "app:create_app()"
```

若平台沒有 `$PORT`，可改：

```bash
gunicorn -w 2 -b 0.0.0.0:5000 "app:create_app()"
```

### 必填環境變數

| 變數 | 說明 |
|------|------|
| `NOTEADVENTURE_DB_HOST` | MySQL host |
| `NOTEADVENTURE_DB_PORT` | 通常 `3306` |
| `NOTEADVENTURE_DB_USER` | 資料庫帳號 |
| `NOTEADVENTURE_DB_PASSWORD` | 資料庫密碼 |
| `NOTEADVENTURE_DB_NAME` | 例如 `music_rpg_v2` |
| `NOTEADVENTURE_SECRET_KEY` | 自訂一串長隨機字串（登入 cookie 用） |
| `NOTEADVENTURE_COOKIE_SECURE` | 設 `1`（網站是 HTTPS 時） |

> 不要把 `config.ini` 上傳到 GitHub。雲端用環境變數即可。

### 部署後自測

1. 開 `https://你的網域/api/health`（若有 health API）看是否正常  
2. 開 `https://你的網域/student/app`  
3. 用手機測琴房錄音（HTTPS 才比較穩）

---

## 三、本機老師端連雲端

本機 Streamlit **不要**再連 `127.0.0.1:5000`，改連雲端 Flask。

PowerShell 範例：

```powershell
$env:NOTEADVENTURE_API_BASE_URL = "https://你的Flask網域"
streamlit run streamlit_app.py
```

流程會變成：

```text
本機 Streamlit（老師）──HTTP──→ 雲端 Flask API ──→ 雲端 MySQL
學生瀏覽器 ───────────────→ 雲端 Flask 學生頁 ──→ 同一套 API／DB
```

---

## 四、上線前檢查清單

- [ ] schema 已在雲端 MySQL 建好  
- [ ] 環境變數都設齊，且 `SECRET_KEY` 不是預設值  
- [ ] `COOKIE_SECURE=1`  
- [ ] 學生能登入、看任務、上傳練習  
- [ ] 本機 Streamlit 能建立學生／指派任務（資料出現在雲端）  
- [ ] `config.ini`、密碼沒有進 Git  

---

## 五、常見問題

**Q：本機還想用 config.ini 開發可以嗎？**  
可以。沒設環境變數時，`db.py` 仍會讀本機 `config.ini`。

**Q：上傳的錄音檔會存在哪？**  
目前存在伺服器的 `uploads/`。免費方案重部署後檔案可能消失；測試階段通常可接受，之後可再改雲端儲存。

**Q：只要學生測，一定要上 Streamlit 嗎？**  
不用。Streamlit 可留在你自己電腦。
