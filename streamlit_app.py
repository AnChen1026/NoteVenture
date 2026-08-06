import os
import tempfile
import wave
from html import escape

import streamlit as st

from services.teacher_service import login_teacher
from services.student_service import login_student, show_student, create_student, get_student
from services.quest_service import teacher_show_quest, student_show_quest, update_quest_progress
from services.reward_service import give_quest_rewards
from services.practice_service import save_audio_file, create_practice_upload, teacher_show_practice_upload
from services.pet_service import show_pet
from services.shop_service import (
    item_type_text,
    teacher_show_shop_item,
    student_show_shop_item,
    purchase_item,
    teacher_show_pending_purchase,
    redeem_purchase
)

st.set_page_config(page_title='NoteAdventure', page_icon=':material/music_note:', layout='wide')

# ========= 顯示用中文對照 ===========
# 與 student_menu.py 相同，之後拆函式時會搬到共用位置

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

boolean_text = {
    0: '否',
    1: '是',
    False: '否',
    True: '是'
}

quest_active_text = {
    0: '已停用',
    1: '啟用中',
    False: '已停用',
    True: '啟用中'
}

shop_active_text = {
    0: '已下架',
    1: '上架中',
    False: '已下架',
    True: '上架中'
}

# 標題放在卡片內的頁面，避免外層大標題與置中卡片對不齊
FORM_PAGES = {'建立學生', '上傳練習'}

st.session_state.setdefault('user', None)
st.session_state.setdefault('role', None)
st.session_state.setdefault('flash', None)


