from db import SqlUtils

db = SqlUtils()
# def create_student(teacher_id=teacher['teacher_id'], username, password):


def show_student(teacher):
    sql = """
    select student_id 序號, username 帳號, student_name 姓名, total_xp 經驗值, total_coin 金幣數 from student where teacher_id = %s;
    """

    result = db.query_all(sql, teacher['teacher_id'])
    if result:
        print('開啟學生列表')
        return result
    else:
        return '沒有學生資料'

