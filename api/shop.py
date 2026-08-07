from flask import Blueprint, request, jsonify
from db import SqlUtils
from api.guards import get_login_teacher, get_login_student, json_safe
from services.shop_service import (
    teacher_show_shop_item,
    student_show_shop_item,
    purchase_item,
    student_show_inventory,
    teacher_show_pending_purchase,
    redeem_purchase
)
from services.student_service import get_student

shop_bp = Blueprint('shop', __name__)
db = SqlUtils()

ITEM_TYPES = {'VIRTUAL', 'PHYSICAL'}


# ======================================================
# 老師查看商品清單
# ======================================================
@shop_bp.get('/api/shop-items')
def api_teacher_shop_items():
    teacher, error = get_login_teacher()
    if error:
        return error

    result = teacher_show_shop_item(teacher)
    if isinstance(result, str):
        return jsonify({'message': result, 'data': []})
    return jsonify({'data': json_safe(result)})


# ======================================================
# 老師建立商品
# ======================================================
@shop_bp.post('/api/shop-items')
def api_create_shop_item():
    teacher, error = get_login_teacher()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    item_name = str(data.get('item_name', '')).strip()
    item_type = data.get('item_type')
    price = data.get('price')
    stock = data.get('stock', None)
    description = data.get('description')

    if item_name == '':
        return jsonify({'message': '請輸入商品名稱'}), 400
    if item_type not in ITEM_TYPES:
        return jsonify({'message': '商品類型不正確'}), 400
    if not isinstance(price, int) or price < 0:
        return jsonify({'message': '價格請輸入非負整數'}), 400
    if stock is not None and (not isinstance(stock, int) or stock < 0):
        return jsonify({'message': '庫存請輸入非負整數，或不限量請傳 null'}), 400
    if description == '':
        description = None

    rowcount = db.execute(
        """
        INSERT INTO shop_item (
        teacher_id,
        item_name,
        item_type,
        price,
        stock,
        description
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            teacher['teacher_id'],
            item_name,
            item_type,
            price,
            stock,
            description
        )
    )
    if rowcount > 0:
        return jsonify({'message': '商品新增成功'}), 201
    return jsonify({'message': '商品新增失敗'}), 500


# ======================================================
# 學生查看商店商品
# ======================================================
@shop_bp.get('/api/students/<int:student_id>/shop-items')
def api_student_shop_items(student_id):
    student, error = get_login_student()
    if error:
        return error
    if student['student_id'] != student_id:
        return jsonify({'message': '只能查看自己的商店'}), 403

    result = student_show_shop_item(student)
    if isinstance(result, str):
        return jsonify({'message': result, 'data': []})
    return jsonify({'data': json_safe(result)})


# ======================================================
# 學生購買商品
# ======================================================
@shop_bp.post('/api/shop-items/<int:item_id>/purchase')
def api_purchase_item(item_id):
    student, error = get_login_student()
    if error:
        return error

    result = purchase_item(student, item_id)
    if result.startswith('購買成功'):
        refreshed = get_student(student['student_id'])
        auto_deactivated = '商品已自動下架' in result
        return jsonify({
            'message': result,
            'total_coin': refreshed['total_coin'] if refreshed else None,
            'auto_deactivated': auto_deactivated
        })
    if '金幣不足' in result:
        return jsonify({'message': result}), 400
    if result in ('查無此商品', '商品已售完'):
        return jsonify({'message': result}), 404
    return jsonify({'message': result}), 400


# ======================================================
# 學生查看我的背包
# ======================================================
@shop_bp.get('/api/students/<int:student_id>/purchases')
def api_student_inventory(student_id):
    student, error = get_login_student()
    if error:
        return error
    if student['student_id'] != student_id:
        return jsonify({'message': '只能查看自己的背包'}), 403

    result = student_show_inventory(student)
    if isinstance(result, str):
        return jsonify({'message': result, 'data': []})
    return jsonify({'data': json_safe(result)})


# ======================================================
# 老師查看待兌換實體商品
# ======================================================
@shop_bp.get('/api/purchases/pending')
def api_pending_purchases():
    teacher, error = get_login_teacher()
    if error:
        return error

    result = teacher_show_pending_purchase(teacher)
    if isinstance(result, str):
        return jsonify({'message': result, 'data': []})
    return jsonify({'data': json_safe(result)})


# ======================================================
# 老師標記已兌換
# ======================================================
@shop_bp.patch('/api/purchases/<int:purchase_id>/redeem')
def api_redeem_purchase(purchase_id):
    teacher, error = get_login_teacher()
    if error:
        return error

    result = redeem_purchase(teacher, purchase_id)
    if '已完成兌換' in result:
        return jsonify({'message': result})
    return jsonify({'message': result}), 404
