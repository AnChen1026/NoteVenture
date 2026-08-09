# 學生一頁版實驗區（feature/student-spa）

## 入口

```text
http://127.0.0.1:5000/student/app
```

也可加 hash：`/student/app#home`、`#shop`、`#practice` …

## 做法

- **外層殼頁**固定不卸載：BGM、橫放提示、雙擊全螢幕
- **內層 iframe** 載入現有多頁學生 UI（登入／主頁／商店…）
- 舊網址（`/student/login` 等）仍可單獨開啟，不受影響

## 與 main 的關係

- 本功能在分支 `feature/student-spa`
- 正式展示仍可用 `main` 的多頁版
- 確認穩定後再決定是否合併

## 本機測試

```bash
source .venv/bin/activate
flask --app app run --port 5000
```

瀏覽器開：`http://127.0.0.1:5000/student/app`
