from db import SqlUtils
from services.pet_service import show_pet

db = SqlUtils()


# ======================================================
# 查詢單一 COUNT 結果
# ======================================================
def _count(sql, params):
    row = db.query_one(sql, params)
    if not row:
        return 0
    return int(row['cnt'])


# ======================================================
# 老師 Dashboard：彙總數字與近期清單
# ======================================================
def get_teacher_dashboard(teacher):
    teacher_id = teacher['teacher_id']

    student_count = _count(
        """
        SELECT COUNT(*) AS cnt
        FROM student
        WHERE teacher_id = %s;
        """,
        (teacher_id,)
    )

    active_quest_count = _count(
        """
        SELECT COUNT(*) AS cnt
        FROM quest_list
        WHERE teacher_id = %s
        AND is_active = TRUE;
        """,
        (teacher_id,)
    )

    # 進行中：未完成，且尚未到期（無期限也算進行中）
    active_assignment_count = _count(
        """
        SELECT COUNT(*) AS cnt
        FROM student_quest sq
        JOIN student s ON s.student_id = sq.student_id
        WHERE s.teacher_id = %s
        AND sq.completed = FALSE
        AND (sq.expires_at IS NULL OR sq.expires_at > NOW());
        """,
        (teacher_id,)
    )

    expired_assignment_count = _count(
        """
        SELECT COUNT(*) AS cnt
        FROM student_quest sq
        JOIN student s ON s.student_id = sq.student_id
        WHERE s.teacher_id = %s
        AND sq.completed = FALSE
        AND sq.expires_at IS NOT NULL
        AND sq.expires_at <= NOW();
        """,
        (teacher_id,)
    )

    upload_count_7d = _count(
        """
        SELECT COUNT(*) AS cnt
        FROM practice_upload p
        JOIN student s ON s.student_id = p.student_id
        WHERE s.teacher_id = %s
        AND p.created_at >= (NOW() - INTERVAL 7 DAY);
        """,
        (teacher_id,)
    )

    pending_redeem_count = _count(
        """
        SELECT COUNT(*) AS cnt
        FROM purchase_record p
        JOIN student s ON s.student_id = p.student_id
        WHERE s.teacher_id = %s
        AND p.status = 'PURCHASED';
        """,
        (teacher_id,)
    )

    students = db.query_all(
        """
        SELECT
            student_id AS 序號,
            username AS 帳號,
            student_name AS 姓名,
            total_xp AS 經驗值,
            total_coin AS 金幣數
        FROM student
        WHERE teacher_id = %s
        ORDER BY student_id;
        """,
        (teacher_id,)
    ) or []

    recent_uploads = db.query_all(
        """
        SELECT
            s.student_name AS 學生,
            p.song_name AS 曲目,
            p.audio_duration AS 秒數,
            p.created_at AS 上傳時間
        FROM practice_upload p
        JOIN student s ON s.student_id = p.student_id
        WHERE s.teacher_id = %s
        ORDER BY p.created_at DESC
        LIMIT 10;
        """,
        (teacher_id,)
    ) or []

    active_assignments = db.query_all(
        """
        SELECT
            s.student_name AS 學生,
            q.quest_name AS 任務,
            sq.progress_value AS 目前進度,
            q.condition_value AS 目標,
            sq.expires_at AS 截止時間
        FROM student_quest sq
        JOIN student s ON s.student_id = sq.student_id
        JOIN quest_list q ON q.quest_id = sq.quest_id
        WHERE s.teacher_id = %s
        AND sq.completed = FALSE
        AND (sq.expires_at IS NULL OR sq.expires_at > NOW())
        ORDER BY sq.expires_at IS NULL, sq.expires_at, sq.student_quest_id
        LIMIT 10;
        """,
        (teacher_id,)
    ) or []

    pending_redeems = db.query_all(
        """
        SELECT
            s.student_name AS 學生,
            i.item_name AS 商品,
            p.price AS 價格,
            p.created_at AS 購買時間
        FROM purchase_record p
        JOIN student s ON s.student_id = p.student_id
        JOIN shop_item i ON i.item_id = p.item_id
        WHERE s.teacher_id = %s
        AND p.status = 'PURCHASED'
        ORDER BY p.created_at
        LIMIT 10;
        """,
        (teacher_id,)
    ) or []

    return {
        'summary': {
            'student_count': student_count,
            'active_quest_count': active_quest_count,
            'active_assignment_count': active_assignment_count,
            'expired_assignment_count': expired_assignment_count,
            'upload_count_7d': upload_count_7d,
            'pending_redeem_count': pending_redeem_count
        },
        'students': students,
        'recent_uploads': recent_uploads,
        'active_assignments': active_assignments,
        'pending_redeems': pending_redeems
    }


