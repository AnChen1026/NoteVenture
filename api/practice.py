import os
import tempfile
import wave

from flask import Blueprint, request, jsonify, send_file
from api.guards import get_login_teacher, get_login_student, json_safe
from services.practice_service import (
    save_audio_file,
    create_practice_upload,
    teacher_show_practice_upload,
    get_teacher_practice_upload,
    resolve_audio_path,
)
from services.quest_service import update_quest_progress
from services.reward_service import give_quest_rewards
from services.student_service import get_student

practice_bp = Blueprint('practice', __name__)


# ======================================================
# 從 wav 錄音計算秒數
# ======================================================
def get_wav_duration(file_storage):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        file_storage.save(temp_file.name)
        temp_path = temp_file.name

    try:
        with wave.open(temp_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = int(frames / rate)
        return temp_path, duration
    except wave.Error:
        os.remove(temp_path)
        return None, None


# ======================================================
# 學生上傳練習錄音
# ======================================================
@practice_bp.post('/api/students/<int:student_id>/practice-uploads')
def api_create_practice_upload(student_id):
    student, error = get_login_student()
    if error:
        return error
    if student['student_id'] != student_id:
        return jsonify({'message': '只能替自己上傳練習'}), 403

    song_name = str(request.form.get('song_name', '')).strip()
    audio_file = request.files.get('audio')

    if song_name == '':
        return jsonify({'message': '請輸入曲目名稱'}), 400
    if audio_file is None or audio_file.filename == '':
        return jsonify({'message': '請上傳錄音檔'}), 400

    # 優先用 wav 自動算秒數；其他格式可帶 duration
    filename = audio_file.filename.lower()
    temp_path = None
    audio_duration = None

    if filename.endswith('.wav'):
        temp_path, audio_duration = get_wav_duration(audio_file)
        if temp_path is None:
            return jsonify({'message': '無法讀取 wav 錄音'}), 400
    else:
        duration_text = request.form.get('audio_duration', '')
        if not str(duration_text).isdigit() or int(duration_text) <= 0:
            return jsonify({'message': '非 wav 檔請提供錄音秒數 audio_duration'}), 400
        audio_duration = int(duration_text)
        file_ext = os.path.splitext(audio_file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            audio_file.save(temp_file.name)
            temp_path = temp_file.name

    try:
        audio_url = save_audio_file(student, temp_path)
        result = create_practice_upload(student, audio_url, song_name, audio_duration)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

    if result != '練習上傳成功':
        return jsonify({'message': result}), 500

    progress_list = update_quest_progress(student)
    reward_list = give_quest_rewards(progress_list)
    refreshed = get_student(student_id)

    return jsonify({
        'message': result,
        'audio_duration': audio_duration,
        'audio_url': audio_url,
        'progress': json_safe(progress_list),
        'rewards': json_safe(reward_list),
        'total_xp': refreshed['total_xp'] if refreshed else None,
        'total_coin': refreshed['total_coin'] if refreshed else None
    }), 201


# ======================================================
# 老師查看學生上傳紀錄
# ======================================================
@practice_bp.get('/api/practice-uploads')
def api_list_practice_uploads():
    teacher, error = get_login_teacher()
    if error:
        return error

    student_id = request.args.get('student_id', type=int)
    result = teacher_show_practice_upload(teacher, student_id)
    if isinstance(result, str):
        return jsonify({'message': result, 'data': []})
    return jsonify({'data': json_safe(result)})


# ======================================================
# 老師試聽單筆練習錄音
# ======================================================
@practice_bp.get('/api/practice-uploads/<int:upload_id>/audio')
def api_get_practice_upload_audio(upload_id):
    teacher, error = get_login_teacher()
    if error:
        return error

    upload = get_teacher_practice_upload(teacher, upload_id)
    if not upload:
        return jsonify({'message': '找不到上傳紀錄或無權限'}), 404

    audio_path = resolve_audio_path(upload['audio_url'])
    if audio_path is None:
        return jsonify({'message': '音檔不存在或路徑無效'}), 404

    # 依副檔名給瀏覽器／Streamlit 正確的 MIME
    ext = os.path.splitext(audio_path)[1].lower()
    mime_map = {
        '.wav': 'audio/wav',
        '.webm': 'audio/webm',
        '.mp3': 'audio/mpeg',
        '.ogg': 'audio/ogg',
        '.m4a': 'audio/mp4',
    }
    mimetype = mime_map.get(ext, 'application/octet-stream')
    return send_file(audio_path, mimetype=mimetype, conditional=True)
