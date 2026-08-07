from flask import Flask, render_template, send_from_directory
from api.health import health_bp
from api.auth import auth_bp
from api.students import students_bp
from api.quests import quests_bp
from api.practice import practice_bp
from api.shop import shop_bp
from api.pet import pet_bp
from api.dashboard import dashboard_bp


# ======================================================
# Flask 應用程式工廠
# ======================================================
def create_app():
    app = Flask(__name__)

    # session 需要密鑰，用來簽名 cookie；開發用預設值，正式環境請改掉
    app.secret_key = 'noteadventure-dev-secret'
    # JSON_AS_ASCII=False：回傳中文時不要轉成 \uXXXX
    app.config['JSON_AS_ASCII'] = False

    # 註冊 API 藍圖（Blueprint）
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(quests_bp)
    app.register_blueprint(practice_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(pet_bp)
    app.register_blueprint(dashboard_bp)

    # --------------------------------------------------
    # 學生 HTML 前端（v2，素材來自 material/）
    # --------------------------------------------------
    @app.get('/student/login')
    def student_login_page():
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

    @app.get('/student/backpack')
    def student_backpack_page():
        return render_template(
            'student_placeholder.html',
            title='背包',
            message='背包頁面建置中，之後會顯示已購買／持有的物品。'
        )

    @app.get('/student/settings')
    def student_settings_page():
        return render_template(
            'student_placeholder.html',
            title='設定｜修改密碼',
            message='修改密碼頁面建置中。'
        )

    @app.get('/assets/material/<path:filename>')
    def material_asset(filename):
        return send_from_directory('material', filename)

    return app


# flask --app app run 啟動時會讀取這個 app 變數
app = create_app()
