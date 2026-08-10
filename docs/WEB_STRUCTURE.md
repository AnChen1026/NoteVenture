# 網頁結構說明（正式版）

本專案正式網頁**只有兩條線**：

| 角色 | 介面 | 入口 |
|------|------|------|
| 學生 | Flask HTML／CSS／JS **一頁版（SPA 殼）** | `/student` 或 `/student/app` |
| 老師 | Streamlit 管理後台 | `streamlit run streamlit_app.py` |

兩者都呼叫同一套 Flask API（`api/` → `services/`）。

**期中口試／自己複習串接：** 請先讀 [`docs/MIDTERM_CODE_MAP.md`](MIDTERM_CODE_MAP.md)。

---

## 學生一頁版怎麼組成？

看起來像很多 HTML，但**不是多套網頁**，而是：

```text
/student/app          ← 外殼（BGM、橫放、全螢幕）templates/student_spa.html
    └── iframe 載入功能頁
          ├── /student/login
          ├── /student/home
          ├── /student/practice
          ├── /student/shop
          ├── /student/quests
          ├── /student/pet
          ├── /student/class
          ├── /student/settings
          └── /student/backpack（placeholder）
```

因此 `templates/student_*.html` 與 `static/web/student_*.css/js` **必須保留**，它們是一頁版的「內頁模組」，不是舊版替代品。

### 共用前端

| 檔案 | 用途 |
|------|------|
| `student_spa.*` | 一頁版殼：hash ↔ 路徑、iframe |
| `student_viewport.*` | 橫放／鎖捲動／全螢幕；頂層舊路徑導回 `/student/app` |
| `student_bgm.*` | 背景音樂（殼層播放） |
| `page_transition.*` | 內頁淡入淡出 |

### 素材

正式用圖／音在 `material/`（經 `/assets/material/...` 提供）。未使用的草稿在 `archive/material/`。

---

## 老師後台

- 單一檔：`streamlit_app.py`（**僅老師**登入／管理）
- 設定：`.streamlit/config.toml`
- 舊的「Streamlit 學生頁」備份在 `archive/streamlit_student/`

---

## 不要再當正式入口的東西

見 `archive/README.md`（Console、期中簡報、Streamlit 學生備援、未用素材）。
