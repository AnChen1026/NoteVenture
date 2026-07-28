import secrets
import string


def generate_student_username(teacher_id, serial_no):
    return "T" + str(teacher_id) + "S" + str(serial_no).zfill(3)


def generate_temp_password(length=8):
    alphabet = string.ascii_letters + string.digits

    password = ""

    for _ in range(length):
        password += secrets.choice(alphabet)

    return password