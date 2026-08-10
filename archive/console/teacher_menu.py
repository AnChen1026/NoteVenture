from db import SqlUtils
from utils.password_utils import check_password
from services.teacher_service import change_teacher_password
from services.student_service import show_student, create_student, reset_student_password
from services.quest_service import quest_menu
from services.practice_service import practice_upload_menu
from services.shop_service import shop_menu
from services.dashboard_service import show_teacher_dashboard
# =========== 測試 ============
db = SqlUtils()














# ======================================================
# 老師介面
# ======================================================
def teacher_menu(teacher):
    result = show_teacher_dashboard(teacher)
    print(result)
    while True:
        choice = input(
            f'\n======== {teacher["teacher_name"]}老師選單 ========\n'
            '[1]首頁\n'
            '[2]查看學生列表\n'
            '[3]建立學生帳號\n'
            '[4]任務管理\n'
            '[5]查看學生上傳紀錄\n'
            '[6]商品管理\n'
            '[7]轉介學生\n'
            '[8]重設學生密碼\n'
            '[9]設定(修改密碼)\n'
            '[0]登出\n'
            ':'
        )

        if choice == '1':
            result = show_teacher_dashboard(teacher)
            print(result)

        elif choice == '2':
            data = show_student(teacher)
            print(data)

        elif choice == '3':
            student_name = input('請輸入學生姓名:')
            result = create_student(teacher, student_name)
            if result:
                user_name, password = result
                print("建立成功")
                print("學生帳號：", user_name)
                print("暫時密碼：", password)
            else:
                print("建立失敗")

        elif choice == '4':
            quest_menu(teacher)

        elif choice == '5':
            result = practice_upload_menu(teacher)
            print(result)

        elif choice == '6':
            shop_menu(teacher)

        elif choice == '7':
            print('轉介學生功能尚未建立')

        elif choice == '8':
            student_username = input('請輸入學生帳號：')
            result = reset_student_password(student_username)
            print(result)

        elif choice == '9':
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
