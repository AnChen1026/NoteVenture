from flask import Flask
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

    return app


# flask --app app run 啟動時會讀取這個 app 變數
app = create_app()
