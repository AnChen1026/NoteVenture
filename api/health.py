from flask import Blueprint, jsonify

# health_bp：健康檢查專用藍圖
health_bp = Blueprint('health', __name__)


# ======================================================
# 健康檢查：確認 Flask 有正常啟動
# ======================================================
@health_bp.get('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'NoteAdventure API 運作中'
    })
