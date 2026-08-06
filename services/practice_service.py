import os # 檢查檔案是否存在
import shutil # 複製檔案
from datetime import datetime
from db import SqlUtils
from services.quest_service import update_quest_progress
from services.reward_service import give_quest_rewards

db = SqlUtils()

AUDIO_FOLDER = 'uploads/audio' # 音檔存放路徑


# ======================================================
# 儲存音檔並回傳存放路徑
# ======================================================
def save_audio_file(student, source_path):
    os.makedirs(AUDIO_FOLDER, exist_ok=True) # 建立音檔存放路徑
    file_ext = os.path.splitext(source_path)[1] # 檔案副檔名
    file_time = datetime.now().strftime('%Y%m%d_%H%M%S') # 檔案時間
    file_name = f"{student['student_id']}_{file_time}{file_ext}" # 檔案名稱
    audio_url = f'{AUDIO_FOLDER}/{file_name}'
    shutil.copy(source_path, audio_url) # 複製檔案
    return audio_url # 回傳檔案路徑


# ======================================================
# 建立練習錄音紀錄至資料庫
# ======================================================
def create_practice_upload(student, audio_url, song_name, audio_duration):
    sql = """
    INSERT INTO practice_upload (
    student_id,
    audio_url,
    song_name,
    audio_duration
    )
    VALUES (%s, %s, %s, %s)
    """
    rowcount = db.execute(sql,(student['student_id'],audio_url,song_name,audio_duration))
    if rowcount > 0:
        return '練習上傳成功'
    return '練習上傳失敗'


# ======================================================
# 顯示指定學生或全部學生的上傳紀錄
# ======================================================
def teacher_show_practice_upload(teacher, student_id=None):
    sql = """
    SELECT s.student_name, p.song_name, p.audio_duration, p.audio_url, p.created_at
    FROM practice_upload p
    JOIN student s ON s.student_id = p.student_id
    WHERE s.teacher_id = %s
    """
    params = [teacher['teacher_id']]
    if student_id:
        sql += ' AND p.student_id = %s'
        params.append(student_id)
    sql += ' ORDER BY p.created_at DESC;'

    result = db.query_all(sql, params)
    if result:
        return result
    return '無上傳紀錄'


# ======================================================
# 老師選擇查看指定學生或全部學生的上傳紀錄
# ======================================================
def practice_upload_menu(teacher):
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
    all_choice = f'{i}'

    while True:
        print('\n===== 要查看哪一位學生的上傳紀錄 =====')
        for i in range(1,len(student_dict)+1):
            student = student_dict[str(i)]
            print(f"[{i}] {student['student_name']}")
        print(f'[{all_choice}] 全部學生')

        choice = input('[0]返回\n:')
        if choice == '0':
            return '返回'
        elif choice == all_choice:
            title = '全部學生上傳紀錄'
            result = teacher_show_practice_upload(teacher)
        elif choice in student_dict:
            select_student = student_dict[choice]
            title = f"{select_student['student_name']} 的上傳紀錄"
            result = teacher_show_practice_upload(teacher, select_student['student_id'])
        else:
            print('輸入錯誤')
            continue

        if isinstance(result, str):
            print(result)
            continue

        print(f'\n======== {title} ========')
        for upload in result:
            print()
            print(f"學生：{upload['student_name']}")
            print(f"曲目：{upload['song_name']}")
            print(f"長度：{upload['audio_duration']} 秒")
            print(f"時間：{upload['created_at'].strftime('%Y-%m-%d %H:%M')}")
            print(f"檔案：{upload['audio_url']}")


# ======================================================
# 上傳練習 自行測試輸入用
# ======================================================
def upload_practice(student):
    while True:
        song_name = input('請輸入曲目名稱([0]返回)：')
        if song_name == '0':
            return '已取消上傳'
        elif song_name == '':
            print('曲目名稱不可空白')
            continue

        # Windows 複製檔案路徑時會帶雙引號
        source_path = input('請輸入音檔路徑([0]返回)：').strip('"')
        if source_path == '0':
            return '已取消上傳'
        elif not os.path.isfile(source_path):
            print('找不到音檔')
            continue

        audio_duration = input('請輸入錄音秒數([0]返回)：')
        if audio_duration == '0':
            return '已取消上傳'
        elif not audio_duration.isdigit():
            print('錄音秒數請輸入數字')
            continue

        audio_url = save_audio_file(student, source_path)
        result = create_practice_upload(student, audio_url, song_name, int(audio_duration))
        if result == '練習上傳成功':
            # 上傳成功後更新任務進度，達標的任務發放獎勵
            progress_list = update_quest_progress(student)
            for quest in progress_list:
                print(f"{quest['quest_name']}：{quest['progress_value']} / {quest['condition_value']}")
            for reward in give_quest_rewards(progress_list):
                print(f"任務完成 {reward['quest_name']}，獲得 {reward['reward_xp']} 經驗值、{reward['reward_coin']} 金幣")
        return result
