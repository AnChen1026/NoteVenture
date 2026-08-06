from db import SqlUtils

db = SqlUtils()

# ======================================================
# 發放單筆任務獎勵
# ======================================================
def give_quest_reward(student_quest_id):
    # 只取未完成的任務，已發過獎的任務查不到，避免重複發獎
    sql = """
    SELECT sq.student_id, sq.progress_value,
           q.quest_name, q.quest_type, q.condition_value, q.reward_xp, q.reward_coin
    FROM student_quest sq
    JOIN quest_list q ON q.quest_id = sq.quest_id
    WHERE sq.student_quest_id = %s
    AND sq.completed = FALSE;
    """
    quest = db.query_one(sql, (student_quest_id,))
    if not quest:
        return None

    # 進度未達標不發獎
    if quest['progress_value'] < quest['condition_value']:
        return None

    if quest['quest_type'] == 'HIDDEN':
        source_type = 'HIDDEN_QUEST'
    else:
        source_type = 'QUEST_REWARD'

    complete_sql = """
    UPDATE student_quest
    SET completed = TRUE,
        completed_at = NOW()
    WHERE student_quest_id = %s
    AND completed = FALSE;
    """
    student_sql = """
    UPDATE student
    SET total_xp = total_xp + %s,
        total_coin = total_coin + %s
    WHERE student_id = %s;
    """
    sql_list = [
        (complete_sql, (student_quest_id,)),
        (student_sql, (quest['reward_xp'], quest['reward_coin'], quest['student_id']))
    ]

    # 獎勵為 0 就不留異動紀錄
    if quest['reward_xp'] > 0:
        xp_sql = """
        INSERT INTO xp_source (
        student_id,
        xp_amount,
        source_type
        )
        VALUES (%s, %s, %s)
        """
        sql_list.append((xp_sql, (quest['student_id'], quest['reward_xp'], source_type)))

    if quest['reward_coin'] > 0:
        coin_sql = """
        INSERT INTO coin_transaction (
        student_id,
        source_type,
        amount
        )
        VALUES (%s, %s, %s)
        """
        sql_list.append((coin_sql, (quest['student_id'], source_type, quest['reward_coin'])))

    # 四張表寫在同一個 transaction，失敗全部回復
    if db.execute_transaction(sql_list):
        return {
            'quest_name': quest['quest_name'],
            'reward_xp': quest['reward_xp'],
            'reward_coin': quest['reward_coin']
        }
    return None


# ======================================================
# 發放所有達標任務的獎勵
# ======================================================
def give_quest_rewards(progress_list):
    reward_list = []
    for quest in progress_list:
        if quest['progress_value'] >= quest['condition_value']:
            reward = give_quest_reward(quest['student_quest_id'])
            if reward:
                reward_list.append(reward)
    return reward_list