# ======================================================
# 套用舊版 app.py 的網頁樣式
# ======================================================
def apply_custom_style():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f7f7f8;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            color: #1f2937;
            font-weight: 800;
        }

        /* 登入標題避免斷行 */
        .login-brand h1 {
            white-space: nowrap;
            font-size: 2.2rem;
            margin-bottom: 0.2rem;
        }

        p, label, div {
            color: #374151;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div {
            background-color: #ffffff !important;
            border: 1px solid #d1d5db !important;
            border-radius: 12px !important;
            box-shadow: none !important;
        }

        input, textarea {
            color: #111827 !important;
        }

        .stButton > button {
            background-color: #ffffff !important;
            color: #1f2937 !important;
            border: 1px solid #d1d5db !important;
            border-radius: 12px !important;
            padding: 0.45rem 1rem !important;
            font-weight: 600 !important;
            box-shadow: none !important;
        }

        .stButton > button:hover {
            border-color: #ff5a52 !important;
            color: #ff5a52 !important;
        }

        div[role="radiogroup"] label {
            margin-right: 1rem;
        }

        button[data-baseweb="tab"] {
            color: #6b7280 !important;
            font-weight: 600 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #ff5a52 !important;
            border-bottom: 2px solid #ff5a52 !important;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #d1d5db;
            border-radius: 14px;
            overflow: hidden;
            background: #ffffff;
        }

        div[data-testid="stVerticalBlock"] > div {
            gap: 0.65rem;
        }

        .custom-notice {
            background: #fff7f7;
            border: 1px solid #ffd6d3;
            border-left: 4px solid #ff5a52;
            border-radius: 12px;
            padding: 0.85rem 1rem;
            color: #374151;
            margin: 0.7rem 0;
            font-weight: 500;
        }

        .custom-card-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 0.5rem;
        }

        .muted-text {
            color: #6b7280;
            font-size: 0.95rem;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 16px;
            padding: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# ======================================================
# 置中卡片（沿用舊版版面）
# ======================================================
def centered_card(width_ratio=(1, 2.2, 1)):
    left, center, right = st.columns(width_ratio)
    return center.container(border=True)


# ======================================================
# 顯示提示訊息（沿用舊版紅色邊框樣式）
# ======================================================
def show_notice(message):
    safe_message = escape(str(message))
    st.markdown(
        f"""
        <div class="custom-notice">
            {safe_message}
        </div>
        """,
        unsafe_allow_html=True
    )


# ======================================================
# 任務清單轉成中文顯示用資料
# ======================================================
def format_quest_rows(quest_rows):
    display_rows = []
    for quest in quest_rows:
        display_rows.append({
            '任務編號': quest['任務編號'],
            '任務名稱': quest['任務名稱'],
            '任務類型': quest_type_text.get(quest['任務類型'], quest['任務類型']),
            '任務條件': condition_type_text.get(quest['任務條件類型'], quest['任務條件類型']),
            '條件數值': quest['任務條件數值'],
            '獎勵經驗': quest['獎勵經驗'],
            '獎勵金幣': quest['獎勵金幣'],
            '可重複': boolean_text.get(quest['是否為重複任務'], quest['是否為重複任務']),
            '啟用狀態': quest_active_text.get(quest['任務是否啟用'], quest['任務是否啟用'])
        })
    return display_rows


# ======================================================
# 上傳紀錄轉成中文顯示用資料
# ======================================================
def format_upload_rows(upload_rows):
    display_rows = []
    for upload in upload_rows:
        display_rows.append({
            '學生': upload['student_name'],
            '曲目': upload['song_name'],
            '秒數': upload['audio_duration'],
            '檔案路徑': upload['audio_url'],
            '上傳時間': upload['created_at'].strftime('%Y-%m-%d %H:%M')
        })
    return display_rows


# ======================================================
# 商品清單轉成中文顯示用資料
# ======================================================
def format_shop_rows(item_rows):
    display_rows = []
    for item in item_rows:
        if item['stock'] is None:
            stock_text = '不限量'
        else:
            stock_text = item['stock']

        if item['description']:
            description_text = item['description']
        else:
            description_text = '無'

        display_rows.append({
            '商品編號': item['item_id'],
            '商品名稱': item['item_name'],
            '商品類型': item_type_text.get(item['item_type'], item['item_type']),
            '價格': item['price'],
            '庫存': stock_text,
            '說明': description_text,
            '狀態': shop_active_text.get(item['is_active'], item['is_active'])
        })
    return display_rows


# ======================================================
# 從錄音檔計算秒數（st.audio_input 回傳 wav）
# ======================================================
def get_audio_duration(audio_file):
    audio_file.seek(0)
    with wave.open(audio_file, 'rb') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = int(frames / rate)
    audio_file.seek(0)
    return duration


apply_custom_style()


# ======================================================
# 登入頁
# ======================================================
if st.session_state.user is None:
    with centered_card():
        st.markdown('<div class="login-brand">', unsafe_allow_html=True)
        st.title('NoteAdventure')
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption('音樂練習 RPG 管理系統')

        teacher_tab, student_tab = st.tabs(['老師登入', '學生登入'])

        with teacher_tab:
            with st.form('teacher_login'):
                email = st.text_input('電子信箱')
                teacher_password = st.text_input('密碼', type='password')
                teacher_login = st.form_submit_button('登入')
            if teacher_login:
                teacher = login_teacher(email, teacher_password)
                if teacher:
                    st.session_state.user = teacher
                    st.session_state.role = 'teacher'
                    st.rerun()
                else:
                    st.error('電子信箱或密碼錯誤')

        with student_tab:
            with st.form('student_login'):
                username = st.text_input('學生帳號')
                student_password = st.text_input('密碼', type='password')
                student_login = st.form_submit_button('登入')
            if student_login:
                student = login_student(username, student_password)
                if student:
                    st.session_state.user = student
                    st.session_state.role = 'student'
                    st.rerun()
                else:
                    st.error('帳號或密碼錯誤')

    st.stop()


user = st.session_state.user
role = st.session_state.role


# ======================================================
# 側邊選單
# ======================================================
with st.sidebar:
    if role == 'teacher':
        st.subheader(f"{user['teacher_name']} 老師")
        page = st.radio(
            '功能',
            ['學生列表', '建立學生', '任務清單', '上傳紀錄', '商品清單', '待兌換商品'],
            label_visibility='collapsed'
        )
    else:
        st.subheader(f"{user['student_name']} 同學")
        page = st.radio(
            '功能',
            ['我的寵物', '我的任務', '上傳練習', '商店'],
            label_visibility='collapsed'
        )

    st.divider()
    if st.button('登出'):
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()

# 表單頁標題改放卡片內，避免左對齊標題與置中卡片對不齊
if page not in FORM_PAGES:
    st.title(page)

# 顯示上一個操作的結果
if st.session_state.flash:
    show_notice(st.session_state.flash)
    st.session_state.flash = None


# ======================================================
# 老師：學生列表
# ======================================================
if page == '學生列表':
    result = show_student(user)
    if isinstance(result, str):
        st.info(result)
    else:
        st.dataframe(result, width='stretch')


# ======================================================
# 老師：建立學生
# ======================================================
elif page == '建立學生':
    with centered_card():
        st.subheader('建立學生')
        st.caption('建立後系統會自動產生學生帳號與臨時密碼。')
        with st.form('create_student'):
            student_name = st.text_input('學生姓名')
            submitted = st.form_submit_button('建立')
        if submitted:
            if student_name == '':
                st.warning('學生姓名不可空白')
            else:
                result = create_student(user, student_name)
                if result:
                    new_username, temp_password = result
                    show_notice('建立成功，請把帳號與臨時密碼交給學生')
                    st.code(f'帳號：{new_username}\n臨時密碼：{temp_password}')
                    st.caption('學生首次登入後應立即修改密碼')
                else:
                    st.error('建立失敗')


# ======================================================
# 老師：任務清單
# ======================================================
elif page == '任務清單':
    result = teacher_show_quest(user)
    if isinstance(result, str):
        st.info(result)
    else:
        st.dataframe(format_quest_rows(result), width='stretch')
    st.caption('建立、修改與指派任務目前只能在 Console 版操作')


# ======================================================
# 老師：上傳紀錄
# ======================================================
elif page == '上傳紀錄':
    student_result = show_student(user)
    student_id = None
    if not isinstance(student_result, str):
        # 建立「全部學生」加上每位學生的選項
        student_options = {'全部學生': None}
        for student in student_result:
            student_options[student['姓名']] = student['序號']
        selected = st.selectbox('查看哪一位學生', student_options.keys())
        student_id = student_options[selected]

    result = teacher_show_practice_upload(user, student_id)
    if isinstance(result, str):
        st.info(result)
    else:
        st.dataframe(format_upload_rows(result), width='stretch')


# ======================================================
# 老師：商品清單
# ======================================================
elif page == '商品清單':
    result = teacher_show_shop_item(user)
    if isinstance(result, str):
        st.info(result)
    else:
        st.dataframe(format_shop_rows(result), width='stretch')
    st.caption('新增商品目前只能在 Console 版操作')


# ======================================================
# 老師：待兌換商品
# ======================================================
elif page == '待兌換商品':
    result = teacher_show_pending_purchase(user)
    if isinstance(result, str):
        st.info(result)
    else:
        for purchase in result:
            with st.container(border=True):
                st.markdown(f"**{purchase['student_name']}**　{purchase['item_name']}")
                st.caption(f"花費 {purchase['price']} 金幣　購買時間 {purchase['created_at'].strftime('%Y-%m-%d %H:%M')}")
                if st.button('標記完成兌換', key=f"redeem_{purchase['purchase_id']}"):
                    st.session_state.flash = redeem_purchase(user, purchase['purchase_id'])
                    st.rerun()


# ======================================================
# 學生：我的寵物
# ======================================================
elif page == '我的寵物':
    result = show_pet(user)
    if isinstance(result, str):
        st.info(result)
    else:
        pet_column, coin_column = st.columns(2)
        pet_column.metric('寵物階段', result['stage_name'])
        coin_column.metric('目前金幣', user['total_coin'])

        st.subheader('經驗值進度')
        if result['next_stage_name'] is None:
            st.progress(1.0, text=f"累積經驗 {result['total_xp']}｜已達最終階段")
        else:
            # 用下一階段門檻當分母，顯示目前走到哪裡
            next_threshold = result['total_xp'] + result['xp_to_next']
            progress_ratio = result['total_xp'] / next_threshold
            st.progress(
                min(progress_ratio, 1.0),
                text=(
                    f"累積經驗 {result['total_xp']} / {next_threshold}"
                    f"｜距離{result['next_stage_name']}還需 {result['xp_to_next']}"
                )
            )


# ======================================================
# 學生：我的任務
# ======================================================
elif page == '我的任務':
    result = student_show_quest(user)
    if isinstance(result, str):
        st.info(result)
    else:
        for quest in result:
            with st.container(border=True):
                st.markdown(
                    f"**{quest['quest_name']}**　"
                    f"{quest_type_text[quest['quest_type']]}　"
                    f"{quest_status_text[quest['quest_status']]}"
                )
                st.caption(
                    f"條件：{condition_type_text[quest['condition_type']]} {quest['condition_value']}　"
                    f"獎勵：經驗 {quest['reward_xp']} / 金幣 {quest['reward_coin']}"
                )
                progress = quest['progress_value'] / quest['condition_value']
                st.progress(min(progress, 1.0), text=f"{quest['progress_value']} / {quest['condition_value']}")
                if quest['expires_at'] is None:
                    st.caption('到期時間：無期限')
                else:
                    st.caption(f"到期時間：{quest['expires_at'].strftime('%Y-%m-%d %H:%M')}")


# ======================================================
# 學生：上傳練習
# ======================================================
elif page == '上傳練習':
    with centered_card():
        st.subheader('上傳練習')
        st.caption('請輸入曲目名稱並錄音，錄完後可先試聽，確認無誤再上傳。')

        song_name = st.text_input('曲目名稱')
        # 不用 form，錄音後會立即重新整理並顯示試聽
        audio_file = st.audio_input('練習錄音')

        if audio_file is None:
            st.info('請先完成錄音')
        else:
            audio_duration = get_audio_duration(audio_file)
            st.write(f'錄音長度：{audio_duration} 秒')
            st.audio(audio_file)
            st.caption('請先試聽確認，再按下「確認上傳」。')

            if st.button('確認上傳'):
                if song_name == '':
                    st.warning('曲目名稱不可空白')
                elif audio_duration <= 0:
                    st.warning('錄音時間太短，請重新錄製')
                else:
                    # save_audio_file() 需要檔案路徑，先把錄音寫成暫存 wav
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                        temp_file.write(audio_file.getbuffer())
                        temp_path = temp_file.name

                    audio_url = save_audio_file(user, temp_path)
                    os.remove(temp_path)

                    result = create_practice_upload(user, audio_url, song_name, audio_duration)
                    if result == '練習上傳成功':
                        show_notice(result)
                        progress_list = update_quest_progress(user)
                        for quest in progress_list:
                            st.write(f"{quest['quest_name']}：{quest['progress_value']} / {quest['condition_value']}")
                        for reward in give_quest_rewards(progress_list):
                            show_notice(
                                f"任務完成 {reward['quest_name']}，"
                                f"獲得 {reward['reward_xp']} 經驗值、{reward['reward_coin']} 金幣"
                            )
                        # 經驗值與金幣可能已變動，重新讀取學生資料
                        st.session_state.user = get_student(user['student_id'])
                    else:
                        st.error(result)


# ======================================================
# 學生：商店
# ======================================================
elif page == '商店':
    st.metric('目前金幣', user['total_coin'])

    result = student_show_shop_item(user)
    if isinstance(result, str):
        st.info(result)
    else:
        for item in result:
            if item['stock'] is None:
                stock_text = '不限量'
            else:
                stock_text = f"{item['stock']} 件"

            with st.container(border=True):
                st.markdown(f"**{item['item_name']}**")
                st.caption(f"{item_type_text[item['item_type']]}　{item['price']} 金幣　庫存：{stock_text}")
                if item['description']:
                    st.caption(item['description'])
                if st.button('購買', key=f"buy_{item['item_id']}"):
                    st.session_state.flash = purchase_item(user, item['item_id'])
                    st.session_state.user = get_student(user['student_id'])
                    st.rerun()
