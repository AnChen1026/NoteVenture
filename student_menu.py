from db import SqlUtils
from utils.password_utils import check_password
from services.student_service import change_student_password
# =========== 測試 ============
db = SqlUtils()













# ========= 學生介面 ===========

def student_menu(student):
    while True:
        choice = input(
            f'\n======== {student["student_name"]}學生選單 ========\n'
            '[1]主頁\n'
            '[2]設定(修改密碼)\n'
            '[3]任務欄\n'
            '[4]商店\n'
            '[5]上傳練習\n'
            '[6]查看近期展演資訊\n'
            '[0]登出\n'
            ':'
        )
        if choice == '1':
            print('主頁')

        elif choice == '2':
            old_password = input('請輸入密碼：')
            is_correct = check_password(old_password, student['password_hash'])
            if is_correct:
                result = change_student_password(student, old_password)
                print(result)
            else:
                print('密碼輸入錯誤')

        elif choice == '3':
            print('任務欄')

        elif choice == '4':
            print('商店')

        elif choice == '5':
            print('上傳練習')

        elif choice == '6':
            print('查看近期展演資訊')

        elif choice == '0':
            print('已登出')
            break

        else:
            print('輸入錯誤')
                    