from flask import Blueprint, request, jsonify, session
from db import SqlUtils
from utils.password_utils import hash_password, check_password
from services.teacher_service import login_teacher, create_teacher
from services.student_service import login_student
from api.guards import get_login_teacher, get_login_student

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
# 老師註冊
# ======================================================
@auth_bp.post('/api/teachers/register')
def api_teacher_register():
    data = request.get_json(silent=True) or {}
    teacher_name = str(data.get('teacher_name', '')).strip()
    email = str(data.get('email', '')).strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if teacher_name == '' or email == '' or password == '' or confirm_password == '':
        return jsonify({'message': '請完整填寫姓名、電子信箱與密碼'}), 400
    if password != confirm_password:
        return jsonify({'message': '兩次密碼不一致'}), 400

    existing = db.query_one(
        """
        SELECT teacher_id
        FROM teacher
        WHERE email = %s;
        """,
        (email,)
    )
    if existing:
        return jsonify({'message': '此電子信箱已註冊'}), 409

    result = create_teacher(teacher_name, email, password)
    if result == '老師帳號建立成功':
        return jsonify({'message': result}), 201
    return jsonify({'message': result}), 500


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
# 老師修改密碼
# ======================================================
@auth_bp.post('/api/teachers/change-password')
def api_teacher_change_password():
    teacher, error = get_login_teacher()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if old_password == '' or new_password == '' or confirm_password == '':
        return jsonify({'message': '請完整輸入舊密碼與新密碼'}), 400

    row = db.query_one(
        """
        SELECT password_hash
        FROM teacher
        WHERE teacher_id = %s;
        """,
        (teacher['teacher_id'],)
    )
    if not check_password(old_password, row['password_hash']):
        return jsonify({'message': '舊密碼錯誤'}), 401
    if new_password != confirm_password:
        return jsonify({'message': '兩次新密碼不一致'}), 400
    if new_password == old_password:
        return jsonify({'message': '新密碼不可與舊密碼相同'}), 400

    rowcount = db.execute(
        """
        UPDATE teacher
        SET password_hash = %s
        WHERE teacher_id = %s;
        """,
        (hash_password(new_password), teacher['teacher_id'])
    )
    if rowcount > 0:
        return jsonify({'message': '密碼修改成功'})
    return jsonify({'message': '密碼修改失敗'}), 500


# ======================================================
# 學生修改密碼
# ======================================================
@auth_bp.post('/api/students/change-password')
def api_student_change_password():
    student, error = get_login_student()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if old_password == '' or new_password == '' or confirm_password == '':
        return jsonify({'message': '請完整輸入舊密碼與新密碼'}), 400

    row = db.query_one(
        """
        SELECT password_hash
        FROM student
        WHERE student_id = %s;
        """,
        (student['student_id'],)
    )
    if not check_password(old_password, row['password_hash']):
        return jsonify({'message': '舊密碼錯誤'}), 401
    if new_password != confirm_password:
        return jsonify({'message': '兩次新密碼不一致'}), 400
    if new_password == old_password:
        return jsonify({'message': '新密碼不可與舊密碼相同'}), 400

    rowcount = db.execute(
        """
        UPDATE student
        SET password_hash = %s,
            password_changed = TRUE
        WHERE student_id = %s;
        """,
        (hash_password(new_password), student['student_id'])
    )
    if rowcount > 0:
        return jsonify({'message': '密碼修改成功'})
    return jsonify({'message': '密碼修改失敗'}), 500


# ======================================================
# 登出
# ======================================================
@auth_bp.post('/api/logout')
def api_logout():
    session.clear()
    return jsonify({'message': '已登出'})
