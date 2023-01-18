from data_base.sql_main import *


async def make_used_categories_ids_list(categories_data):
    print('Hello')
    used_categories_ids_list = []
    request = 'SELECT DISTINCT categories.id FROM categories, link_categories_and_purchases ' \
              'WHERE categories.id IN (link_categories_and_purchases.category_id) ORDER BY categories.number;'
    # used_categories_ids_lists = cur.execute('SELECT DISTINCT category_id FROM link_categories_and_purchases').fetchall()
    used_categories_ids_data = cur.execute(request).fetchall()
    used_categories_ids = []
    for category_list in used_categories_ids_data:
        if category_list[0] is not None:
            used_categories_ids.append(category_list[0])
    for category in categories_data:
        if category[0] in used_categories_ids:
            used_categories_ids_list.append(category[0])
    # categories_data = cur.execute('SELECT id, number FROM categories').fetchall()
    # categories = {}
    # for category_data in categories_data:
    #     categories[category_data[0]] = category_data[1]
    # print(f'categories:\n{categories}')
    # used_categories_ids_sorted_list = [-5] * len(categories)
    # print(f'used_categories_ids_sorted_list:\n{used_categories_ids_sorted_list}')
    # print(f'used_categories_ids:\n{used_categories_ids}')
    # for category_id in used_categories_ids:
    #     category_number = categories[category_id]
    #     print(f'category_number: {category_number}')
    #     used_categories_ids_sorted_list[int(category_number)] = category_id
    #     print(f'used_categories_ids_sorted_list:\n{used_categories_ids_sorted_list}')
    # while -5 in used_categories_ids_sorted_list:
    #     used_categories_ids_sorted_list.remove(-5)
    return used_categories_ids_list


async def sql_categorize(id_of_list_of_purchases_ids, category_id):
    print('\n___ sql_categorize ____START\n')
    print('sql_categorize')
    print(f'category_id: {category_id}')
    print(f'id_of_list_of_purchases_ids: {id_of_list_of_purchases_ids}')
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
        print(f'purchases_ids_list:\n{purchases_ids_list}')
        if len(purchases_ids_list) > 1:
            purchase_id = purchases_ids_list[0]
            print(f'purchase_id: {purchase_id}')
            purchase_name = cur.execute("SELECT name FROM list001 WHERE id IS ?",
                                        (purchase_id,)).fetchall()[0][0]
            purchases_ids_string = ','.join(map(str, purchases_ids_list))
            cur.execute('UPDATE list001 SET comment=? WHERE id=?', (purchases_ids_string, id_of_list_of_purchases_ids))
            base.commit()
            print('\n___ sql_categorize ____FINISH\n')
            return purchase_name
        else:
            cur.execute('DELETE FROM list001 WHERE id IS ?', (str(id_of_list_of_purchases_ids),))
            base.commit()
            print('\n___ sql_categorize ____FINISH\n')
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
        print('\n___ sql_categorize ____FINISH\n')
        return ''


async def sql_categorize_or_uncategorize_current_purchase(category_id, purchase_id, uncategorize=False):
    """
    Функция выполняет SQL запрос для добавления связи между товаром и категорией.
    При значении параметра uncategorize=True функция напротив удаляет связь товара и категории.
    При отсутствии какой-нибудь другой связи кроме удаляемой -- назначается связь с категорией "Без категории"
    :param category_id: id категории
    :param purchase_id: id товара
    :param uncategorize: направление действия функции (добавление или удаление связи товара с категорией)
    """
    print('\n___ sql_categorize_or_uncategorize_current_purchase ____START\n')
    if uncategorize:
        cur.execute('DELETE FROM link_categories_and_purchases WHERE category_id=? AND purchase_id=?',
                    (category_id, purchase_id))
        cur.execute('INSERT INTO link_categories_and_purchases (category_id, purchase_id) '
                    'SELECT ?, ? WHERE NOT EXISTS (SELECT category_id, purchase_id FROM link_categories_and_purchases '
                    'WHERE purchase_id=?)',
                    (-1, purchase_id,
                     purchase_id))
    else:
        cur.execute('INSERT INTO link_categories_and_purchases (category_id, purchase_id) '
                    'SELECT ?, ? WHERE NOT EXISTS (SELECT category_id, purchase_id FROM link_categories_and_purchases '
                    'WHERE category_id=? AND purchase_id=?)',
                    (category_id, purchase_id,
                     category_id, purchase_id))
        cur.execute('DELETE FROM link_categories_and_purchases WHERE category_id="-1" AND purchase_id=?', (purchase_id,))
    base.commit()
    print('\n___ sql_categorize_or_uncategorize_current_purchase ____FINISH\n')


