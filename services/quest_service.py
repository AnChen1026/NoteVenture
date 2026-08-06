from db import SqlUtils
from datetime import datetime, timedelta
db = SqlUtils()

# ======================================================
# 老師任務查看
# ======================================================
def teacher_show_quest(teacher):
    sql = """
    SELECT quest_id 任務編號,quest_name 任務名稱, quest_type 任務類型, condition_type 任務條件類型, condition_value 任務條件數值, reward_xp 獎勵經驗, reward_coin 獎勵金幣, is_repeatable 是否為重複任務, is_active 任務是否啟用
    FROM quest_list
    WHERE teacher_id = %s;
    """
    result = db.query_all(sql, (teacher['teacher_id'],))
    if result:
        return result
    return '無任務資料'

# ======================================================
# 學生任務查看
# ======================================================
def student_show_quest(student):
    sql = """
    SELECT quest_name 任務名稱, quest_type 任務類型, condition_type 任務條件類型, condition_value 任務條件數值, reward_xp 獎勵經驗, reward_coin 獎勵金幣
    FROM quest_list
    WHERE teacher_id = %s
    AND quest_type != 'HIDDEN';
    """
    result = db.query_all(sql, (student['teacher_id'],))
    if result:
        return result
    return '無任務資料'

# ======================================================
# 新增任務
# ======================================================
def create_quest(teacher):
    while True:
        quest_name = input('請輸入任務名稱([0]返回):')
        if quest_name == '0':
            break
        while True:
            choice = input(
                '請輸入任務類型\n'
                '[1]每日任務\n'
                '[2]每週任務\n'
                '[3]隱藏任務\n'
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

# ======================================================
# 修改任務
# ======================================================
def update_quest(teacher):
    while True:
        result = teacher_show_quest(teacher)
        menu_dict = {}
        i = 1
        for quest in result:
            menu_dict[f'{i}'] = {
                'quest_id': quest['任務編號'],
                'quest_name': quest['任務名稱']
            }
            i += 1


        # ======================================================
        # 獲得 欲修改任務 change_quest與對應id
        # ======================================================

        while True:
            print('===== 需要修改哪一項任務 =====')
            for i in range(1,len(menu_dict)+1):
                print(f'[{i}] {menu_dict[str(i)]['quest_name']}')

            choice = input('[0]取消\n:')
            if choice == '0':
                return '已取消修改'
            elif choice in menu_dict:
                select_quest = menu_dict[choice]
                change_quest = select_quest['quest_name']
                quest_id = select_quest['quest_id']

                # ======================================================
                # 獲得 欲修改欄位 change_type
                # ======================================================
        
                type_dict = {
                    '1':'quest_name',
                    '2':'quest_type',
                    '3':'condition_type',
                    '4':'condition_value',
                    '5':'reward_xp',
                    '6':'reward_coin',
                    '7':'is_repeatable'
                }

                cancel_change_type = False
                while True:
                    choice = input(
                        '===== 需要修改哪一項目 =====\n'
                        '[1]任務名稱\n'
                        '[2]任務類型\n'
                        '[3]任務條件類型\n'
                        '[4]任務條件數值\n'
                        '[5]獎勵經驗\n'
                        '[6]獎勵金幣\n'
                        '[7]是否為重複任務\n'
                        '[0]返回\n'
                        ':'
                    )
                    if choice in type_dict:
                        change_type = type_dict[choice]
                        break
                    elif choice == '0':
                        cancel_change_type = True
                        break
                    else:
                        print('輸入錯誤')
                if cancel_change_type:
                    break
                    
                # ======================================================
                # 獲得 欲修改內容 change_content
                # ======================================================
        
                if change_type == 'quest_name':
                    change_content = input('新任務名稱:')
                    
                elif change_type == 'quest_type':
                    while True:
                        choice = input(
                            '新任務類型\n'
                            '[1]每日任務\n'
                            '[2]每週任務\n'
                            '[3]隱藏任務\n'
                            '：'
                        )
                        if choice == '1':
                            change_content = 'DAILY'
                            break
                        elif choice == '2':
                            change_content = 'WEEKLY'
                            break
                        elif choice == '3':
                            change_content = 'HIDDEN'
                            break
                        else:
                            print('輸入錯誤')
                    
                    
                elif change_type == 'condition_type':
                    while True:
                        choice = input(
                        '新任務條件\n'
                        '[1]練習次數\n'
                        '[2]練習天數\n'
                        '[3]不同曲目數\n'
                        '[4]連續練習天數\n'
                        '[5]累積上傳次數\n'
                        '[6]間隔一段時間後再次練習\n'
                        '：'
                        )
                        if choice == '1':
                            change_content = 'PRACTICE_COUNT'
                            condition_value = int(input('需要練習幾次：'))
                            break
                        elif choice == '2':
                            change_content = 'PRACTICE_DAYS'
                            condition_value = int(input('需要練習幾天：'))
                            break
                        elif choice == '3':
                            change_content = 'DISTINCT_SONGS'
                            condition_value = int(input('需要練習幾首不同曲目：'))
                            break
                        elif choice == '4':
                            change_content = 'CONSECUTIVE_DAYS'
                            condition_value = int(input('需要連續練習幾天：'))
                            break
                        elif choice == '5':
                            change_content = 'TOTAL_UPLOADS'
                            condition_value = int(input('需要練習幾次：'))
                            break
                        elif choice == '6':
                            change_content = 'RETURN_AFTER_GAP'
                            condition_value = int(input('幾天沒上傳會觸發任務：'))
                            break
                        else:
                            print('輸入錯誤')
                    sql = """
                    UPDATE quest_list
                    SET condition_type = %s,
                        condition_value = %s
                    WHERE quest_id = %s
                    """

                    result = db.execute(sql,(change_content, condition_value, quest_id))
                    if result > 0:
                        return '修改成功'
                    return '修改失敗'
                
                elif change_type == 'condition_value':
                    sql = """
                    SELECT condition_type FROM quest_list WHERE quest_id = %s;
                    """
                    result = db.query_one(sql, (quest_id,))
                    while True:
                        if result['condition_type'] == 'PRACTICE_COUNT':
                            change_content = int(input('需要練習幾次：'))
                            break
                        elif result['condition_type'] == 'PRACTICE_DAYS':
                            change_content = int(input('需要練習幾天：'))
                            break
                        elif result['condition_type'] == 'DISTINCT_SONGS':
                            change_content = int(input('需要練習幾首不同曲目：'))
                            break
                        elif result['condition_type'] == 'CONSECUTIVE_DAYS':
                            change_content = int(input('需要連續練習幾天：'))
                            break
                        elif result['condition_type'] == 'TOTAL_UPLOADS':
                            change_content = int(input('需要練習幾次：'))
                            break
                        elif result['condition_type'] == 'RETURN_AFTER_GAP':
                            change_content = int(input('幾天沒上傳會觸發任務：'))
                            break
                        else:
                            print('讀取失敗')
                            break

                elif change_type == 'reward_xp' or change_type == 'reward_coin':
                    change_content = int(input('新數值:'))
                    
                elif change_type == 'is_repeatable':
                    while True:
                        choice = input('[1]是 [2]否:')
                        if choice == '1':
                            change_content = 1
                            break
                        elif choice == '2':
                            change_content = 0
                            break
                        else:
                            print('輸入錯誤')


                sql = f"""
                UPDATE quest_list
                SET {change_type} = %s
                WHERE quest_id = %s;
                """
                result = db.execute(sql, (change_content,quest_id,))
                if result > 0:
                    return '修改成功'
            else:
                print('輸入錯誤')

# ======================================================
# 指派任務
# ======================================================
def assign_quest(teacher):
    quest_type_text = {
        'DAILY': '每日任務',
        'WEEKLY': '每週任務',
        'HIDDEN': '隱藏任務'
    }

    # 只取老師自己且啟用中的任務
    sql = """
    SELECT quest_id, quest_name, quest_type, reward_xp, reward_coin
    FROM quest_list
    WHERE teacher_id = %s
    AND is_active = TRUE;
    """
    quest_result = db.query_all(sql, (teacher['teacher_id'],))
    if not quest_result:
        return '沒有可指派的任務'

    quest_dict = {}
    i = 1
    for quest in quest_result:
        quest_dict[f'{i}'] = quest
        i += 1

    # 只取老師自己的學生
    sql = """
    SELECT student_id, username, student_name
    FROM student
    WHERE teacher_id = %s;
    """
    student_result = db.query_all(sql, (teacher['teacher_id'],))
    if not student_result:
        return '沒有學生資料'

    student_dict = {}
    i = 1
    for student in student_result:
        student_dict[f'{i}'] = student
        i += 1

    while True:
        print('===== 要指派哪一項任務 =====')
        for i in range(1,len(quest_dict)+1):
            quest = quest_dict[str(i)]
            print(f"[{i}] {quest['quest_name']} | {quest_type_text[quest['quest_type']]} | 經驗 {quest['reward_xp']} | 金幣 {quest['reward_coin']}")

        choice = input('[0]取消\n:')
        if choice == '0':
            return '已取消指派'
        elif choice not in quest_dict:
            print('輸入錯誤')
            continue
        select_quest = quest_dict[choice]

        while True:
            print('===== 要指派給哪一位學生 =====')
            for i in range(1,len(student_dict)+1):
                student = student_dict[str(i)]
                print(f"[{i}] {student['student_name']} | {student['username']}")

            choice = input('[0]返回\n:')
            if choice == '0':
                break
            elif choice not in student_dict:
                print('輸入錯誤')
                continue
            select_student = student_dict[choice]

            # 計算指派時間、到期時間與任務期間
            assigned_at = datetime.now()
            if select_quest['quest_type'] == 'HIDDEN':
                expires_at = None
                expires_at_text = '無期限'
                period_key = 'ONCE'
            elif select_quest['quest_type'] == 'DAILY':
                expires_at = assigned_at + timedelta(days=1)
                expires_at_text = expires_at.strftime('%Y-%m-%d %H:%M')
                period_key = assigned_at.strftime('%Y-%m-%d')
            else:
                expires_at = assigned_at + timedelta(days=7)
                expires_at_text = expires_at.strftime('%Y-%m-%d %H:%M')
                iso = assigned_at.isocalendar()
                period_key = f'{iso.year}-W{iso.week:02d}'

            # 同一期間不可重複指派
            sql = """
            SELECT student_quest_id
            FROM student_quest
            WHERE student_id = %s
            AND quest_id = %s
            AND period_key = %s;
            """
            exist = db.query_one(
                sql,
                (
                    select_student['student_id'],
                    select_quest['quest_id'],
                    period_key
                )
            )
            if exist:
                print(f"學生 {select_student['student_name']} 在期間 {period_key} 已被指派任務 {select_quest['quest_name']}")
                continue

            print(
            '\n===== 指派內容確認 =====\n'
            f"任務名稱：{select_quest['quest_name']}\n"
            f"任務類型：{quest_type_text[select_quest['quest_type']]}\n"
            f"指派學生：{select_student['student_name']}\n"
            f"指派時間：{assigned_at.strftime('%Y-%m-%d %H:%M')}\n"
            f'到期時間：{expires_at_text}\n'
            f'任務期間：{period_key}\n'
            )
            while True:
                choice = input('是否指派\n[1]是 [2]否：')
                if choice == '1':
                    sql = """
                    INSERT INTO student_quest (
                    student_id,
                    quest_id,
                    assigned_at,
                    expires_at,
                    period_key
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    result = db.execute(
                        sql,
                        (
                            select_student['student_id'],
                            select_quest['quest_id'],
                            assigned_at,
                            expires_at,
                            period_key
                        )
                    )
                    if result > 0:
                        return '任務指派成功'
                    return '任務指派失敗'
                elif choice == '2':
                    break
                else:
                    print('輸入錯誤')











# ======================================================
# 刪除任務
# ======================================================
def delete_quest(teacher):
    result = teacher_show_quest(teacher)
    if isinstance(result, str):
        return result
    menu_dict = {}
    i = 1
    for quest in result:
        menu_dict[f'{i}'] = {
            'quest_id': quest['任務編號'],
            'quest_name': quest['任務名稱']
        }
        i += 1
    while True:
        print('===== 需要刪除哪一項任務 =====')
        for i in range(1,len(menu_dict)+1):
            print(f'[{i}] {menu_dict[str(i)]['quest_name']}')

        choice = input('[0]取消\n:')
        if choice == '0':
            return '已取消刪除'
        elif choice in menu_dict:
            select_quest = menu_dict[choice]
            change_quest = select_quest['quest_name']
            quest_id = select_quest['quest_id']
            while True:
                print(f'確定要刪除任務:{change_quest} ?')
                choice = input('[1]是 [2]否')
                if choice == '1':
                    sql = """
                    DELETE FROM quest_list WHERE quest_id = %s
                    """
                    result = db.execute(sql, (quest_id,))
                    if result > 0:
                        return '已刪除任務'
                    return '刪除失敗'
                elif choice == '2':
                    break
                else:
                    print('輸入錯誤')
        else:
            print('輸入錯誤')

# ======================================================
# 啟用/停用任務
# ======================================================
def stop_quest(teacher):
    result = teacher_show_quest(teacher)
    if isinstance(result, str):
        return result
    menu_dict = {}
    i = 1
    for quest in result:
        menu_dict[f'{i}'] = {
            'quest_id': quest['任務編號'],
            'quest_name': quest['任務名稱'],
            'is_active': quest['任務是否啟用']
        }
        i += 1
    while True:
        print('===== 需要停用/啟用哪一項任務 =====')
        for i in range(1,len(menu_dict)+1):
            quest = menu_dict[str(i)]
            if quest['is_active'] == 1:
                status = '啟用中'
            else:
                status = '停用中'
            print(f"[{i}] {quest['quest_name']} | {status}")

        choice = input('[0]取消\n:')
        if choice == '0':
            return '已取消變更'
        elif choice in menu_dict:
            select_quest = menu_dict[choice]
            change_quest = select_quest['quest_name']
            quest_id = select_quest['quest_id']
            if select_quest['is_active'] == 1:
                status = '啟用中'
            else:
                status = '停用中'
            while True:
                print(f'任務 [{change_quest}] 現在是{status}狀態\n是否變更 ?')
                choice = input('[1]是 [2]否')
                if choice == '1':
                    if select_quest['is_active'] == 1:
                        change_active = 0
                    else:
                        change_active = 1
                    sql = """
                    UPDATE quest_list SET is_active = %s WHERE quest_id = %s
                    """
                    result = db.execute(sql, (change_active, quest_id,))
                    if result > 0:
                        return '已變更狀態'
                    return '變更失敗'
                elif choice == '2':
                    break
                else:
                    print('輸入錯誤')
        else:
            print('輸入錯誤')
    

# ======================================================
# 任務介面
# ======================================================
def quest_menu(teacher):
    while True:
        choice = input(
            '\n======== 任務管理 ========\n'
            '[1]查看任務\n'
            '[2]指派任務\n'
            '[3]新增任務\n'
            '[4]停用/啟用任務\n'
            '[5]刪除任務\n'
            '[6]修改任務\n'
            '[0]返回\n'
            ':'
        )
        if choice == '1':
            quest = teacher_show_quest(teacher)
            print(quest)
        elif choice == '2':
            result = assign_quest(teacher)
            print(result)
        
        elif choice == '3':
            result = create_quest(teacher)
            print(result)

        elif choice == '4':
            result = stop_quest(teacher)
            print(result)

        elif choice == '5':
            result = delete_quest(teacher)
            print(result)

        elif choice == '6':
            result = update_quest(teacher)
            print(result)

        elif choice == '0':
            print('返回')
            break

        else:
            print('輸入錯誤')



