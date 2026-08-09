# 學生一頁版（正式入口）

## 入口

```text
https://你的網域/student/app
https://你的網域/student
```

也可加 hash：`/student/app#home`、`#shop`、`#practice` …

本機：`http://127.0.0.1:5000/student/app`

舊路徑（如 `/student/login`）在「頂層開啟」時會自動導向一頁版；iframe 內仍載入原頁，不會迴圈。

## 做法

- **外層殼頁**固定不卸載：BGM、橫放提示、雙擊全螢幕
- **內層 iframe** 載入現有多頁學生 UI
- 內頁切換仍用原本的**淡入淡出**（`page_transition`）
