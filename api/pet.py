"""
api/pet.py｜學生寵物狀態

學生 HTML（student_pet.js）→ GET /api/students/<id>/pet → pet_service.show_pet
只能查自己的 student_id（guards + 比對）。
"""

from flask import Blueprint, jsonify
from api.guards import get_login_student, json_safe
from services.pet_service import show_pet

pet_bp = Blueprint('pet', __name__)


# ======================================================
# 學生查看自己的寵物狀態
# ======================================================
@pet_bp.get('/api/students/<int:student_id>/pet')
def api_show_pet(student_id):
    student, error = get_login_student()
    if error:
        return error
    if student['student_id'] != student_id:
        return jsonify({'message': '只能查看自己的寵物'}), 403

    result = show_pet(student)
    if isinstance(result, str):
        return jsonify({'message': result}), 404
    return jsonify({'data': json_safe(result)})
