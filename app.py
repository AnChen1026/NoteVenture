"""
NoteAdventure｜Flask 進入點（Application Factory）

報告時可以這樣講整條線：

1. 啟動：flask --app app run  →  讀取下方的 app = create_app()
2. 老師網頁（Streamlit）用 HTTP 打 /api/...
3. 學生網頁（HTML／JS）也用 fetch 打同一套 /api/...
4. api/*.py 負責收請求、檢查登入（session）、再呼叫 services/
5. services/ 負責商業邏輯與資料庫（你已熟悉，這裡不改）

本檔只做三件事：
- 建立 Flask app、設定 session cookie
- 掛上各功能 Blueprint（api/）
- 提供學生「頁面」路由（回傳 HTML）與素材路由（material/）
"""

import os

from flask import Flask, render_template, send_from_directory

# 各功能的「路由藍圖」：一個檔案管一類 API
from api.health import health_bp
from api.auth import auth_bp
from api.students import students_bp
from api.quests import quests_bp
from api.practice import practice_bp
from api.shop import shop_bp
from api.pet import pet_bp
from api.dashboard import dashboard_bp
from api.class_board import class_bp


def create_app():
    """建立並設定 Flask 應用程式（工廠函式，方便測試／部署重複建立）。"""
    app = Flask(__name__)

    # ---------- session（登入狀態存在伺服器端 cookie）----------
    # 正式環境請用環境變數設密鑰，不要用預設字串上線
    app.secret_key = os.environ.get(
        'NOTEADVENTURE_SECRET_KEY',
        'noteadventure-dev-secret',
    )
    # HTTPS 上線時設 NOTEADVENTURE_COOKIE_SECURE=1，瀏覽器才只在安全連線送 cookie
    cookie_secure = os.environ.get('NOTEADVENTURE_COOKIE_SECURE', '').lower() in (
        '1', 'true', 'yes',
    )
    app.config['SESSION_COOKIE_SECURE'] = cookie_secure
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 降低 CSRF 風險的常見設定
    app.config['JSON_AS_ASCII'] = False  # API 回傳中文時不要變成 \uXXXX
    app.config['TEMPLATES_AUTO_RELOAD'] = True  # 改 HTML 後開發時較快看到新內容

    # ---------- 註冊 API（JSON）----------
    # 註冊後，例如 auth_bp 裡的 @auth_bp.post('/api/teachers/login') 就會生效
    app.register_blueprint(health_bp)      # GET  /api/health
    app.register_blueprint(auth_bp)        # 登入／登出／改密碼／註冊
    app.register_blueprint(students_bp)    # 老師：學生列表／建立／重設密碼
    app.register_blueprint(quests_bp)      # 任務建立／指派／學生查看
    app.register_blueprint(practice_bp)    # 練習上傳（會連動任務進度與獎勵）
    app.register_blueprint(shop_bp)        # 商店／購買／兌換
    app.register_blueprint(pet_bp)         # 寵物狀態
    app.register_blueprint(dashboard_bp)   # 老師／學生首頁摘要
    app.register_blueprint(class_bp)       # 教室：兩廳院節目看板

    # ---------- 學生「網頁」路由（回傳 HTML，不是 JSON）----------
    # 正式入口只有一頁版殼；其餘路徑是殼裡 iframe 載入的功能內頁。
    # 詳細開啟方式：docs/啟動說明.md ；舊版結構筆記：archive/docs/

    @app.get('/student')
    @app.get('/student/')
    @app.get('/student/app')
    def student_spa_page():
        """學生正式入口：外殼（BGM／橫放／全螢幕）+ iframe。"""
        return render_template('student_spa.html')

    @app.get('/student/login')
    def student_login_page():
        """登入內頁（通常由 SPA iframe 載入）。"""
        return render_template('student_login.html')

    @app.get('/student/home')
    def student_home_page():
        return render_template('student_home.html')

    @app.get('/student/practice')
    def student_practice_page():
        return render_template('student_practice.html')

    @app.get('/student/pet')
    def student_pet_page():
        return render_template('student_pet.html')

    @app.get('/student/shop')
    def student_shop_page():
        return render_template('student_shop.html')

    @app.get('/student/quests')
    def student_quests_page():
        return render_template('student_quests.html')

    @app.get('/student/class')
    def student_class_page():
        return render_template('student_class.html')

    @app.get('/student/backpack')
    def student_backpack_page():
        return render_template('student_backpack.html')

    @app.get('/student/settings')
    def student_settings_page():
        return render_template('student_settings.html')

    # 學生頁面用的圖／音：HTML 寫 /assets/material/home.png → 對應 material/home.png
    @app.get('/assets/material/<path:filename>')
    def material_asset(filename):
        return send_from_directory('material', filename)

    return app


# 本機：flask --app app run
# 雲端：gunicorn ... "app:create_app()" 也會用到這個模組
app = create_app()
