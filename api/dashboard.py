"""
api/dashboard.py｜首頁摘要數字

- 老師 Streamlit「首頁」→ GET /api/dashboard → get_teacher_dashboard
- 學生端若需要摘要 → GET /api/students/<id>/dashboard → get_student_dashboard
"""

from flask import Blueprint, jsonify
from api.guards import get_login_teacher, get_login_student, json_safe
from services.dashboard_service import get_teacher_dashboard, get_student_dashboard

dashboard_bp = Blueprint('dashboard', __name__)


# ======================================================
# 老師首頁 Dashboard
# ======================================================
@dashboard_bp.get('/api/dashboard')
def api_teacher_dashboard():
    teacher, error = get_login_teacher()
    if error:
        return error

    data = get_teacher_dashboard(teacher)
    return jsonify({'data': json_safe(data)})


# ======================================================
# 學生首頁 Dashboard
# ======================================================
@dashboard_bp.get('/api/students/<int:student_id>/dashboard')
def api_student_dashboard(student_id):
    student, error = get_login_student()
    if error:
        return error
    if student['student_id'] != student_id:
        return jsonify({'message': '只能查看自己的首頁'}), 403

    data = get_student_dashboard(student)
    if not data:
        return jsonify({'message': '找不到學生資料'}), 404
    return jsonify({'data': json_safe(data)})