# ======================================================
# 學生 Dashboard：彙總數字、寵物與近期清單
# ======================================================
def get_student_dashboard(student):
    student_id = student['student_id']

    profile = db.query_one(
        """
        SELECT student_name, total_xp, total_coin
        FROM student
        WHERE student_id = %s;
        """,
        (student_id,)
    )
    if not profile:
        return None

    active_assignment_count = _count(
        """
        SELECT COUNT(*) AS cnt
        FROM student_quest sq
        JOIN quest_list q ON q.quest_id = sq.quest_id
        WHERE sq.student_id = %s
        AND sq.completed = FALSE
        AND (sq.expires_at IS NULL OR sq.expires_at > NOW())
        AND q.quest_type != 'HIDDEN';
        """,
        (student_id,)
    )

    # HIDDEN 未完成不顯示，與學生任務列表一致
    expired_assignment_count = _count(
        """
        SELECT COUNT(*) AS cnt
        FROM student_quest sq
        JOIN quest_list q ON q.quest_id = sq.quest_id
        WHERE sq.student_id = %s
        AND sq.completed = FALSE
        AND sq.expires_at IS NOT NULL
        AND sq.expires_at <= NOW()
        AND q.quest_type != 'HIDDEN';
        """,
        (student_id,)
    )

    completed_assignment_count = _count(
        """
        SELECT COUNT(*) AS cnt
        FROM student_quest
        WHERE student_id = %s
        AND completed = TRUE;
        """,
        (student_id,)
    )

    upload_count_7d = _count(
        """
        SELECT COUNT(*) AS cnt
        FROM practice_upload
        WHERE student_id = %s
        AND created_at >= (NOW() - INTERVAL 7 DAY);
        """,
        (student_id,)
    )

    pending_purchase_count = _count(
        """
        SELECT COUNT(*) AS cnt
        FROM purchase_record
        WHERE student_id = %s
        AND status = 'PURCHASED';
        """,
        (student_id,)
    )

    pet = show_pet(student)
    if isinstance(pet, str):
        pet = None

    active_assignments = db.query_all(
        """
        SELECT
            q.quest_name AS 任務,
            q.quest_type AS 任務類型,
            sq.progress_value AS 目前進度,
            q.condition_value AS 目標,
            sq.expires_at AS 截止時間
        FROM student_quest sq
        JOIN quest_list q ON q.quest_id = sq.quest_id
        WHERE sq.student_id = %s
        AND sq.completed = FALSE
        AND (sq.expires_at IS NULL OR sq.expires_at > NOW())
        AND q.quest_type != 'HIDDEN'
        ORDER BY sq.expires_at IS NULL, sq.expires_at, sq.student_quest_id
        LIMIT 10;
        """,
        (student_id,)
    ) or []

    recent_uploads = db.query_all(
        """
        SELECT
            song_name AS 曲目,
            audio_duration AS 秒數,
            created_at AS 上傳時間
        FROM practice_upload
        WHERE student_id = %s
        ORDER BY created_at DESC
        LIMIT 10;
        """,
        (student_id,)
    ) or []

    recent_purchases = db.query_all(
        """
        SELECT
            i.item_name AS 商品,
            p.price AS 價格,
            p.status AS 狀態,
            p.created_at AS 購買時間
        FROM purchase_record p
        JOIN shop_item i ON i.item_id = p.item_id
        WHERE p.student_id = %s
        ORDER BY p.created_at DESC
        LIMIT 10;
        """,
        (student_id,)
    ) or []

    return {
        'summary': {
            'student_name': profile['student_name'],
            'total_xp': profile['total_xp'],
            'total_coin': profile['total_coin'],
            'active_assignment_count': active_assignment_count,
            'expired_assignment_count': expired_assignment_count,
            'completed_assignment_count': completed_assignment_count,
            'upload_count_7d': upload_count_7d,
            'pending_purchase_count': pending_purchase_count
        },
        'pet': pet,
        'active_assignments': active_assignments,
        'recent_uploads': recent_uploads,
        'recent_purchases': recent_purchases
    }


