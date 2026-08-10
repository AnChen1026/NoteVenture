"""
api/quests.py｜任務模板與指派

- 老師 Streamlit：列表／建立／指派 → quest_service
- 學生 HTML：查看自己的指派 → student_show_quest
建立／指派時部分 SQL 寫在本檔（與 Console 時期流程對齊）；查詢多走 service。
"""

from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from db import SqlUtils
from api.guards import get_login_teacher, get_login_student, json_safe
from services.quest_service import teacher_show_quest, student_show_quest

quests_bp = Blueprint('quests', __name__)
db = SqlUtils()

QUEST_TYPES = {'DAILY', 'WEEKLY', 'HIDDEN'}
CONDITION_TYPES = {
    'PRACTICE_COUNT',
    'PRACTICE_DAYS',
    'DISTINCT_SONGS',
    'CONSECUTIVE_DAYS',
    'TOTAL_UPLOADS',
    'RETURN_AFTER_GAP'
}


# ======================================================
# 老師查看自己的任務清單
# ======================================================
@quests_bp.get('/api/quests')
def api_list_quests():
    teacher, error = get_login_teacher()
    if error:
        return error

    result = teacher_show_quest(teacher)
    if isinstance(result, str):
        return jsonify({'message': result, 'data': []})
    return jsonify({'data': json_safe(result)})


# ======================================================
# 老師建立任務
# ======================================================
@quests_bp.post('/api/quests')
def api_create_quest():
    teacher, error = get_login_teacher()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    quest_name = str(data.get('quest_name', '')).strip()
    quest_type = data.get('quest_type')
    condition_type = data.get('condition_type')
    condition_value = data.get('condition_value')
    reward_xp = data.get('reward_xp', 0)
    reward_coin = data.get('reward_coin', 0)
    is_repeatable = data.get('is_repeatable', True)

    if quest_name == '':
        return jsonify({'message': '請輸入任務名稱'}), 400
    if quest_type not in QUEST_TYPES:
        return jsonify({'message': '任務類型不正確'}), 400
    if condition_type not in CONDITION_TYPES:
        return jsonify({'message': '任務條件類型不正確'}), 400
    if not isinstance(condition_value, int) or condition_value <= 0:
        return jsonify({'message': '條件數值請輸入正整數'}), 400
    if not isinstance(reward_xp, int) or reward_xp < 0:
        return jsonify({'message': '獎勵經驗請輸入非負整數'}), 400
    if not isinstance(reward_coin, int) or reward_coin < 0:
        return jsonify({'message': '獎勵金幣請輸入非負整數'}), 400

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
    rowcount = db.execute(
        sql,
        (
            teacher['teacher_id'],
            quest_name,
            quest_type,
            condition_type,
            condition_value,
            reward_xp,
            reward_coin,
            bool(is_repeatable)
        )
    )
    if rowcount > 0:
        return jsonify({'message': '任務新建成功'}), 201
    return jsonify({'message': '任務建立失敗'}), 500


# ======================================================
# 老師指派任務給學生
# ======================================================
@quests_bp.post('/api/quests/<int:quest_id>/assign')
def api_assign_quest(quest_id):
    teacher, error = get_login_teacher()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    student_id = data.get('student_id')
    if not isinstance(student_id, int):
        return jsonify({'message': '請提供學生編號 student_id'}), 400

    # 只能指派自己啟用中的任務
    quest = db.query_one(
        """
        SELECT quest_id, quest_name, quest_type
        FROM quest_list
        WHERE quest_id = %s
        AND teacher_id = %s
        AND is_active = TRUE;
        """,
        (quest_id, teacher['teacher_id'])
    )
    if not quest:
        return jsonify({'message': '查無此任務或任務未啟用'}), 404

    # 只能指派給自己的學生
    student = db.query_one(
        """
        SELECT student_id, student_name
        FROM student
        WHERE student_id = %s
        AND teacher_id = %s;
        """,
        (student_id, teacher['teacher_id'])
    )
    if not student:
        return jsonify({'message': '查無此學生'}), 404

    assigned_at = datetime.now()
    if quest['quest_type'] == 'HIDDEN':
        expires_at = None
        period_key = 'ONCE'
    elif quest['quest_type'] == 'DAILY':
        expires_at = assigned_at + timedelta(days=1)
        period_key = assigned_at.strftime('%Y-%m-%d')
    else:
        expires_at = assigned_at + timedelta(days=7)
        iso = assigned_at.isocalendar()
        period_key = f'{iso.year}-W{iso.week:02d}'

    exist = db.query_one(
        """
        SELECT student_quest_id
        FROM student_quest
        WHERE student_id = %s
        AND quest_id = %s
        AND period_key = %s;
        """,
        (student_id, quest_id, period_key)
    )
    if exist:
        return jsonify({'message': f'此期間已指派過該任務（{period_key}）'}), 409

    rowcount = db.execute(
        """
        INSERT INTO student_quest (
        student_id,
        quest_id,
        assigned_at,
        expires_at,
        period_key
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (student_id, quest_id, assigned_at, expires_at, period_key)
    )
    if rowcount > 0:
        return jsonify({
            'message': '任務指派成功',
            'period_key': period_key,
            'assigned_at': json_safe(assigned_at),
            'expires_at': json_safe(expires_at)
        }), 201
    return jsonify({'message': '任務指派失敗'}), 500


# ======================================================
# 學生查看自己的任務
# ======================================================
@quests_bp.get('/api/students/<int:student_id>/quests')
def api_student_quests(student_id):
    student, error = get_login_student()
    if error:
        return error
    if student['student_id'] != student_id:
        return jsonify({'message': '只能查看自己的任務'}), 403

    result = student_show_quest(student)
    if isinstance(result, str):
        return jsonify({'message': result, 'data': []})
    return jsonify({'data': json_safe(result)})
