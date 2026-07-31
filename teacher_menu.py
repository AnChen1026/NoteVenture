from db import SqlUtils
from utils.password_utils import check_password
from services.teacher_service import change_teacher_password
from services.student_service import show_student, create_student, reset_student_password
from services.quest_service import quest_menu
# =========== 測試 ============
db = SqlUtils()














# ========= 老師介面 ===========

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
            '[8]設定(修改密碼)\n'
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
            quest_menu(teacher)

        elif choice == '4':
            print('查看學生上傳紀錄尚未建立')

        elif choice == '5':
            print('商品管理')

        elif choice == '6':
            print('轉介學生功能尚未建立')

        elif choice == '7':
            student_username = input('請輸入學生帳號：')
            result = reset_student_password(student_username)
            print(result)
            
        elif choice == '8':
            old_password = input('請輸入密碼：')
            is_correct = check_password(old_password, teacher['password_hash'])
            if is_correct:
                result = change_teacher_password(teacher, old_password)
                print(result)
            else:
                print('密碼輸入錯誤')

        elif choice == '0':
            print('已登出')
            break

        else:
            print('輸入錯誤')
