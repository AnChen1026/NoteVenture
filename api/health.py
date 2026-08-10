"""
api/health.py｜健康檢查

部署後開 /api/health，確認 Flask 有起來（不碰資料庫也可先測）。
"""

from flask import Blueprint, jsonify

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
