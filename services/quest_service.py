from db import SqlUtils
db = SqlUtils()


def show_quest(teacher):
    sql = """
    SELECT quest_name 任務名稱, quest_type 任務類型, condition_type 任務條件類型, condition_value 任務條件數值, reward_xp 獎勵經驗, reward_coin 獎勵金幣, is_repeatable 是否為重複任務, is_active 任務是否啟用
    FROM quest_list
    WHERE teacher_id = %s;
    """
    result = db.query_all(sql, (teacher['teacher_id'],))
    if result:
        return result
    return '無任務資料'

def create_quest(teacher):
    while True:
        quest_name = input('請輸入任務名稱:')
        while True:
            choice = input(
                '請輸入任務類型\n'
                '[1]每日任務:DAILY\n'
                '[2]每週任務:WEEKLY\n'
                '[3]隱藏任務:HIDDEN\n'
                '：'
            )
            if choice == '1':
                quest_type = 'DAILY'
                quest_type_text = '每日任務'
                break
            elif choice == '2':
                quest_type = 'WEEKLY'
                quest_type_text = '每週任務'
                break
            elif choice == '3':
                quest_type = 'HIDDEN'
                quest_type_text = '隱藏任務'
                break
            else:
                print('輸入錯誤')

        while True:
            choice = input(
                '請輸入任務條件\n'
                '[1]練習次數\n'
                '[2]練習天數\n'
                '[3]不同曲目數\n'
                '[4]連續練習天數\n'
                '[5]累積上傳次數\n'
                '[6]間隔一段時間後再次練習\n'
                '：'
            )
            if choice == '1':
                condition_type = 'PRACTICE_COUNT'
                condition_value = int(input('需要練習幾次：'))
                condition_type_text = '練習次數'
                break
            elif choice == '2':
                condition_type = 'PRACTICE_DAYS'
                condition_value = int(input('需要練習幾天：'))
                condition_type_text = '練習天數'
                break
            elif choice == '3':
                condition_type = 'DISTINCT_SONGS'
                condition_value = int(input('需要練習幾首不同曲目：'))
                condition_type_text = '不同曲目數'
                break
            elif choice == '4':
                condition_type = 'CONSECUTIVE_DAYS'
                condition_value = int(input('需要連續練習幾天：'))
                condition_type_text = '連續練習天數'
                break
            elif choice == '5':
                condition_type = 'TOTAL_UPLOADS'
                condition_value = int(input('需要練習幾次：'))
                condition_type_text = '累積上傳次數'
                break
            elif choice == '6':
                condition_type = 'RETURN_AFTER_GAP'
                condition_value = int(input('幾天沒上傳會觸發任務：'))
                condition_type_text = '間隔一段時間後再次練習'
                break
            else:
                print('輸入錯誤')

        reward_xp = int(input('獎勵經驗多少：'))
        reward_coin = int(input('獎勵金幣多少：'))
        while True:
            choice = input('是否為一次性任務\n[1]是 [2]否：')
            if choice == '1':
                is_repeatable = False
                is_repeatable_text = '是'
                break
            elif choice == '2':
                is_repeatable = True
                is_repeatable_text = '否'
                break
            else:
                print('輸入錯誤')

        print(
        '\n===== 任務內容確認 =====\n'
        f'任務名稱：{quest_name}\n'
        f'任務類型：{quest_type_text}\n'
        f'任務條件：{condition_type_text}\n'
        f'條件數值：{condition_value}\n'
        f'獎勵經驗：{reward_xp}\n'
        f'獎勵金幣：{reward_coin}\n'
        f'一次性任務：{is_repeatable_text}\n'
        )
        while True:
            choice = input('是否正確\n[1]是 [2]否：')
            if choice == '1':
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
                result = db.execute(
                    sql, 
                    (
                        teacher['teacher_id'], 
                        quest_name, quest_type, 
                        condition_type, 
                        condition_value, 
                        reward_xp, 
                        reward_coin, 
                        is_repeatable
                    )
                )
                if result > 0:
                    return '任務新建成功'
                return '任務建立失敗'
            elif choice == '2':
                break
            else:
                print('輸入錯誤')




# ========= 任務介面 ===========
def quest_menu(teacher):
    while True:
        choice = input(
            '\n======== 任務管理 ========\n'
            '[1]查看任務\n'
            '[2]指派任務\n'
            '[3]新增任務\n'
            '[4]刪除任務\n'
            '[5]修改任務\n'
            '[0]返回\n'
            ':'
        )
        if choice == '1':
            quest = show_quest(teacher)
            print(quest)
        elif choice == '2':
            print('指派任務尚未啟用')
        
        elif choice == '3':
            result = create_quest(teacher)
            print(result)

        elif choice == '4':
            print('刪除任務尚未啟用')

        elif choice == '5':
            print('修改任務尚未啟用')

        elif choice == '0':
            print('返回')
            break

        else:
            print('輸入錯誤')