import wave
from html import escape

import requests
import streamlit as st

st.set_page_config(page_title='NoteAdventure', page_icon=':material/music_note:', layout='wide')

API_BASE_URL = 'http://127.0.0.1:5000'

# ========= 顯示用中文對照 ===========

quest_type_text = {
    'DAILY': '每日任務',
    'WEEKLY': '每週任務',
    'HIDDEN': '隱藏任務'
}

quest_type_options = {
    '每日任務': 'DAILY',
    '每週任務': 'WEEKLY',
    '隱藏任務': 'HIDDEN'
}

condition_type_text = {
    'PRACTICE_COUNT': '練習次數',
    'PRACTICE_DAYS': '練習天數',
    'DISTINCT_SONGS': '不同曲目數',
    'CONSECUTIVE_DAYS': '連續練習天數',
    'TOTAL_UPLOADS': '累積上傳次數',
    'RETURN_AFTER_GAP': '間隔一段時間後再次練習'
}

condition_type_options = {
    '練習次數': 'PRACTICE_COUNT',
    '練習天數': 'PRACTICE_DAYS',
    '不同曲目數': 'DISTINCT_SONGS',
    '連續練習天數': 'CONSECUTIVE_DAYS',
    '累積上傳次數': 'TOTAL_UPLOADS',
    '間隔一段時間後再次練習': 'RETURN_AFTER_GAP'
}

quest_status_text = {
    'COMPLETED': '已完成',
    'ACTIVE': '進行中',
    'EXPIRED': '已過期'
}

boolean_text = {0: '否', 1: '是', False: '否', True: '是'}
quest_active_text = {0: '已停用', 1: '啟用中', False: '已停用', True: '啟用中'}
shop_active_text = {0: '已下架', 1: '上架中', False: '已下架', True: '上架中'}
item_type_text = {'VIRTUAL': '虛擬商品', 'PHYSICAL': '實體商品'}
item_type_options = {'虛擬商品': 'VIRTUAL', '實體商品': 'PHYSICAL'}

FORM_PAGES = {
    '建立學生', '重設學生密碼', '新增任務', '指派任務',
    '新增商品', '上傳練習', '修改密碼'
}

st.session_state.setdefault('user', None)
st.session_state.setdefault('role', None)
st.session_state.setdefault('flash', None)
st.session_state.setdefault('api_session', None)


# ======================================================
# 取得會記住 cookie 的 HTTP session
# ======================================================
def get_api_session():
    if st.session_state.api_session is None:
        st.session_state.api_session = requests.Session()
    return st.session_state.api_session


# ======================================================
# 呼叫 Flask API
# ======================================================
def call_api(method, path, **kwargs):
    url = API_BASE_URL + path
    try:
        response = get_api_session().request(method, url, timeout=30, **kwargs)
    except requests.exceptions.ConnectionError:
        return False, '無法連接 Flask API，請先啟動：flask --app app run --port 5000', None
    except requests.exceptions.RequestException as error:
        return False, f'API 連線失敗：{error}', None

    try:
        data = response.json()
    except ValueError:
        # 常見於 Flask 還是舊版時回傳 HTML 404
        if response.status_code == 404:
            return False, 'API 不存在（404）。請重啟 Flask：flask --app app run --port 5000', 404
        return False, response.text[:200], response.status_code

    if response.ok:
        return True, data, response.status_code
    return False, data.get('message', '請求失敗'), response.status_code


# ======================================================
# 重新向 API 查詢目前登入者
# ======================================================
def refresh_login_user():
    ok, data, _ = call_api('GET', '/api/me')
    if ok:
        st.session_state.user = data['user']
        st.session_state.role = data['role']
        return True
    st.session_state.user = None
    st.session_state.role = None
    return False


def format_datetime_text(value):
    if value is None:
        return '無期限'
    if hasattr(value, 'strftime'):
        return value.strftime('%Y-%m-%d %H:%M')
    text = str(value)
    return text[:16] if len(text) >= 16 else text


