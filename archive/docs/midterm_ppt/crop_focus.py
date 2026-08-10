# -*- coding: utf-8 -*-
"""把原始截圖裁成「重點內容」，減少空白與側欄，方便簡報清楚顯示。"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'screenshots'
DST = ROOT / 'screenshots_crop'
DST.mkdir(parents=True, exist_ok=True)

# (left, top, right, bottom) — 以 screenshots/ 原始尺寸為準
CROPS = {
    # Console：只留選單文字區（含標題列）
    'c01_console_main.png': (0, 0, 560, 340),
    'c02_console_teacher.png': (0, 0, 640, 500),
    'c03_console_student.png': (0, 0, 600, 430),

    # Streamlit 老師：裁掉左側選單與右側空白，放大主內容
    '02_teacher_home.png': (300, 40, 1220, 840),
    '03_teacher_students.png': (300, 40, 1280, 780),
    '04_teacher_quests.png': (300, 50, 1400, 560),
    '05_teacher_uploads.png': (300, 50, 1340, 640),
    '06_teacher_shop.png': (300, 50, 1340, 640),
    '07_teacher_redeem.png': (300, 50, 1340, 640),

    # Streamlit 學生頁（轉折對比用）：側欄 + 首頁摘要
    '09_student_home.png': (0, 40, 1100, 780),

    # 學生 HTML：裁到功能面板／地圖主體
    'html_01_login.png': (440, 100, 1000, 800),
    'html_02_home.png': (60, 20, 1380, 880),
    'html_03_practice.png': (420, 150, 1020, 740),
    'html_04_quests.png': (420, 150, 1020, 620),
    'html_05_pet.png': (360, 180, 1080, 820),
    'html_06_shop.png': (420, 140, 1020, 700),
    'html_07_class.png': (200, 140, 1160, 760),
    'html_08_settings.png': (400, 100, 1040, 800),
}


def clamp_box(w, h, box):
    left, top, right, bottom = box
    left = max(0, min(left, w - 1))
    top = max(0, min(top, h - 1))
    right = max(left + 1, min(right, w))
    bottom = max(top + 1, min(bottom, h))
    return (left, top, right, bottom)


def main():
    count = 0
    for name, box in CROPS.items():
        src = SRC / name
        if not src.exists():
            print('skip missing', name)
            continue
        im = Image.open(src)
        crop = im.crop(clamp_box(im.width, im.height, box))
        out = DST / name
        crop.save(out)
        print(f'{name}: {im.size} -> {crop.size} ratio={crop.width / crop.height:.2f}')
        count += 1
    print(f'done, cropped {count} files -> {DST}')


if __name__ == '__main__':
    main()
