import secrets # 產生安全的隨機資料
import string # 常用字元集合

# 自動產生學生帳號
def generate_student_username(teacher_id):
    num = string.digits
    user_name = f"T{str(teacher_id)}S"
    for _ in range(6):
        user_name += secrets.choice(num)
    return user_name


# 自動產生隨機臨時密碼
def generate_temp_password(length=8):
    alphabet = string.ascii_letters + string.digits # 將英文字母大小寫與數字0-9合成一個字串

    password = ""

    for _ in range(length):
        password += secrets.choice(alphabet) # 用for迴圈跑 每次從alphabet 隨機選一個字元加進密碼

    return password