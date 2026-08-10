"""
api/class_board.py｜學生「教室」看板（兩廳院近期音樂節目）

學生 HTML（student_class.js）→ GET /api/class/ntch-programs
→ services.ntch_service（對外抓資料／快取，不是核心 RPG 資料表）
"""

from flask import Blueprint, jsonify, request
from services.ntch_service import get_upcoming_music_programs

class_bp = Blueprint("class_board", __name__)


@class_bp.get("/api/class/ntch-programs")
def api_ntch_programs():
    """教室看板：近一個月兩廳院音樂相關節目。"""
    force = str(request.args.get("refresh", "")).lower() in ("1", "true", "yes")
    try:
        payload = get_upcoming_music_programs(force_refresh=force)
        return jsonify(
            {
                "message": "ok",
                "fetched_at": payload.get("fetched_at"),
                "source": payload.get("source"),
                "count": payload.get("count", 0),
                "data": payload.get("data") or [],
            }
        )
    except Exception:
        return jsonify({"message": "目前無法取得兩廳院節目資料，請稍後再試", "data": []}), 502
