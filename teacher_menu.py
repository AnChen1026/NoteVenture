from db import SqlUtils
from utils.password_utils import check_password
from services.teacher_service import change_teacher_password
from services.student_service import show_student, create_student, reset_student_password

# =========== 測試 ============
db = SqlUtils()


def show_quest():
    sql = """
    SELECT quest_id 任務ID, quest_name 任務名稱, quest_type 任務類型, condition_type 任務條件類型, condition_value 任務條件數值, reward_xp 獎勵經驗, reward_coin 獎勵金幣, is_repeatable 是否為重複任務, is_active 任務是否啟用 FROM quest_list
    """
    result = db.query_all(sql)
    if result:
        return result
    return '無任務資料'

def create_quest(teacher):
    quest_name = input('請輸入任務名稱:')
    while True:
        choice = input('請輸入任務類型\n[1]每日任務:DAILY [2]每週任務:WEEKLY [3]隱藏任務:HIDDEN')
        if choice == '1':
            quest_type = 'DAILY'
            break
        elif choice == '2':
            quest_type = 'WEEKLY'
            break
        elif choice == '3':
            quest_type = 'HIDDEN'
            break
        else:
            print('輸入錯誤')
    condition_type = input('')
    condition_value = input('')
    reward_xp = input('')
    reward_coin = input('')
    is_repeatable = input('')
    sql = """
    INSERT INTO quest_list (
    teacher_id,
    quest_name,
    quest_type,
    condition_type,
    condition_value,
    reward_xp,
    reward_coin,
    is_repeatable
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """






# ========= 任務介面 ===========
def quest_menu():
    while True:
        choice = input(
            '\n======== 任務管理 ========\n'
            '[1]查看任務\n'
            '[2]新增任務\n'
            '[3]刪除任務\n'
            '[4]修改任務\n'
            '[0]返回\n'
            ':'
        )
        if choice == '1':
            quest = show_quest()
            print(quest)
        elif choice == '2':
            print('新增任務')

        elif choice == '3':
            print('刪除任務')

        elif choice == '4':
            print('修改任務')

        elif choice == '0':
            print('返回')
            break

        else:
            print('輸入錯誤')















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
            quest_menu()

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
