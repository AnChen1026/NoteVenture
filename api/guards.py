from flask import session, jsonify
from db import SqlUtils

db = SqlUtils()


# ======================================================
# 取得目前登入的老師，失敗時回傳錯誤回應
# ======================================================
def get_login_teacher():
    if session.get('role') != 'teacher':
        return None, (jsonify({'message': '請先以老師身分登入'}), 401)

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
        return None, (jsonify({'message': '請先以老師身分登入'}), 401)
    return teacher, None


# ======================================================
# 取得目前登入的學生，失敗時回傳錯誤回應
# ======================================================
def get_login_student():
    if session.get('role') != 'student':
        return None, (jsonify({'message': '請先以學生身分登入'}), 401)

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
        return None, (jsonify({'message': '請先以學生身分登入'}), 401)
    return student, None


# ======================================================
# 把 datetime 轉成字串，方便 jsonify
# ======================================================
def json_safe(value):
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if hasattr(value, 'isoformat'):
        return value.isoformat(sep=' ', timespec='seconds')
    return value
