# -*- coding: utf-8 -*-
"""擷取學生 HTML UI。使用 Flask session cookie（不印出密碼／金鑰）。"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402

OUT = Path(__file__).resolve().parent / 'screenshots'
OUT.mkdir(parents=True, exist_ok=True)
CROP = Path(__file__).resolve().parent / 'screenshots_crop'
CROP.mkdir(parents=True, exist_ok=True)

BASE = 'http://127.0.0.1:5000'
STUDENT_ID = 1
PAGES = [
    ('html_01_login', '/student/login', False),
    ('html_02_home', '/student/home', True),
    ('html_03_practice', '/student/practice', True),
    ('html_04_quests', '/student/quests', True),
    ('html_05_pet', '/student/pet', True),
    ('html_06_shop', '/student/shop', True),
    ('html_07_class', '/student/class', True),
    ('html_08_settings', '/student/settings', True),
]


def session_cookie_value(app, student_id=STUDENT_ID):
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['role'] = 'student'
        sess['student_id'] = student_id
    client.get('/api/me')

    # Werkzeug / Flask 版本差異：優先 get_cookie，再退回 cookie_jar
    if hasattr(client, 'get_cookie'):
        cookie = client.get_cookie('session')
        if cookie is not None:
            return cookie.value

    jar = getattr(client, 'cookie_jar', None)
    if jar is not None:
        for c in jar:
            if getattr(c, 'name', None) == 'session':
                return c.value

    raise RuntimeError('無法建立 session cookie，請確認 Flask SECRET_KEY 與 student_id')


def crop_center(src: Path, dst: Path, max_w=1400, max_h=900):
    from PIL import Image

    img = Image.open(src)
    w, h = img.size
    # 去掉過長捲軸，取上方視窗
    box = (0, 0, min(w, max_w), min(h, max_h))
    img.crop(box).save(dst)


def main():
    app = create_app()
    cookie_val = session_cookie_value(app)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        context.add_cookies([{
            'name': 'session',
            'value': cookie_val,
            'url': BASE,
            'httpOnly': True,
            'sameSite': 'Lax',
        }])
        page = context.new_page()

        for name, path, need_auth in PAGES:
            page.goto(BASE + path, wait_until='domcontentloaded')
            page.wait_for_timeout(2200 if need_auth else 1200)
            out = OUT / f'{name}.png'
            page.screenshot(path=str(out), full_page=False)
            crop_center(out, CROP / f'{name}.png')
            print('saved', out)

        browser.close()
    print('done')


if __name__ == '__main__':
    main()
