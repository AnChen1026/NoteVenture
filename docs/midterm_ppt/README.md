# NoteAdventure 期中簡報使用說明

## 檔案

- `NoteAdventure_Midterm_Report.pptx`：簡報主檔（約 10–15 分鐘）
- `screenshots/`：Playwright 擷取的實際前端畫面
- `screenshots_crop/`：裁切後用於簡報的截圖
- `build_ppt.py`：重新產生簡報
- `capture_screens.py`：重新擷取畫面（需先啟動 Flask + Streamlit）

## 建議時間分配

| 頁次 | 主題 | 時間 |
|------|------|------|
| 1–2 | 封面、大綱 | 1 分 |
| 3–4 | 動機、角色 | 2 分 |
| 5–6 | 架構、流程 | 2–3 分 |
| 7–13 | 實際畫面演示 | 6–7 分 |
| 14–15 | 進度、結語 Q&A | 2 分 |

## 重新產生

```bash
# 先啟動
flask --app app run --port 5000
streamlit run streamlit_app.py

# 擷取畫面（帳密用環境變數，不要寫進程式）
# PowerShell 範例：
# $env:NOTEADVENTURE_TEACHER_PASSWORD="你的老師密碼"
# $env:NOTEADVENTURE_STUDENT_PASSWORD="你的學生密碼"
python docs/midterm_ppt/capture_screens.py

# 產生 PPT
python docs/midterm_ppt/build_ppt.py
```
