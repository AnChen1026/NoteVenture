# -*- coding: utf-8 -*-
"""擷取 Streamlit 畫面。帳密請用環境變數，勿把真實密碼寫進檔案。"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path('docs/midterm_ppt/screenshots')
OUT.mkdir(parents=True, exist_ok=True)
BASE = os.environ.get('NOTEADVENTURE_UI_URL', 'http://127.0.0.1:8501')

TEACHER_EMAIL = os.environ.get('NOTEADVENTURE_TEACHER_EMAIL', 'test')
TEACHER_PASSWORD = os.environ.get('NOTEADVENTURE_TEACHER_PASSWORD', '')
STUDENT_USERNAME = os.environ.get('NOTEADVENTURE_STUDENT_USERNAME', 'test')
STUDENT_PASSWORD = os.environ.get('NOTEADVENTURE_STUDENT_PASSWORD', '')


def shot(page, name):
    path = OUT / f'{name}.png'
    page.screenshot(path=str(path), full_page=True)
    print('saved', path)


def main():
    if not TEACHER_PASSWORD or not STUDENT_PASSWORD:
        raise SystemExit(
            '請先設定環境變數 NOTEADVENTURE_TEACHER_PASSWORD 與 '
            'NOTEADVENTURE_STUDENT_PASSWORD 後再執行。'
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        page.goto(BASE, wait_until='domcontentloaded')
        page.wait_for_timeout(3000)
        shot(page, '01_login')

        page.get_by_role('tab').nth(0).click()
        page.wait_for_timeout(500)
        form = page.locator('[data-testid="stForm"]').nth(0)
        form.get_by_role('textbox').nth(0).fill(TEACHER_EMAIL)
        form.locator('input[type="password"]').fill(TEACHER_PASSWORD)
        form.get_by_test_id('stBaseButton-secondaryFormSubmit').click()
        page.wait_for_timeout(3000)
        shot(page, '02_teacher_home')

        for label, fname in [
            ('學生列表', '03_teacher_students'),
            ('任務清單', '04_teacher_quests'),
            ('上傳紀錄', '05_teacher_uploads'),
            ('商品清單', '06_teacher_shop'),
            ('待兌換商品', '07_teacher_redeem'),
        ]:
            try:
                page.locator('label', has_text=label).first.click()
                page.wait_for_timeout(1800)
                shot(page, fname)
            except Exception as e:
                print('skip', label, e)

        page.get_by_role('button', name='登出').click()
        page.wait_for_timeout(2500)

        page.goto(BASE, wait_until='domcontentloaded')
        page.wait_for_timeout(2000)
        page.get_by_role('tab').nth(2).click()
        page.wait_for_timeout(500)
        form = page.locator('[data-testid="stForm"]').nth(2)
        form.get_by_role('textbox').nth(0).fill(STUDENT_USERNAME)
        form.locator('input[type="password"]').fill(STUDENT_PASSWORD)
        form.get_by_test_id('stBaseButton-secondaryFormSubmit').click()
        page.wait_for_timeout(3000)

        if page.get_by_role('button', name='登出').count() > 0:
            shot(page, '09_student_home')
            for label, fname in [
                ('我的寵物', '10_student_pet'),
                ('我的任務', '11_student_quests'),
                ('商店', '12_student_shop'),
                ('我的背包', '13_student_backpack'),
                ('上傳練習', '14_student_upload'),
            ]:
                try:
                    page.locator('label', has_text=label).first.click()
                    page.wait_for_timeout(1800)
                    shot(page, fname)
                except Exception as e:
                    print('skip', label, e)
        else:
            print('student login failed')

        browser.close()
        print('done')


if __name__ == '__main__':
    main()
