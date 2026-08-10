"""
api/students.py｜老師管理學生帳號

主要給 streamlit_app.py 使用：
- GET  /api/students              → student_service.show_student
- POST /api/students              → create_student（回傳帳號＋臨時密碼）
- POST /api/students/reset-password → reset_student_password
"""

from flask import Blueprint, request, jsonify
from api.guards import get_login_teacher, json_safe
from services.student_service import show_student, create_student, reset_student_password

students_bp = Blueprint('students', __name__)


# ======================================================
# 老師查看自己的學生列表
# ======================================================
@students_bp.get('/api/students')
def api_list_students():
    teacher, error = get_login_teacher()
    if error:
        return error

    result = show_student(teacher)
    if isinstance(result, str):
        return jsonify({'message': result, 'data': []})
    return jsonify({'data': json_safe(result)})


# ======================================================
# 老師建立學生帳號
# ======================================================
@students_bp.post('/api/students')
def api_create_student():
    teacher, error = get_login_teacher()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    student_name = str(data.get('student_name', '')).strip()
    if student_name == '':
        return jsonify({'message': '請輸入學生姓名'}), 400

    result = create_student(teacher, student_name)
    if not result:
        return jsonify({'message': '建立失敗'}), 500

    username, password = result
    return jsonify({
        'message': '建立成功',
        'username': username,
        'temp_password': password
    }), 201


# ======================================================
# 老師重設學生密碼
# ======================================================
@students_bp.post('/api/students/reset-password')
def api_reset_student_password():
    teacher, error = get_login_teacher()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    username = str(data.get('username', '')).strip()
    if username == '':
        return jsonify({'message': '請輸入學生帳號'}), 400

    # 確認學生屬於這位老師
    from db import SqlUtils
    db = SqlUtils()
    student = db.query_one(
        """
        SELECT student_id
        FROM student
        WHERE username = %s
        AND teacher_id = %s;
        """,
        (username, teacher['teacher_id'])
    )
    if not student:
        return jsonify({'message': '找不到該學生帳號'}), 404

    result = reset_student_password(username)
    if result.startswith('密碼修改成功'):
        new_password = result.split('新密碼', 1)[-1]
        return jsonify({
            'message': '密碼重設成功',
            'temp_password': new_password
        })
    return jsonify({'message': result}), 400
