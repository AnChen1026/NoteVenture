# NoteAdventure 期中簡報使用說明

## 檔案

- `NoteAdventure_Midterm_Report.pptx`：簡報主檔（約 10 分鐘／16 頁）
- `SPEAKER_SCRIPT.md`：逐字講稿與時間分配
- `screenshots/`、`screenshots_crop/`：操作截圖
- `build_ppt.py`：重新產生簡報
- `make_console_shots.py`：產生 Console 選單畫面
- `crop_focus.py`：裁切重點區域（避免簡報塞滿無關空白）
- `capture_screens.py`：擷取 Streamlit 畫面
- `capture_student_html.py`：擷取學生 HTML UI（需 Flask 已啟動）

## 簡報故事線

1. 開發原點：老師難以掌握／追蹤練習  
2. 解方：遊戲化激勵上傳  
3. **Console 操作畫面（一小段）**  
4. **Streamlit 老師前端操作截圖**  
5. 溫度不足 → **學生 HTML UI 實際操作截圖**  
6. 架構與重要功能邏輯  
7. 成果與結語  

## 建議時間分配

| 頁次 | 主題 | 時間 |
|------|------|------|
| 1–2 | 封面、大綱 | 0:35 |
| 3–4 | 原點、解方 | 2:10 |
| 5–9 | Console → Streamlit → 轉折 | 3:30 |
| 10–14 | 學生 UI、架構、邏輯 | 3:00 |
| 15–16 | 進度、結語 | 0:45 |

詳細講稿請看 `SPEAKER_SCRIPT.md`。

## 重新產生簡報

```bash
# 在專案根目錄
.\.venv\Scripts\python.exe docs/midterm_ppt/make_console_shots.py
.\.venv\Scripts\python.exe docs/midterm_ppt/crop_focus.py
.\.venv\Scripts\python.exe docs/midterm_ppt/build_ppt.py
```

若要更新學生 HTML 截圖（Flask 需在 `http://127.0.0.1:5000` 運行）：

```bash
.\.venv\Scripts\python.exe docs/midterm_ppt/capture_student_html.py
.\.venv\Scripts\python.exe docs/midterm_ppt/build_ppt.py
```

若要更新 Streamlit 截圖：

```bash
streamlit run streamlit_app.py
# PowerShell 用環境變數帶入密碼，不要寫進程式
.\.venv\Scripts\python.exe docs/midterm_ppt/capture_screens.py
.\.venv\Scripts\python.exe docs/midterm_ppt/build_ppt.py
```
