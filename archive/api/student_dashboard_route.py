"""
備援：舊版學生首頁摘要 API（已非正式路徑）。

原掛在 api/dashboard.py：
  GET /api/students/<student_id>/dashboard

確認僅 archive/streamlit_student/streamlit_app_with_student_backup.py 有呼叫。
正式學生 HTML／現版老師 Streamlit 皆未使用。
老師端請繼續用 GET /api/dashboard。

若要恢復：把下方路由貼回 api/dashboard.py，並 import
get_login_student、get_student_dashboard。
"""

# ----- 以下為移出前的路由內容（參考用，不會被 app 註冊）-----
#
# @dashboard_bp.get('/api/students/<int:student_id>/dashboard')
# def api_student_dashboard(student_id):
#     student, error = get_login_student()
#     if error:
#         return error
#     if student['student_id'] != student_id:
#         return jsonify({'message': '只能查看自己的首頁'}), 403
#
#     data = get_student_dashboard(student)
#     if not data:
#         return jsonify({'message': '找不到學生資料'}), 404
#     return jsonify({'data': json_safe(data)})