def apply_custom_style():
    st.markdown(
        """
        <style>
        .stApp { background-color: #f7f7f8; }
        .block-container { max-width: 1200px; padding-top: 2rem; padding-bottom: 2rem; }
        h1, h2, h3 { color: #1f2937; font-weight: 800; }
        .login-brand h1 { white-space: nowrap; font-size: 2.2rem; margin-bottom: 0.2rem; }
        p, label, div { color: #374151; }
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div {
            background-color: #ffffff !important;
            border: 1px solid #d1d5db !important;
            border-radius: 12px !important;
            box-shadow: none !important;
        }
        input, textarea { color: #111827 !important; }
        .stButton > button {
            background-color: #ffffff !important;
            color: #1f2937 !important;
            border: 1px solid #d1d5db !important;
            border-radius: 12px !important;
            padding: 0.45rem 1rem !important;
            font-weight: 600 !important;
            box-shadow: none !important;
        }
        .stButton > button:hover { border-color: #ff5a52 !important; color: #ff5a52 !important; }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #ff5a52 !important;
            border-bottom: 2px solid #ff5a52 !important;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #d1d5db; border-radius: 14px; overflow: hidden; background: #ffffff;
        }
        .custom-notice {
            background: #fff7f7; border: 1px solid #ffd6d3; border-left: 4px solid #ff5a52;
            border-radius: 12px; padding: 0.85rem 1rem; color: #374151; margin: 0.7rem 0; font-weight: 500;
        }
        .backpack-card {
            aspect-ratio: 1 / 1;
            border: 1px solid #d1d5db;
            border-radius: 14px;
            background: #ffffff;
            padding: 0.7rem;
            margin-bottom: 0.75rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            overflow: hidden;
            box-sizing: border-box;
        }
        .backpack-card.empty {
            background: #f3f4f6;
            border-style: dashed;
        }
        .backpack-name {
            color: #1f2937;
            font-weight: 700;
            font-size: 0.95rem;
            margin-bottom: 0.35rem;
            word-break: break-word;
        }
        .backpack-desc {
            color: #6b7280;
            font-size: 0.8rem;
            word-break: break-word;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def centered_card(width_ratio=(1, 2.2, 1)):
    left, center, right = st.columns(width_ratio)
    return center.container(border=True)


def show_notice(message):
    safe_message = escape(str(message))
    st.markdown(f'<div class="custom-notice">{safe_message}</div>', unsafe_allow_html=True)


def format_quest_rows(quest_rows):
    rows = []
    for quest in quest_rows:
        rows.append({
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
    return rows


def format_upload_rows(upload_rows):
    rows = []
    for upload in upload_rows:
        rows.append({
            '學生': upload['student_name'],
            '曲目': upload['song_name'],
            '秒數': upload['audio_duration'],
            '檔案路徑': upload['audio_url'],
            '上傳時間': format_datetime_text(upload['created_at'])
        })
    return rows


def format_shop_rows(item_rows):
    rows = []
    for item in item_rows:
        rows.append({
            '商品編號': item['item_id'],
            '商品名稱': item['item_name'],
            '商品類型': item_type_text.get(item['item_type'], item['item_type']),
            '價格': item['price'],
            '庫存': '不限量' if item['stock'] is None else item['stock'],
            '說明': item['description'] or '無',
            '狀態': shop_active_text.get(item['is_active'], item['is_active'])
        })
    return rows


def get_audio_duration(audio_file):
    audio_file.seek(0)
    with wave.open(audio_file, 'rb') as wav_file:
        duration = int(wav_file.getnframes() / wav_file.getframerate())
    audio_file.seek(0)
    return duration


def render_change_password_form(is_teacher, force=False):
    with centered_card():
        st.subheader('修改密碼' if not force else '首次登入請先修改密碼')
        if force:
            st.caption('使用臨時密碼登入後，必須先設定自己的密碼才能使用其他功能。')
        with st.form('change_password_form'):
            old_password = st.text_input('目前密碼', type='password')
            new_password = st.text_input('新密碼', type='password')
            confirm_password = st.text_input('確認新密碼', type='password')
            submitted = st.form_submit_button('確認修改')
        if submitted:
            path = '/api/teachers/change-password' if is_teacher else '/api/students/change-password'
            ok, data, _ = call_api(
                'POST',
                path,
                json={
                    'old_password': old_password,
                    'new_password': new_password,
                    'confirm_password': confirm_password
                }
            )
            if ok:
                show_notice(data.get('message', '密碼修改成功'))
                refresh_login_user()
                if force:
                    st.rerun()
            else:
                st.error(data)


apply_custom_style()


# ======================================================
# 登入頁
# ======================================================
if st.session_state.user is None:
    with centered_card():
        st.markdown('<div class="login-brand">', unsafe_allow_html=True)
        st.title('NoteAdventure')
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption('音樂練習 RPG 管理系統（Streamlit → Flask API）')

        teacher_tab, register_tab, student_tab = st.tabs(['老師登入', '老師註冊', '學生登入'])

        with teacher_tab:
            with st.form('teacher_login'):
                email = st.text_input('電子信箱')
                teacher_password = st.text_input('密碼', type='password')
                teacher_login = st.form_submit_button('登入')
            if teacher_login:
                ok, data, _ = call_api(
                    'POST', '/api/teachers/login',
                    json={'email': email, 'password': teacher_password}
                )
                if ok:
                    st.session_state.user = data['user']
                    st.session_state.role = data['role']
                    st.rerun()
                else:
                    st.error(data)

        with register_tab:
            st.caption('註冊成功後，請回到「老師登入」使用電子信箱登入。')
            with st.form('teacher_register'):
                teacher_name = st.text_input('老師姓名')
                register_email = st.text_input('電子信箱', key='register_email')
                register_password = st.text_input('密碼', type='password', key='register_password')
                confirm_password = st.text_input('確認密碼', type='password')
                teacher_register = st.form_submit_button('註冊')
            if teacher_register:
                if (
                    teacher_name.strip() == ''
                    or register_email.strip() == ''
                    or register_password == ''
                    or confirm_password == ''
                ):
                    st.warning('請完整填寫姓名、電子信箱與密碼')
                elif register_password != confirm_password:
                    st.warning('兩次密碼不一致')
                else:
                    ok, data, _ = call_api(
                        'POST', '/api/teachers/register',
                        json={
                            'teacher_name': teacher_name.strip(),
                            'email': register_email.strip(),
                            'password': register_password,
                            'confirm_password': confirm_password
                        }
                    )
                    if ok:
                        show_notice(data.get('message', '老師帳號建立成功'))
                    else:
                        st.error(data)

        with student_tab:
            with st.form('student_login'):
                username = st.text_input('學生帳號')
                student_password = st.text_input('密碼', type='password')
                student_login = st.form_submit_button('登入')
            if student_login:
                ok, data, _ = call_api(
                    'POST', '/api/students/login',
                    json={'username': username, 'password': student_password}
                )
                if ok:
                    st.session_state.user = data['user']
                    st.session_state.role = data['role']
                    st.rerun()
                else:
                    st.error(data)
    st.stop()


user = st.session_state.user
role = st.session_state.role


# ======================================================
# 學生首次登入：強制改密碼
# ======================================================
if role == 'student' and not user.get('password_changed', True):
    with st.sidebar:
        st.subheader(f"{user['student_name']} 同學")
        st.caption('請先修改密碼')
        if st.button('登出'):
            call_api('POST', '/api/logout')
            st.session_state.user = None
            st.session_state.role = None
            st.session_state.api_session = None
            st.rerun()
    render_change_password_form(is_teacher=False, force=True)
    st.stop()


# ======================================================
# 側邊選單
# ======================================================
with st.sidebar:
    if role == 'teacher':
        st.subheader(f"{user['teacher_name']} 老師")
        page = st.radio(
            '功能',
            [
                '首頁',
                '學生列表', '建立學生', '重設學生密碼',
                '任務清單', '新增任務', '指派任務',
                '上傳紀錄',
                '商品清單', '新增商品', '待兌換商品',
                '修改密碼'
            ],
            label_visibility='collapsed'
        )
    else:
        st.subheader(f"{user['student_name']} 同學")
        page = st.radio(
            '功能',
            ['首頁', '我的寵物', '我的任務', '上傳練習', '商店', '我的背包', '修改密碼'],
            label_visibility='collapsed'
        )

    st.divider()
    if st.button('登出'):
        call_api('POST', '/api/logout')
        st.session_state.user = None
        st.session_state.role = None
        st.session_state.api_session = None
        st.rerun()

if page not in FORM_PAGES:
    st.title(page)

if st.session_state.flash:
    show_notice(st.session_state.flash)
    st.session_state.flash = None


# ======================================================
# 老師：首頁 Dashboard
# ======================================================
if role == 'teacher' and page == '首頁':
    ok, data, _ = call_api('GET', '/api/dashboard')
    if not ok:
        st.error(data)
    else:
        dashboard = data.get('data') or {}
        summary = dashboard.get('summary') or {}

        c1, c2, c3 = st.columns(3)
        c1.metric('學生人數', summary.get('student_count', 0))
        c2.metric('啟用中任務', summary.get('active_quest_count', 0))
        c3.metric('進行中任務', summary.get('active_assignment_count', 0))

        c4, c5, c6 = st.columns(3)
        c4.metric('已過期任務', summary.get('expired_assignment_count', 0))
        c5.metric('近 7 天上傳', summary.get('upload_count_7d', 0))
        c6.metric('待兌換商品', summary.get('pending_redeem_count', 0))

        st.subheader('學生概況')
        students = dashboard.get('students') or []
        if students:
            st.dataframe(students, width='stretch')
        else:
            st.info('尚無學生')

        st.subheader('進行中任務（最近 5 筆）')
        assignments = (dashboard.get('active_assignments') or [])[:5]
        if assignments:
            rows = []
            for item in assignments:
                rows.append({
                    '學生': item.get('學生'),
                    '任務': item.get('任務'),
                    '進度': f"{item.get('目前進度', 0)} / {item.get('目標', 0)}",
                    '截止時間': format_datetime_text(item.get('截止時間'))
                })
            st.dataframe(rows, width='stretch')
        else:
            st.info('目前沒有進行中的任務')

        st.subheader('最近上傳（最近 5 筆）')
        uploads = (dashboard.get('recent_uploads') or [])[:5]
        if uploads:
            rows = []
            for item in uploads:
                rows.append({
                    '學生': item.get('學生'),
                    '曲目': item.get('曲目'),
                    '秒數': item.get('秒數'),
                    '上傳時間': format_datetime_text(item.get('上傳時間'))
                })
            st.dataframe(rows, width='stretch')
        else:
            st.info('尚無上傳紀錄')

        st.subheader('待兌換商品（最近 5 筆）')
        redeems = (dashboard.get('pending_redeems') or [])[:5]
        if redeems:
            rows = []
            for item in redeems:
                rows.append({
                    '學生': item.get('學生'),
                    '商品': item.get('商品'),
                    '價格': item.get('價格'),
                    '購買時間': format_datetime_text(item.get('購買時間'))
                })
            st.dataframe(rows, width='stretch')
        else:
            st.info('目前沒有待兌換商品')


# ======================================================
# 老師：學生列表
# ======================================================
elif page == '學生列表':
    ok, data, _ = call_api('GET', '/api/students')
    if not ok:
        st.error(data)
    elif not data.get('data'):
        st.info(data.get('message', '沒有學生資料'))
    else:
        st.dataframe(data['data'], width='stretch')


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
                ok, data, _ = call_api('POST', '/api/students', json={'student_name': student_name})
                if ok:
                    show_notice(data.get('message', '建立成功'))
                    st.code(f"帳號：{data['username']}\n臨時密碼：{data['temp_password']}")
                    st.caption('學生首次登入後必須修改密碼')
                else:
                    st.error(data)


# ======================================================
# 老師：重設學生密碼
# ======================================================
elif page == '重設學生密碼':
    with centered_card():
        st.subheader('重設學生密碼')
        st.caption('重設後學生下次登入需重新修改密碼。')
        with st.form('reset_password'):
            username = st.text_input('學生帳號')
            submitted = st.form_submit_button('重設密碼')
        if submitted:
            if username == '':
                st.warning('請輸入學生帳號')
            else:
                ok, data, _ = call_api(
                    'POST', '/api/students/reset-password',
                    json={'username': username}
                )
                if ok:
                    show_notice(data.get('message', '密碼重設成功'))
                    st.code(f"臨時密碼：{data['temp_password']}")
                else:
                    st.error(data)


# ======================================================
# 老師：任務清單
# ======================================================
elif page == '任務清單':
    ok, data, _ = call_api('GET', '/api/quests')
    if not ok:
        st.error(data)
    elif not data.get('data'):
        st.info(data.get('message', '無任務資料'))
    else:
        st.dataframe(format_quest_rows(data['data']), width='stretch')


# ======================================================
# 老師：新增任務
# ======================================================
elif page == '新增任務':
    with centered_card():
        st.subheader('新增任務')
        with st.form('create_quest'):
            quest_name = st.text_input('任務名稱')
            quest_type_label = st.selectbox('任務類型', list(quest_type_options.keys()))
            condition_label = st.selectbox('任務條件', list(condition_type_options.keys()))
            condition_value = st.number_input('條件數值', min_value=1, step=1, value=1)
            reward_xp = st.number_input('獎勵經驗', min_value=0, step=1, value=10)
            reward_coin = st.number_input('獎勵金幣', min_value=0, step=1, value=5)
            is_once = st.checkbox('一次性任務（不可重複）')
            submitted = st.form_submit_button('建立任務')
        if submitted:
            if quest_name.strip() == '':
                st.warning('任務名稱不可空白')
            else:
                ok, data, _ = call_api(
                    'POST', '/api/quests',
                    json={
                        'quest_name': quest_name.strip(),
                        'quest_type': quest_type_options[quest_type_label],
                        'condition_type': condition_type_options[condition_label],
                        'condition_value': int(condition_value),
                        'reward_xp': int(reward_xp),
                        'reward_coin': int(reward_coin),
                        'is_repeatable': not is_once
                    }
                )
                if ok:
                    show_notice(data.get('message', '任務新建成功'))
                else:
                    st.error(data)


# ======================================================
# 老師：指派任務
# ======================================================
elif page == '指派任務':
    with centered_card():
        st.subheader('指派任務')
        quests_ok, quests_data, _ = call_api('GET', '/api/quests')
        students_ok, students_data, _ = call_api('GET', '/api/students')

        if not quests_ok:
            st.error(quests_data)
        elif not students_ok:
            st.error(students_data)
        else:
            quest_rows = [
                q for q in quests_data.get('data', [])
                if q.get('任務是否啟用') in (1, True)
            ]
            student_rows = students_data.get('data', [])

            if not quest_rows:
                st.info('沒有可指派的啟用任務')
            elif not student_rows:
                st.info('沒有學生資料')
            else:
                quest_labels = {
                    f"{q['任務名稱']}": q['任務編號']
                    for q in quest_rows
                }
                student_labels = {
                    f"{s['姓名']}（{s['帳號']}）": s['序號']
                    for s in student_rows
                }
                with st.form('assign_quest'):
                    quest_label = st.selectbox('選擇任務', list(quest_labels.keys()))
                    student_label = st.selectbox('選擇學生', list(student_labels.keys()))
                    submitted = st.form_submit_button('確認指派')
                if submitted:
                    quest_id = quest_labels[quest_label]
                    student_id = student_labels[student_label]
                    ok, data, _ = call_api(
                        'POST',
                        f'/api/quests/{quest_id}/assign',
                        json={'student_id': int(student_id)}
                    )
                    if ok:
                        show_notice(data.get('message', '任務指派成功'))
                        st.write(f"期間：{data.get('period_key')}")
                        st.write(f"到期：{format_datetime_text(data.get('expires_at'))}")
                    else:
                        st.error(data)


# ======================================================
# 老師：上傳紀錄
# ======================================================
elif page == '上傳紀錄':
    ok, student_data, _ = call_api('GET', '/api/students')
    student_id = None
    if ok and student_data.get('data'):
        student_options = {'全部學生': None}
        for student in student_data['data']:
            student_options[student['姓名']] = student['序號']
        selected = st.selectbox('查看哪一位學生', student_options.keys())
        student_id = student_options[selected]

    params = {'student_id': student_id} if student_id is not None else {}
    ok, data, _ = call_api('GET', '/api/practice-uploads', params=params)
    if not ok:
        st.error(data)
    elif not data.get('data'):
        st.info(data.get('message', '無上傳紀錄'))
    else:
        st.dataframe(format_upload_rows(data['data']), width='stretch')


# ======================================================
# 老師：商品清單
# ======================================================
elif page == '商品清單':
    ok, data, _ = call_api('GET', '/api/shop-items')
    if not ok:
        st.error(data)
    elif not data.get('data'):
        st.info(data.get('message', '無商品資料'))
    else:
        st.dataframe(format_shop_rows(data['data']), width='stretch')


# ======================================================
# 老師：新增商品
# ======================================================
elif page == '新增商品':
    with centered_card():
        st.subheader('新增商品')
        # checkbox 放在 form 外，才能立刻重跑並顯示／隱藏庫存欄位
        unlimited = st.checkbox('不限量庫存', value=True, key='shop_unlimited_stock')
        stock = None
        if not unlimited:
            stock = st.number_input('庫存數量', min_value=0, step=1, value=1, key='shop_stock_value')

        with st.form('create_shop_item'):
            item_name = st.text_input('商品名稱')
            item_type_label = st.selectbox('商品類型', list(item_type_options.keys()))
            price = st.number_input('價格（金幣）', min_value=0, step=1, value=10)
            description = st.text_area('商品說明（可留空）')
            submitted = st.form_submit_button('建立商品')
        if submitted:
            if item_name.strip() == '':
                st.warning('商品名稱不可空白')
            else:
                ok, data, _ = call_api(
                    'POST', '/api/shop-items',
                    json={
                        'item_name': item_name.strip(),
                        'item_type': item_type_options[item_type_label],
                        'price': int(price),
                        'stock': None if unlimited else int(stock),
                        'description': description.strip() or None
                    }
                )
                if ok:
                    show_notice(data.get('message', '商品新增成功'))
                else:
                    st.error(data)


# ======================================================
# 老師：待兌換商品
# ======================================================
elif page == '待兌換商品':
    ok, data, _ = call_api('GET', '/api/purchases/pending')
    if not ok:
        st.error(data)
    elif not data.get('data'):
        st.info(data.get('message', '沒有待兌換的商品'))
    else:
        for purchase in data['data']:
            with st.container(border=True):
                st.markdown(f"**{purchase['student_name']}**　{purchase['item_name']}")
                st.caption(
                    f"花費 {purchase['price']} 金幣　"
                    f"購買時間 {format_datetime_text(purchase['created_at'])}"
                )
                if st.button('標記完成兌換', key=f"redeem_{purchase['purchase_id']}"):
                    redeem_ok, redeem_data, _ = call_api(
                        'PATCH',
                        f"/api/purchases/{purchase['purchase_id']}/redeem"
                    )
                    st.session_state.flash = (
                        redeem_data.get('message', '兌換完成') if redeem_ok else redeem_data
                    )
                    st.rerun()


# ======================================================
# 老師／學生：修改密碼
# ======================================================
elif page == '修改密碼':
    render_change_password_form(is_teacher=(role == 'teacher'))


# ======================================================
# 學生：首頁 Dashboard
# ======================================================
elif role == 'student' and page == '首頁':
    ok, data, _ = call_api('GET', f"/api/students/{user['student_id']}/dashboard")
    if not ok:
        st.error(data)
    else:
        dashboard = data.get('data') or {}
        summary = dashboard.get('summary') or {}
        pet = dashboard.get('pet')

        # 首頁數字以資料庫為準，同步到 session
        if 'total_xp' in summary:
            user['total_xp'] = summary['total_xp']
        if 'total_coin' in summary:
            user['total_coin'] = summary['total_coin']

        c1, c2, c3 = st.columns(3)
        c1.metric('經驗值', summary.get('total_xp', 0))
        c2.metric('金幣', summary.get('total_coin', 0))
        c3.metric('進行中任務', summary.get('active_assignment_count', 0))

        c4, c5, c6 = st.columns(3)
        c4.metric('已過期任務', summary.get('expired_assignment_count', 0))
        c5.metric('近 7 天上傳', summary.get('upload_count_7d', 0))
        c6.metric('待領取實體商品', summary.get('pending_purchase_count', 0))

        st.subheader('我的寵物')
        if not pet:
            st.info('無寵物資料')
        else:
            pet_column, next_column = st.columns(2)
            pet_column.metric('寵物階段', pet.get('stage_name', '-'))
            if pet.get('next_stage_name') is None:
                next_column.metric('下一階段', '已達最終階段')
                st.progress(1.0, text=f"累積經驗 {pet.get('total_xp', 0)}｜已達最終階段")
            else:
                next_column.metric('下一階段', pet.get('next_stage_name'))
                next_threshold = pet['total_xp'] + pet['xp_to_next']
                progress_ratio = pet['total_xp'] / next_threshold if next_threshold else 1.0
                st.progress(
                    min(progress_ratio, 1.0),
                    text=(
                        f"累積經驗 {pet['total_xp']} / {next_threshold}"
                        f"｜距離{pet['next_stage_name']}還需 {pet['xp_to_next']}"
                    )
                )

        st.subheader('進行中任務（最近 5 筆）')
        assignments = (dashboard.get('active_assignments') or [])[:5]
        if assignments:
            rows = []
            for item in assignments:
                rows.append({
                    '任務': item.get('任務'),
                    '類型': quest_type_text.get(item.get('任務類型'), item.get('任務類型')),
                    '進度': f"{item.get('目前進度', 0)} / {item.get('目標', 0)}",
                    '截止時間': format_datetime_text(item.get('截止時間'))
                })
            st.dataframe(rows, width='stretch')
        else:
            st.info('目前沒有進行中的任務')

        st.subheader('最近上傳（最近 5 筆）')
        uploads = (dashboard.get('recent_uploads') or [])[:5]
        if uploads:
            rows = []
            for item in uploads:
                rows.append({
                    '曲目': item.get('曲目'),
                    '秒數': item.get('秒數'),
                    '上傳時間': format_datetime_text(item.get('上傳時間'))
                })
            st.dataframe(rows, width='stretch')
        else:
            st.info('尚無上傳紀錄')

        st.subheader('最近購買（最近 5 筆）')
        purchases = (dashboard.get('recent_purchases') or [])[:5]
        if purchases:
            purchase_status_text = {
                'OWNED': '已擁有',
                'PURCHASED': '待兌換',
                'REDEEMED': '已兌換'
            }
            rows = []
            for item in purchases:
                rows.append({
                    '商品': item.get('商品'),
                    '價格': item.get('價格'),
                    '狀態': purchase_status_text.get(item.get('狀態'), item.get('狀態')),
                    '購買時間': format_datetime_text(item.get('購買時間'))
                })
            st.dataframe(rows, width='stretch')
        else:
            st.info('尚無購買紀錄')


# ======================================================
# 學生：我的寵物
# ======================================================
elif page == '我的寵物':
    ok, data, _ = call_api('GET', f"/api/students/{user['student_id']}/pet")
    if not ok:
        st.error(data)
    else:
        result = data['data']
        pet_column, coin_column = st.columns(2)
        pet_column.metric('寵物階段', result['stage_name'])
        coin_column.metric('目前金幣', user['total_coin'])

        st.subheader('經驗值進度')
        if result['next_stage_name'] is None:
            st.progress(1.0, text=f"累積經驗 {result['total_xp']}｜已達最終階段")
        else:
            next_threshold = result['total_xp'] + result['xp_to_next']
            progress_ratio = result['total_xp'] / next_threshold if next_threshold else 1.0
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
    ok, data, _ = call_api('GET', f"/api/students/{user['student_id']}/quests")
    if not ok:
        st.error(data)
    elif not data.get('data'):
        st.info(data.get('message', '無任務資料'))
    else:
        for quest in data['data']:
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
                st.progress(
                    min(progress, 1.0),
                    text=f"{quest['progress_value']} / {quest['condition_value']}"
                )
                st.caption(f"到期時間：{format_datetime_text(quest['expires_at'])}")


# ======================================================
# 學生：上傳練習
# ======================================================
elif page == '上傳練習':
    with centered_card():
        st.subheader('上傳練習')
        st.caption('請輸入曲目名稱並錄音，錄完後可先試聽，確認無誤再上傳。')
        song_name = st.text_input('曲目名稱')
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
                    audio_file.seek(0)
                    ok, data, _ = call_api(
                        'POST',
                        f"/api/students/{user['student_id']}/practice-uploads",
                        data={'song_name': song_name},
                        files={'audio': ('practice.wav', audio_file.getvalue(), 'audio/wav')}
                    )
                    if ok:
                        show_notice(data.get('message', '練習上傳成功'))
                        for quest in data.get('progress', []):
                            st.write(
                                f"{quest['quest_name']}："
                                f"{quest['progress_value']} / {quest['condition_value']}"
                            )
                        for reward in data.get('rewards', []):
                            show_notice(
                                f"任務完成 {reward['quest_name']}，"
                                f"獲得 {reward['reward_xp']} 經驗值、"
                                f"{reward['reward_coin']} 金幣"
                            )
                        refresh_login_user()
                    else:
                        st.error(data)


# ======================================================
# 學生：商店
# ======================================================
elif page == '商店':
    st.metric('目前金幣', user['total_coin'])
    ok, data, _ = call_api('GET', f"/api/students/{user['student_id']}/shop-items")
    if not ok:
        st.error(data)
    elif not data.get('data'):
        st.info(data.get('message', '目前沒有可購買的商品'))
    else:
        for item in data['data']:
            stock_text = '不限量' if item['stock'] is None else f"{item['stock']} 件"
            with st.container(border=True):
                st.markdown(f"**{item['item_name']}**")
                st.caption(
                    f"{item_type_text[item['item_type']]}　"
                    f"{item['price']} 金幣　庫存：{stock_text}"
                )
                if item['description']:
                    st.caption(item['description'])
                if st.button('購買', key=f"buy_{item['item_id']}"):
                    buy_ok, buy_data, _ = call_api(
                        'POST', f"/api/shop-items/{item['item_id']}/purchase"
                    )
                    if buy_ok:
                        # message 在庫存歸零時會附帶「商品已自動下架」說明
                        st.session_state.flash = buy_data.get('message', '購買成功')
                        refresh_login_user()
                    else:
                        st.session_state.flash = buy_data
                    st.rerun()


# ======================================================
# 學生：我的背包
# ======================================================
elif page == '我的背包':
    ok, data, _ = call_api('GET', f"/api/students/{user['student_id']}/purchases")
    if not ok:
        st.error(data)
    elif not data.get('data'):
        st.info(data.get('message', '背包是空的'))
    else:
        # 5 欄 × 6 列正方形格子；超過 30 件只顯示最近 30 件
        backpack_cols = 5
        backpack_rows = 6
        slot_count = backpack_cols * backpack_rows
        items = list(data['data'][:slot_count])
        while len(items) < slot_count:
            items.append(None)

        for row_index in range(backpack_rows):
            columns = st.columns(backpack_cols)
            for col_index in range(backpack_cols):
                item = items[row_index * backpack_cols + col_index]
                with columns[col_index]:
                    if item is None:
                        st.markdown(
                            '<div class="backpack-card empty"></div>',
                            unsafe_allow_html=True
                        )
                    else:
                        name = escape(str(item.get('item_name') or ''))
                        description = escape(str(item.get('description') or '').strip())
                        desc_html = (
                            f'<div class="backpack-desc">{description}</div>'
                            if description
                            else ''
                        )
                        st.markdown(
                            f'<div class="backpack-card">'
                            f'<div class="backpack-name">{name}</div>'
                            f'{desc_html}'
                            f'</div>',
                            unsafe_allow_html=True
                        )
