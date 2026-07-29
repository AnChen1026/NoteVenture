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






# ========== main ==========
while True:
    choice = input(
        '===== 音樂練習 RPG =====\n'
        '選擇功能\n'
        '[1]老師登入\n'
        '[2]學生登入\n'
        '[3]老師註冊\n'
        '[0]離開\n'
        '：'
                   )
    if choice == '1':
        email = input('請輸入email：')
        password = input('請輸入密碼：')
        teacher = login_teacher(email, password)
        if teacher:
            print('進入老師功能')
            break
        

    elif choice == '2':
        print('學生登入功能尚未開通')

    elif choice == '3':
        while True:
            teacher_name = input('請輸入老師姓名\n：')
            email = input('請輸入電子信箱\n：')
            password = input('請輸入密碼\n：')
            confirm_password = input('請確認密碼\n：')
            if confirm_password == password:
                message = create_teacher(teacher_name, email, password)
                print(message)
                break
            else:
                print('密碼不一致')

    elif choice == '0':
        print('感謝您的使用，再見')
        break

    else:
        print('輸入錯誤')