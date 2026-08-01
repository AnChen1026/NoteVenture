from services.teacher_service import create_teacher, login_teacher
from services.student_service import login_student
from teacher_menu import teacher_menu
from student_menu import student_menu






# ========== main ==========
while True:
    choice = input(
        '\n===== 音樂練習 RPG =====\n'
        '選擇功能\n'
        '[1]老師登入\n'
        '[2]學生登入\n'
        '[3]老師註冊\n'
        '[0]離開\n'
        '：'
                   )
    if choice == '1':
        email = 'test'
        password = 'test'
        # email = input('請輸入email：')
        # password = input('請輸入密碼：')
        teacher = login_teacher(email, password)
        if teacher:
            teacher_menu(teacher)
            
        

    elif choice == '2':
        username = 'Test001'
        password = 'test'
        # username = input('請輸入帳號：')
        # password = input('請輸入密碼：')
        student = login_student(username, password)
        if student:
            student_menu(student)

    elif choice == '3':
        while True:
            teacher_name = input('請輸入老師姓名\n：')
            email = input('請輸入電子信箱\n：')
            password = input('請輸入密碼\n：')
            confirm_password = input('請確認密碼\n：')
            if confirm_password == password:
                message = create_teacher(teacher_name, email, password)
                print(message)
                break
            else:
                print('密碼不一致')

    elif choice == '0':
        print('感謝您的使用，再見')
        break

    else:
        print('輸入錯誤')