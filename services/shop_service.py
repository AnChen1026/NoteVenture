from db import SqlUtils

db = SqlUtils()

# ========= 顯示用中文對照 ===========

item_type_text = {
    'VIRTUAL': '虛擬商品',
    'PHYSICAL': '實體商品'
}


# ======================================================
# 老師查看自己建立的商品
# ======================================================
def teacher_show_shop_item(teacher):
    sql = """
    SELECT item_id, item_name, item_type, price, stock, description, is_active
    FROM shop_item
    WHERE teacher_id = %s
    ORDER BY item_id;
    """
    result = db.query_all(sql, (teacher['teacher_id'],))
    if result:
        return result
    return '無商品資料'


# ======================================================
# 新增商品
# ======================================================
def create_shop_item(teacher):
    while True:
        item_name = input('請輸入商品名稱([0]返回)：')
        if item_name == '0':
            return '已取消新增'
        elif item_name == '':
            print('商品名稱不可空白')
            continue

        while True:
            choice = input(
                '請選擇商品類型\n'
                '[1]虛擬商品\n'
                '[2]實體商品\n'
                '：'
            )
            if choice == '1':
                item_type = 'VIRTUAL'
                break
            elif choice == '2':
                item_type = 'PHYSICAL'
                break
            else:
                print('輸入錯誤')

        while True:
            price = input('請輸入商品價格(金幣)：')
            if price.isdigit():
                price = int(price)
                break
            print('價格請輸入數字')

        # 庫存留空表示不限量，存入 NULL
        while True:
            stock = input('請輸入商品庫存(不限量請直接按 Enter)：')
            if stock == '':
                stock = None
                break
            elif stock.isdigit():
                stock = int(stock)
                break
            print('庫存請輸入數字')

        description = input('請輸入商品說明(可留空)：')
        if description == '':
            description = None

        if stock is None:
            stock_text = '不限量'
        else:
            stock_text = f'{stock} 件'

        if description is None:
            description_text = '無'
        else:
            description_text = description

        print(
        '\n===== 商品內容確認 =====\n'
        f'商品名稱：{item_name}\n'
        f'商品類型：{item_type_text[item_type]}\n'
        f'商品價格：{price} 金幣\n'
        f'商品庫存：{stock_text}\n'
        f'商品說明：{description_text}\n'
        )
        while True:
            choice = input('是否正確\n[1]是 [2]否：')
            if choice == '1':
                sql = """
                INSERT INTO shop_item (
                teacher_id,
                item_name,
                item_type,
                price,
                stock,
                description
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                rowcount = db.execute(
                    sql,
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
                    return '商品新增成功'
                return '商品新增失敗'
            elif choice == '2':
                break
            else:
                print('輸入錯誤')


# ======================================================
# 商品管理介面
# ======================================================
def shop_menu(teacher):
    while True:
        choice = input(
            '\n======== 商品管理 ========\n'
            '[1]查看商品\n'
            '[2]新增商品\n'
            '[0]返回\n'
            ':'
        )
        if choice == '1':
            result = teacher_show_shop_item(teacher)
            if isinstance(result, str):
                print(result)
                continue

            print('\n======== 商品清單 ========')
            for item in result:
                if item['stock'] is None:
                    stock_text = '不限量'
                else:
                    stock_text = f"{item['stock']} 件"

                if item['is_active']:
                    is_active_text = '上架中'
                else:
                    is_active_text = '已下架'

                print()
                print(f"[{item['item_id']}] {item['item_name']}")
                print(f"類型：{item_type_text[item['item_type']]}")
                print(f"價格：{item['price']} 金幣")
                print(f"庫存：{stock_text}")
                print(f"狀態：{is_active_text}")
                if item['description']:
                    print(f"說明：{item['description']}")

        elif choice == '2':
            result = create_shop_item(teacher)
            print(result)

        elif choice == '0':
            print('返回')
            break

        else:
            print('輸入錯誤')
