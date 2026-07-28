def teacher_menu(teacher):
    while True:
        choice = input(
            f'\n======== {teacher}老師選單 ========\n'
            '[1]查看學生列表\n'
            '[2]建立學生帳號\n'
            '[3]任務管理\n'
            '[4]查看學生上傳紀錄\n'
            '[5]商品管理\n'
            '[6]轉介學生\n'
            '[7]重設學生密碼\n'
            '[8]設定\n'
            '[0]離開\n'
            ':'
        )

        if choice == '1':
            print('查看學生列表')

        elif choice == '2':
            print('建立學生帳號')

        elif choice == '3':
            print('任務管理')

        elif choice == '4':
            print('查看學生上傳紀錄')

        elif choice == '5':
            print('商品管理')

        elif choice == '6':
            print('轉介學生')

        elif choice == '7':
            print('重設學生密碼')

        elif choice == '8':
            print('設定')

        elif choice == '0':
            print('謝謝')
            break

        else:
            print('輸入錯誤')

teacher_menu('an')