async def sql_get_categories_ids_for_purchase(purchase_id):
    categories_ids_data = cur.execute(
        'SELECT category_id FROM link_categories_and_purchases WHERE purchase_id IS ?', (purchase_id,)).fetchall()
    categories_ids = []
    for category_id_data in categories_ids_data:
        categories_ids.append(category_id_data[0])
    return categories_ids


async def sql_add_category(name, description):
    categories_quantity = len(cur.execute('select * from categories').fetchall())
    cur.execute('INSERT INTO categories (name, description, number) VALUES (?, ?, ?)', (name, description, categories_quantity))
    base.commit()


async def sql_update_category(category_id, name, description):
    cur.execute('UPDATE categories SET name = ?, description = ? WHERE id = ?', (name, description, category_id))
    base.commit()


async def sql_read_categories():
    data = cur.execute('SELECT * FROM categories ORDER BY number').fetchall()
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
        request = 'SELECT DISTINCT categories.id FROM categories, link_categories_and_purchases ' \
                  'WHERE categories.id IN (link_categories_and_purchases.category_id) ORDER BY categories.number;'
        # used_categories_ids_data = cur.execute('SELECT DISTINCT category_id FROM link_categories_and_purchases').fetchall()
        used_categories_ids_data = cur.execute(request).fetchall()
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
    # categories_data = cur.execute('SELECT * FROM categories').fetchall()
    # used_categories_ids_list = []
    # for category in categories_data:
    #     if category[0] in used_categories_ids:
    #         used_categories_ids_list.append(category[0])
    # categories_data = cur.execute('SELECT id, number FROM categories').fetchall()
    # categories = {}
    # # Наполняем словарь с категориями (id: sort_number)
    # for category_data in categories_data:
    #     category_id = category_data[0]
    #     category_sort_number = category_data[1]
    #     categories[category_id] = category_sort_number
    # print(f'categories dict with ids and numbers:\n{categories}')
    # # Создаем список, в который будем добавлять id категорий, используя номер сортировки как индекс
    # # наполняем его значениями "-5", чтобы сохранилась сортировка при наполнении списка id категорий
    # used_categories_ids_sorted_list = [-5] * len(categories)
    # print(f'used_categories_ids_sorted_list:\n{used_categories_ids_sorted_list}')
    # print(f'used_categories_ids:\n{used_categories_ids}')
    # # Наполняем список категориями
    # for category_id in used_categories_ids:
    #     category_number = categories[category_id]
    #     print(f'category_number: {category_number}')
    #     used_categories_ids_sorted_list[int(category_number)] = category_id
    #     print(f'used_categories_ids_sorted_list:\n{used_categories_ids_sorted_list}')
    # # Удаляем из списка элементы, наполненные служебным значением "-5"
    # while -5 in used_categories_ids_sorted_list:
    #     used_categories_ids_sorted_list.remove(-5)
    # print('___ sql_read_used_categories_ids ____FINISH')
    return used_categories_ids


async def sql_read_category(category_id):
    category = cur.execute('SELECT * FROM categories WHERE id IS ?', (category_id,)).fetchall()
    return category


async def sql_delete_category(category_id):
    categories_data = await sql_read_categories()
    exceptions_list = await make_used_categories_ids_list(categories_data)
    if category_id not in exceptions_list:
        # Читаем номер сортировки категории перед удалением
        category_number = cur.execute('SELECT number FROM categories WHERE id IS ?', (category_id,)).fetchall()[0][0]
        # Удаляем категорию
        cur.execute(f"""DELETE FROM categories WHERE id='{category_id}'""")
        # Изменяем поле number для всех категорий, у которых number больше, чем у удаленной категории на -1
        categories_data = cur.execute('SELECT id FROM categories WHERE number > ?', (category_number,)).fetchall()
        for category_data in categories_data:
            next_category_id = category_data[0]
            cur.execute('UPDATE categories SET number=number-1 WHERE id=?', (next_category_id,))
        base.commit()
        return True
    else:
        return False
