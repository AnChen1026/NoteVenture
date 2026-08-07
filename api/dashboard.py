from flask import Blueprint, jsonify
from api.guards import get_login_teacher, json_safe
from services.dashboard_service import get_teacher_dashboard

dashboard_bp = Blueprint('dashboard', __name__)


# ======================================================
# 老師 Dashboard 總覽
# ======================================================
@dashboard_bp.get('/api/dashboard')
def api_teacher_dashboard():
    teacher, error = get_login_teacher()
    if error:
        return error

    data = get_teacher_dashboard(teacher)
    return jsonify({'data': json_safe(data)})
