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
# 學生查看老師上架的商品
# ======================================================
def student_show_shop_item(student):
    # 只顯示自己老師上架、還有庫存的商品
    sql = """
    SELECT item_id, item_name, item_type, price, stock, description
    FROM shop_item
    WHERE teacher_id = %s
    AND is_active = TRUE
    AND (stock IS NULL OR stock > 0)
    ORDER BY item_id;
    """
    result = db.query_all(sql, (student['teacher_id'],))
    if result:
        return result
    return '目前沒有可購買的商品'


# ======================================================
# 學生購買商品
# ======================================================
def purchase_item(student, item_id):
    # 只能買自己老師上架的商品
    sql = """
    SELECT item_id, item_name, item_type, price, stock
    FROM shop_item
    WHERE item_id = %s
    AND teacher_id = %s
    AND is_active = TRUE;
    """
    item = db.query_one(sql, (item_id, student['teacher_id']))
    if not item:
        return '查無此商品'
    if item['stock'] is not None and item['stock'] <= 0:
        return '商品已售完'

    # 金幣以資料庫目前數值為準
    sql = """
    SELECT total_coin
    FROM student
    WHERE student_id = %s;
    """
    total_coin = db.query_one(sql, (student['student_id'],))['total_coin']
    if total_coin < item['price']:
        return f"金幣不足，還需要 {item['price'] - total_coin} 金幣"

    # 虛擬商品購買後直接持有，實體商品要等老師兌換
    if item['item_type'] == 'VIRTUAL':
        status = 'OWNED'
    else:
        status = 'PURCHASED'

    coin_sql = """
    UPDATE student
    SET total_coin = total_coin - %s
    WHERE student_id = %s
    AND total_coin >= %s;
    """
    transaction_sql = """
    INSERT INTO coin_transaction (
    student_id,
    source_type,
    amount
    )
    VALUES (%s, 'SHOP_PURCHASE', %s)
    """
    purchase_sql = """
    INSERT INTO purchase_record (
    student_id,
    item_id,
    price,
    status
    )
    VALUES (%s, %s, %s, %s)
    """
    sql_list = [
        (coin_sql, (item['price'], student['student_id'], item['price'])),
        (transaction_sql, (student['student_id'], -item['price'])),
        (purchase_sql, (student['student_id'], item['item_id'], item['price'], status))
    ]

    # 不限量商品不需要扣庫存
    if item['stock'] is not None:
        stock_sql = """
        UPDATE shop_item
        SET stock = stock - 1
        WHERE item_id = %s
        AND stock > 0;
        """
        sql_list.append((stock_sql, (item['item_id'],)))

    # 扣金幣、金幣異動、購買紀錄與庫存寫在同一個 transaction
    if db.execute_transaction(sql_list):
        if status == 'PURCHASED':
            return f"購買成功 {item['item_name']}，請找老師兌換"
        return f"購買成功 {item['item_name']}"
    return '購買失敗'


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


# ======================================================
# 學生商店介面
# ======================================================
def student_shop_menu(student):
    while True:
        result = student_show_shop_item(student)
        if isinstance(result, str):
            return result

        # 金幣與庫存每次都重新查詢，購買後才會顯示最新數字
        sql = """
        SELECT total_coin
        FROM student
        WHERE student_id = %s;
        """
        total_coin = db.query_one(sql, (student['student_id'],))['total_coin']

        item_dict = {}
        i = 1
        for item in result:
            item_dict[f'{i}'] = item
            i += 1

        print(f'\n======== 商店 (目前金幣 {total_coin}) ========')
        for i in range(1, len(item_dict) + 1):
            item = item_dict[str(i)]
            if item['stock'] is None:
                stock_text = '不限量'
            else:
                stock_text = f"{item['stock']} 件"

            print()
            print(f"[{i}] {item['item_name']}")
            print(f"類型：{item_type_text[item['item_type']]}")
            print(f"價格：{item['price']} 金幣")
            print(f"庫存：{stock_text}")
            if item['description']:
                print(f"說明：{item['description']}")

        choice = input('\n請選擇要購買的商品([0]返回)：')
        if choice == '0':
            return '返回'
        elif choice in item_dict:
            result = purchase_item(student, item_dict[choice]['item_id'])
            print(result)
        else:
            print('輸入錯誤')
