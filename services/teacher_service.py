from db import SqlUtils
from utils.password_utils import hash_password, check_password
db = SqlUtils()

# 新增老師功能
def create_teacher(teacher_name, email, password):
    sql = """
    INSERT INTO teacher (teacher_name, email, password_hash)
    VALUES (%s, %s, %s);
    """
    password_hash = hash_password(password)
    result = db.execute(sql, (teacher_name, email, password_hash))

    if result:
        return '老師帳號建立成功'
    else:
        return '老師帳號建立失敗'

def login_teacher(email, password):
    sql = """
    SELECT teacher_id, teacher_name, email, password_hash
    FROM teacher
    WHERE email = %s
    """
    try:
        result = db.query_one(sql, (email,))
        if result is None:
            print("查無此老師帳號")
            return None
        is_correct = check_password(password, result["password_hash"])
        if is_correct:
            print(f"登入成功，{result['teacher_name']} 老師您好")
            return result
        else:
            print("密碼錯誤")
            return None
    except Exception as e:
        print("老師登入失敗：", e)
        return None

