from data_base.sql_main import *


async def make_categories_delete_exceptions_list(categories_data):
    result = []
    used_categories_ids_lists = cur.execute('SELECT DISTINCT category_id FROM link_categories_and_purchases').fetchall()
    used_categories_ids = []
    for category_list in used_categories_ids_lists:
        if category_list[0] is not None:
            used_categories_ids.append(category_list[0])
    for category in categories_data:
        if category[0] in used_categories_ids:
            result.append(category[0])
    return result


async def sql_categorize(id_of_list_of_purchases_ids, category_id):
    print('\n***********************************\nid_of_list_of_purchases_ids ____START\n')
    print('sql_categorize')
    print(f'category_id: {category_id}')
    purchases_ids_str = cur.execute('SELECT comment FROM list001 WHERE id IS ?',
                                    (str(id_of_list_of_purchases_ids),)).fetchall()[0][0]
    purchases_ids_list = purchases_ids_str.split(",")
    if purchases_ids_list[-1] == '-50':
        purchase_id = purchases_ids_list[0]
        if category_id != '-1':
            cur.execute("INSERT INTO link_categories_and_purchases (category_id, purchase_id) VALUES (?, ?)",
                        (category_id, int(purchase_id)))
            cur.execute("DELETE from link_categories_and_purchases WHERE category_id='-1' AND purchase_id=?",
                        (purchase_id,))
        del purchases_ids_list[0]
        print(f'purchases_ids_list:\npurchases_ids_list')
        if len(purchases_ids_list) > 1:
            purchase_id = purchases_ids_list[0]
            purchase_name = cur.execute("SELECT name FROM list001 WHERE id IS ?",
                                        (purchase_id,)).fetchall()[0][0]
            purchases_ids_string = ','.join(map(str, purchases_ids_list))
            cur.execute('UPDATE list001 SET comment=? WHERE id=?', (purchases_ids_string, id_of_list_of_purchases_ids))
            base.commit()
            print('\nid_of_list_of_purchases_ids ____FINISH\n***********************************\n')
            return purchase_name
        else:
            cur.execute('DELETE FROM list001 WHERE id IS ?', (str(id_of_list_of_purchases_ids),))
            base.commit()
            print('\nid_of_list_of_purchases_ids ____FINISH\n***********************************\n')
            return ''

    else:
        cur.execute('DELETE FROM list001 WHERE id IS ?', (str(id_of_list_of_purchases_ids),))
        print(f'purchases_ids_list: {purchases_ids_list}')
        for purchase_id in purchases_ids_list:
            if int(category_id) != -1:
                print(f"Добавляем связь товара {purchase_id} с категорией '{category_id}'")
                cur.execute("INSERT INTO link_categories_and_purchases (category_id, purchase_id) VALUES (?, ?)",
                            (category_id, int(purchase_id)))
                print(f"Удаляем связь товара {purchase_id} с категорией 'Бех категории'")
                cur.execute("""DELETE FROM link_categories_and_purchases WHERE category_id='-1' and purchase_id=?""",
                            (int(purchase_id),))
        base.commit()
        print('\nid_of_list_of_purchases_ids ____FINISH\n***********************************\n')
        return ''


async def sql_get_categories_ids_for_purchase(purchase_id):
    categories_ids_data = cur.execute(
        'SELECT category_id FROM link_categories_and_purchases WHERE purchase_id IS ?', (purchase_id,)).fetchall()
    categories_ids = []
    for category_id_data in categories_ids_data:
        categories_ids.append(category_id_data[0])
    return categories_ids


async def sql_add_category(name, description):
    cur.execute('INSERT INTO categories (name, description) VALUES (?, ?)', (name, description))
    base.commit()


async def sql_update_category(category_id, name, description):
    cur.execute('UPDATE categories SET name = ?, description = ? WHERE id = ?', (name, description, category_id))
    base.commit()


async def sql_read_categories():
    data = cur.execute('SELECT * FROM categories').fetchall()
    return data


async def sql_read_current_group_categories():
    data = cur.execute('SELECT * FROM categories WHERE ').fetchall()
    return data


async def sql_read_used_categories_ids(purchases_ids_list=[]):
    print('___ sql_read_used_categories_ids ____START')
    print(f'purchases_ids_list: {purchases_ids_list}')
    used_categories_ids = []
    if purchases_ids_list:
        for purchase_id in purchases_ids_list:
            print(f'purchase_id: {purchase_id}')
            category_id = cur.execute('SELECT category_id FROM link_categories_and_purchases WHERE purchase_id IS ?',
                                      (purchase_id,)).fetchall()[0][0]
            used_categories_ids.append(category_id)
            print(f'category_id: {category_id}')
            print(f'used_categories_ids: {used_categories_ids}')
        used_categories_ids = [*set(used_categories_ids)]  # Удаляем дубликаты
        print(print(f'used_categories_ids after removing duplicates: {used_categories_ids}'))
    else:
        used_categories_ids_data = cur.execute('SELECT DISTINCT category_id FROM link_categories_and_purchases').fetchall()
        for category_id_data in used_categories_ids_data:
            # if purchases_ids_list:
            #     specific_category_purchases_ids_lists = cur.execute(
            #         'SELECT DISTINCT purchase_id FROM link_categories_and_purchases WHERE category_id IS ?',
            #         (category_id_data[0],))
            #     for purchase_id_list in specific_category_purchases_ids_lists:
            #         if purchase_id_list[0] in purchases_ids_list:
            #             used_categories_ids.append(category_id_data[0])
            # else:
            used_categories_ids.append(category_id_data[0])
    print('___ sql_read_used_categories_ids ____FINISH')
    return used_categories_ids


async def sql_read_category(category_id):
    category = cur.execute('SELECT * FROM categories WHERE id IS ?', (category_id,)).fetchall()
    return category


async def sql_delete_category(category_id):
    categories_data = await sql_read_categories()
    exceptions_list = await make_categories_delete_exceptions_list(categories_data)
    if category_id not in exceptions_list:
        cur.execute(f"""DELETE FROM categories WHERE id='{category_id}'""")
        base.commit()
        return True
    else:
        return False
    # Перед удалением нужно проверить, действительно ли категория
    # все еще свободна, возможно другой пользователь в это время ее уже занял