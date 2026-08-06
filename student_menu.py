from db import SqlUtils
from utils.password_utils import check_password
from services.student_service import change_student_password
from services.quest_service import student_show_quest
from services.practice_service import upload_practice
# =========== 測試 ============
db = SqlUtils()













# ========= 顯示用中文對照 ===========

quest_type_text = {
    'DAILY': '每日任務',
    'WEEKLY': '每週任務',
    'HIDDEN': '隱藏任務'
}

condition_type_text = {
    'PRACTICE_COUNT': '練習次數',
    'PRACTICE_DAYS': '練習天數',
    'DISTINCT_SONGS': '不同曲目數',
    'CONSECUTIVE_DAYS': '連續練習天數',
    'TOTAL_UPLOADS': '累積上傳次數',
    'RETURN_AFTER_GAP': '間隔一段時間後再次練習'
}

quest_status_text = {
    'COMPLETED': '已完成',
    'ACTIVE': '進行中',
    'EXPIRED': '已過期'
}


# ======================================================
# 學生介面
# ======================================================
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
            result = student_show_quest(student)
            if isinstance(result, str):
                print(result)
            else:
                print('\n======== 我的任務 ========')
                for quest in result:
                    if quest['expires_at'] is None:
                        expires_at_text = '無期限'
                    else:
                        expires_at_text = quest['expires_at'].strftime('%Y-%m-%d %H:%M')
                    print()
                    print(f"[{quest_type_text[quest['quest_type']]}] {quest['quest_name']}")
                    print(f"條件：{condition_type_text[quest['condition_type']]} {quest['condition_value']}")
                    print(f"進度：{quest['progress_value']} / {quest['condition_value']}")
                    print(f"到期：{expires_at_text}")
                    print(f"狀態：{quest_status_text[quest['quest_status']]}")
                    print(f"獎勵：經驗 {quest['reward_xp']} / 金幣 {quest['reward_coin']}")
        elif choice == '4':
            print('商店')

        elif choice == '5':
            result = upload_practice(student)
            print(result)

        elif choice == '6':
            print('查看近期展演資訊')

        elif choice == '0':
            print('已登出')
            break

        else:
            print('輸入錯誤')
                    