# ======================================================
# 時間顯示文字（Console 用）
# ======================================================
def _format_datetime(value):
    if value is None:
        return '無期限'
    if hasattr(value, 'strftime'):
        return value.strftime('%Y-%m-%d %H:%M')
    text = str(value)
    return text[:16] if len(text) >= 16 else text


# ======================================================
# 列印指定行數清單（Console 用）
# ======================================================
def _print_rows(title, rows, empty_message, parmas=10):
    print(f'\n--- {title} ---')
    if not rows:
        print(empty_message)
        return
    i = 1
    for row in rows:
        parts = []
        for key, value in row.items():
            if key.endswith('時間') or key == '截止時間':
                value = _format_datetime(value)
            parts.append(f'{key}:{value}')
        print(' | '.join(parts))
        i += 1
        if i > parmas:
            break


# ======================================================
# 老師主頁面（Console 顯示）
# ======================================================
def show_teacher_dashboard(teacher):
    data = get_teacher_dashboard(teacher)
    summary = data['summary']

    print('\n======== 老師總覽 ========')
    print(f"學生人數：{summary['student_count']}")
    print(f"啟用中任務模板：{summary['active_quest_count']}")
    print(f"進行中指派：{summary['active_assignment_count']}")
    print(f"已過期指派：{summary['expired_assignment_count']}")
    print(f"近 7 天上傳：{summary['upload_count_7d']}")
    print(f"待兌換商品：{summary['pending_redeem_count']}")

    _print_rows('學生概況', data['students'], '尚無學生')

    print('\n--- 進行中任務（最近 5 筆） ---')
    if not data['active_assignments']:
        print('目前沒有進行中的任務指派')
    else:
        i = 1
        for item in data['active_assignments']:
            progress = f"{item.get('目前進度', 0)} / {item.get('目標', 0)}"
            expires = _format_datetime(item.get('截止時間'))
            print(
                f"學生:{item.get('學生')} | 任務:{item.get('任務')} | "
                f"進度:{progress} | 截止時間:{expires}"
            )
            i += 1
            if i > 5:
                break

    _print_rows('最近上傳（最近 5 筆）', data['recent_uploads'], '尚無上傳紀錄', 5)
    _print_rows('待兌換商品（最近 5 筆）', data['pending_redeems'], '目前沒有待兌換商品', 5)
    return '總覽顯示完成'


# ======================================================
# 學生主頁（Console 顯示）
# ======================================================
def show_student_dashboard(student):
    data = get_student_dashboard(student)
    if not data:
        return '找不到學生資料'

    summary = data['summary']
    print('\n======== 學生主頁 ========')
    print(f"姓名：{summary['student_name']}")
    print(f"經驗值：{summary['total_xp']}")
    print(f"金幣：{summary['total_coin']}")
    print(f"進行中任務：{summary['active_assignment_count']}")
    print(f"已過期任務：{summary['expired_assignment_count']}")
    print(f"已完成任務：{summary['completed_assignment_count']}")
    print(f"近 7 天上傳：{summary['upload_count_7d']}")
    print(f"待領取實體商品：{summary['pending_purchase_count']}")

    pet = data['pet']
    print('\n--- 我的寵物 ---')
    if not pet:
        print('無寵物資料')
    else:
        print(f"寵物階段：{pet['stage_name']}")
        print(f"經驗值：{pet['total_xp']}")
        if pet['next_stage_name'] is None:
            print('已達最終階段')
        else:
            print(f"下一階段：{pet['next_stage_name']}")
            print(f"還需經驗值：{pet['xp_to_next']}")

    print('\n--- 進行中任務（最近 5 筆） ---')
    if not data['active_assignments']:
        print('目前沒有進行中的任務')
    else:
        i = 1
        for item in data['active_assignments']:
            progress = f"{item.get('目前進度', 0)} / {item.get('目標', 0)}"
            expires = _format_datetime(item.get('截止時間'))
            print(
                f"任務:{item.get('任務')} | 進度:{progress} | 截止時間:{expires}"
            )
            i += 1
            if i > 5:
                break

    _print_rows('最近上傳（最近 5 筆）', data['recent_uploads'], '尚無上傳紀錄', 5)
    _print_rows('最近購買（最近 5 筆）', data['recent_purchases'], '尚無購買紀錄', 5)
    return '主頁顯示完成'
