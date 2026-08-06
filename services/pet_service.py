from db import SqlUtils

db = SqlUtils()

# ======================================================
# 依累積經驗值更新寵物階段，沒有寵物就建立
# ======================================================
def update_pet_stage(student_id):
    # 取門檻小於等於目前經驗值的最後一個階段
    sql = """
    SELECT ps.stage_id
    FROM student s
    JOIN pet_stage ps ON ps.xp_threshold <= s.total_xp
    WHERE s.student_id = %s
    ORDER BY ps.stage_order DESC
    LIMIT 1;
    """
    stage = db.query_one(sql, (student_id,))
    if not stage:
        return '無寵物階段資料'

    # 一位學生只有一隻寵物，pet.student_id 是 UNIQUE
    # 沒有寵物就新增，已有寵物就更新階段
    sql = """
    INSERT INTO pet (
    student_id,
    stage_id
    )
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE stage_id = %s
    """
    rowcount = db.execute(sql, (student_id, stage['stage_id'], stage['stage_id']))
    if rowcount > 0:
        return '寵物階段更新成功'
    return '寵物階段未變動'


# ======================================================
# 查看寵物目前階段與下一階段
# ======================================================
def show_pet(student):
    # 先確認寵物存在且階段正確
    update_pet_stage(student['student_id'])

    sql = """
    SELECT s.total_xp, ps.stage_name, ps.stage_order
    FROM pet p
    JOIN pet_stage ps ON ps.stage_id = p.stage_id
    JOIN student s ON s.student_id = p.student_id
    WHERE p.student_id = %s;
    """
    pet = db.query_one(sql, (student['student_id'],))
    if not pet:
        return '無寵物資料'

    # 下一個階段
    sql = """
    SELECT stage_name, xp_threshold
    FROM pet_stage
    WHERE stage_order > %s
    ORDER BY stage_order
    LIMIT 1;
    """
    next_stage = db.query_one(sql, (pet['stage_order'],))

    result = {
        'total_xp': pet['total_xp'],
        'stage_name': pet['stage_name'],
        'next_stage_name': None,
        'xp_to_next': None
    }
    # 已經是最終階段時沒有下一階段
    if next_stage:
        result['next_stage_name'] = next_stage['stage_name']
        result['xp_to_next'] = next_stage['xp_threshold'] - pet['total_xp']
    return result
