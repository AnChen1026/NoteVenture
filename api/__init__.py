# api 套件
#
# 這裡放 Flask Blueprint（藍圖）：把不同功能的「網址路徑」拆到不同檔案。
# app.py 的 create_app() 會 register_blueprint(...) 把它們掛上。
#
# 典型流程：
#   瀏覽器／Streamlit 請求
#     → api/某檔案（檢查參數、session）
#       → services/某檔案（商業邏輯、SQL）
#         → 回傳 JSON
#
# 串接總表：docs/MIDTERM_CODE_MAP.md
