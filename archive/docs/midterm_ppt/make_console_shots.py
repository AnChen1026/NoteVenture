# -*- coding: utf-8 -*-
"""把 Console 選單文字渲染成終端機風格截圖（不含真實密碼）。"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / 'screenshots'
OUT.mkdir(parents=True, exist_ok=True)
CROP = Path(__file__).resolve().parent / 'screenshots_crop'
CROP.mkdir(parents=True, exist_ok=True)

W, H = 1280, 720
BG = (12, 16, 22)
FG = (220, 230, 235)
ACCENT = (255, 180, 90)
DIM = (140, 150, 160)


def font(size=22):
    # 優先用可顯示繁中的字型（Consolas 不支援中文會變方塊）
    for name in (
        'C:/Windows/Fonts/msjh.ttc',
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/mingliu.ttc',
        'C:/Windows/Fonts/consola.ttf',
    ):
        try:
            return ImageFont.truetype(name, size, index=0)
        except OSError:
            continue
    return ImageFont.load_default()


def render(name, lines, title='PowerShell — NoteAdventure Console'):
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    title_font = font(16)
    body_font = font(22)

    # title bar
    draw.rectangle((0, 0, W, 36), fill=(32, 38, 48))
    draw.text((14, 8), title, fill=DIM, font=title_font)

    y = 56
    for line in lines:
        color = ACCENT if line.startswith('=====') or line.startswith('========') else FG
        if line.startswith('[') or line.endswith('：') or line.endswith(':'):
            color = FG
        if line.startswith('PS ') or line.startswith('> '):
            color = DIM
        draw.text((28, y), line, fill=color, font=body_font)
        y += 30

    path = OUT / f'{name}.png'
    img.save(path)
    img.save(CROP / f'{name}.png')
    print('saved', path)


def main():
    render(
        'c01_console_main',
        [
            'PS C:\\Users\\student\\Desktop\\NoteVenture> python main.py',
            '',
            '===== 音樂練習 RPG =====',
            '選擇功能',
            '[1]老師登入',
            '[2]學生登入',
            '[3]老師註冊',
            '[0]離開',
            '：_',
        ],
    )
    render(
        'c02_console_teacher',
        [
            '> 選擇 [1] 老師登入',
            '',
            '======== test老師選單 ========',
            '[1]首頁',
            '[2]查看學生列表',
            '[3]建立學生帳號',
            '[4]任務管理',
            '[5]查看學生上傳紀錄',
            '[6]商品管理',
            '[7]轉介學生',
            '[8]重設學生密碼',
            '[9]設定(修改密碼)',
            '[0]登出',
            ':_',
        ],
    )
    render(
        'c03_console_student',
        [
            '> 選擇 [2] 學生登入',
            '',
            '======== 學生選單 ========',
            '[1]首頁',
            '[2]設定(修改密碼)',
            '[3]任務欄',
            '[4]商店',
            '[5]我的背包',
            '[6]上傳練習',
            '[7]查看近期展演資訊',
            '[0]登出',
            ':_',
        ],
    )
    print('done')


if __name__ == '__main__':
    main()
