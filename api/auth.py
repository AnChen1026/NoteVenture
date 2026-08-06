from flask import Blueprint, request, jsonify, session
from db import SqlUtils
from services.teacher_service import login_teacher
from services.student_service import login_student

auth_bp = Blueprint('auth', __name__)
db = SqlUtils()


# ======================================================
# 老師公開資料（不回傳密碼）
# ======================================================
def teacher_public(teacher):
    return {
        'teacher_id': teacher['teacher_id'],
        'teacher_name': teacher['teacher_name'],
        'email': teacher['email']
    }


# ======================================================
# 學生公開資料（不回傳密碼）
# ======================================================
def student_public(student):
    return {
        'student_id': student['student_id'],
        'teacher_id': student['teacher_id'],
        'username': student['username'],
        'student_name': student['student_name'],
        'password_changed': bool(student['password_changed']),
        'total_xp': student['total_xp'],
        'total_coin': student['total_coin']
    }


# ======================================================
# 老師登入
# ======================================================
@auth_bp.post('/api/teachers/login')
def api_teacher_login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if email == '' or password == '':
        return jsonify({'message': '請輸入電子信箱與密碼'}), 400

    teacher = login_teacher(email, password)
    if not teacher:
        return jsonify({'message': '電子信箱或密碼錯誤'}), 401

    # session：記住這位使用者，之後的 API 才能知道是誰
    session.clear()
    session['role'] = 'teacher'
    session['teacher_id'] = teacher['teacher_id']

    return jsonify({
        'message': '登入成功',
        'role': 'teacher',
        'user': teacher_public(teacher)
    })


# ======================================================
# 學生登入
# ======================================================
@auth_bp.post('/api/students/login')
def api_student_login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if username == '' or password == '':
        return jsonify({'message': '請輸入帳號與密碼'}), 400

    student = login_student(username, password)
    if not student:
        return jsonify({'message': '帳號或密碼錯誤'}), 401

    session.clear()
    session['role'] = 'student'
    session['student_id'] = student['student_id']

    return jsonify({
        'message': '登入成功',
        'role': 'student',
        'user': student_public(student)
    })


# ======================================================
# 查詢目前登入者
# ======================================================
@auth_bp.get('/api/me')
def api_me():
    role = session.get('role')

    if role == 'teacher':
        teacher = db.query_one(
            """
            SELECT teacher_id, teacher_name, email
            FROM teacher
            WHERE teacher_id = %s;
            """,
            (session.get('teacher_id'),)
        )
        if not teacher:
            session.clear()
            return jsonify({'message': '尚未登入'}), 401
        return jsonify({
            'role': 'teacher',
            'user': teacher_public(teacher)
        })

    if role == 'student':
        student = db.query_one(
            """
            SELECT *
            FROM student
            WHERE student_id = %s;
            """,
            (session.get('student_id'),)
        )
        if not student:
            session.clear()
            return jsonify({'message': '尚未登入'}), 401
        return jsonify({
            'role': 'student',
            'user': student_public(student)
        })

    return jsonify({'message': '尚未登入'}), 401


# ======================================================
# 登出
# ======================================================
@auth_bp.post('/api/logout')
def api_logout():
    session.clear()
    return jsonify({'message': '已登出'})
