import os # 檢查檔案是否存在
import shutil # 複製檔案
from datetime import datetime
from db import SqlUtils

db = SqlUtils()

AUDIO_FOLDER = 'uploads/audio' # 音檔存放路徑


# ======================================================
# 儲存音檔並回傳存放路徑
# ======================================================
def save_audio_file(student, source_path):
    os.makedirs(AUDIO_FOLDER, exist_ok=True)
    file_ext = os.path.splitext(source_path)[1]
    file_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"{student['student_id']}_{file_time}{file_ext}"
    audio_url = f'{AUDIO_FOLDER}/{file_name}'
    shutil.copy(source_path, audio_url)
    return audio_url


# ======================================================
# 建立練習錄音紀錄
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
    rowcount = db.execute(
        sql,
        (
            student['student_id'],
            audio_url,
            song_name,
            audio_duration
        )
    )
    if rowcount > 0:
        return '練習上傳成功'
    return '練習上傳失敗'


# ======================================================
# 上傳練習
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
        return create_practice_upload(student, audio_url, song_name, int(audio_duration))
