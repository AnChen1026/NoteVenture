# =========== 測試 ============
from db import SqlUtils
from utils.username_utils import generate_student_username, generate_temp_password
from utils.password_utils import hash_password

db = SqlUtils()
# def create_student(teacher_id=teacher['teacher_id'], username, password):


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

def create_student(teacher, student_name):
    user_name = generate_student_username(teacher['teacher_id'])
    password = generate_temp_password()
    password_hash = hash_password(password)
    sql = """
    INSERT INTO student (teacher_id, username, password_hash, student_name)
    VALUES (%s, %s, %s, %s)
    """

    result = db.execute(sql, (teacher['teacher_id'], user_name, password_hash, student_name))
    if result:
        return user_name, password
    return None

def reset_student_password(student_name):
    sql = """
                UPDATE teacher
                SET password_hash = %s
                WHERE email = %s
                """



def teacher_menu(teacher):
    while True:
        choice = input(
            f'\n======== {teacher["teacher_name"]}老師選單 ========\n'
            '[1]查看學生列表\n'
            '[2]建立學生帳號\n'
            '[3]任務管理\n'
            '[4]查看學生上傳紀錄\n'
            '[5]商品管理\n'
            '[6]轉介學生\n'
            '[7]重設學生密碼\n'
            '[8]設定\n'
            '[0]登出\n'
            ':'
        )

        if choice == '1':
            data= show_student(teacher)
            print(data)

        elif choice == '2':
            student_name = input('請輸入學生姓名:')
            result = create_student(teacher, student_name)
            if result:
                user_name, password = result
                print("建立成功")
                print("學生帳號：", user_name)
                print("暫時密碼：", password)
            else:
                print("建立失敗")

        elif choice == '3':
            print('任務管理')

        elif choice == '4':
            print('查看學生上傳紀錄')

        elif choice == '5':
            print('商品管理')

        elif choice == '6':
            print('轉介學生')

        elif choice == '7':
            print('重設學生密碼')

        elif choice == '8':
            print('設定')

        elif choice == '0':
            print('謝謝')
            break

        else:
            print('輸入錯誤')
