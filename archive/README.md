# archive／舊版與備援（非正式執行路徑）

這裡放**不再作為正式網頁入口**、但可能還用得到的舊程式與素材。

| 目錄 | 內容 | 說明 |
|------|------|------|
| `console/` | `main.py`、`teacher_menu.py`、`student_menu.py` | 早期文字選單；若要本機測 service 可 `python archive/console/main.py`（需自行調整 import 路徑） |
| `streamlit_student/` | `streamlit_app_with_student_backup.py` | 舊版「Streamlit 也含學生頁」完整備份 |
| `docs/midterm_ppt/` | 期中簡報、截圖腳本 | 展示用，非 runtime |
| `docs/`（根下數支 md） | 舊 WEB_STRUCTURE／MIDTERM_CODE_MAP／STUDENT_SPA／DEPLOY_STUDENT | 已自正式 `docs/` 移出 |
| `templates/` | `student_placeholder.html` | 舊佔位頁（背包已改正式頁） |
| `api/` | `student_dashboard_route.py` | 舊學生 dashboard API 備註；正式 app 已不註冊 |
| `material/` | `other/`、`unused/`、`pet/`、`quest_test.mp4` | 未被學生一頁版引用的素材草稿 |

## 正式網頁（請看 repo 根目錄）

- **學生**：Flask 一頁版 → `/student/app`（`templates/` + `static/web/`）
- **老師**：`streamlit_app.py`（僅老師管理）
- **API／商業邏輯**：`api/`、`services/`（`services/` 請勿在整理網頁時改動）

正式文件：`docs/README.md`、`docs/啟動說明.md`。
