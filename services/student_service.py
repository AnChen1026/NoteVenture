from db import SqlUtils
from utils.username_utils import generate_student_username, generate_temp_password
from utils.password_utils import hash_password, check_password

db = SqlUtils()


# ================================================
# 展示學生清單
# ================================================
def show_student(teacher):
    sql = """
    select student_id 序號, username 帳號, student_name 姓名, total_xp 經驗值, total_coin 金幣數 from student where teacher_id = %s;
    """

    result = db.query_all(sql, teacher['teacher_id'])
    if result:
        print('開啟學生列表')
        return result
    else:
        return '沒有學生資料'


# ================================================
# 新增學生並取得帳號密碼
# ================================================
def create_student(teacher, student_name):
    user_name = generate_student_username(teacher['teacher_id'])
    password = generate_temp_password()
    password_hash = hash_password(password)
    sql = """
    INSERT INTO student (teacher_id, username, password_hash, student_name)
    VALUES (%s, %s, %s, %s);
    """

    rowcount = db.execute(sql, (teacher['teacher_id'], user_name, password_hash, student_name))
    if rowcount > 0:
        return user_name, password
    return None


# ================================================
# 老師重置學生密碼
# ================================================
def reset_student_password(username):
    password = generate_temp_password()
    password_hash = hash_password(password)
    sql = """
    UPDATE student
    SET password_hash = %s
    WHERE username = %s;
    """
    rowcount = db.execute(sql, (password_hash, username))
    if rowcount > 0:
        return f'密碼修改成功\n新密碼{password}'
    else:
        return '找不到該學生帳號'


# ================================================
# 學生登入功能
# ================================================
def login_student(username, password):
    sql = """
    SELECT *
    FROM student
    WHERE username = %s;
    """
    try:
        result = db.query_one(sql, (username,))
        if result is None:
            print("查無此學生帳號")
            return None
        is_correct = check_password(password, result["password_hash"])
        if is_correct:
            print(f"登入成功，{result['student_name']} 您好")
            return result
        else:
            print("密碼錯誤")
            return None
    except Exception as e:
        print("登入失敗：", e)
        return None


# ================================================
# 學生修改密碼
# ================================================
def change_student_password(student, old_password):
    while True:
        new_password = input('請輸入新密碼：')
        confirm_password = input('請確認新密碼：')
        if confirm_password != new_password:
            print('密碼不一致')

        elif confirm_password == old_password:
            print('新密碼與原密碼相同')

        elif confirm_password == new_password:
            password_hash = hash_password(new_password)
            sql = """
            UPDATE student
            SET password_hash = %s
            WHERE student_id = %s;
            """
            rowcount = db.execute(sql, (password_hash, student['student_id']))
            if rowcount > 0:
                student['password_hash'] = password_hash
                return '密碼修改成功'
            
            return '密碼修改失敗'
