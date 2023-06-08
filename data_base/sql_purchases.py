from data_base.sql_main import cur, base, make_text_from_select


async def sql_add_command(purchases_for_add, is_clearing):
    print('___ sql_add_command ____START')
    added_purchases_ids_list = []
    existing_purchases_ids_list = []
    id_list_of_ids = -2
    new_purchases_text = ''
    for new_purchase_name in purchases_for_add:
        existing_purchase_data = cur.execute('SELECT id FROM items001 WHERE name is ?', (new_purchase_name,)).fetchall()
        print(f'existing_purchase_data: {existing_purchase_data}')
        if not existing_purchase_data:
            new_purchases_text += f'{new_purchase_name}\n'
            print(f"{new_purchase_name}, действительно новый товар -- добавляем его в базу")
            cur.execute('INSERT INTO items001 (name) VALUES (?)', (new_purchase_name,))
            added_purchase_id = cur.execute('SELECT id FROM items001 WHERE name IS ?', (new_purchase_name,)).fetchall()[0][0]  # Тип данных индекса: int
            cur.execute("""INSERT INTO link_categories_and_purchases (category_id, purchase_id) VALUES ('-1',?)""",
                        (added_purchase_id,))
            added_purchases_ids_list.insert(0, added_purchase_id)
        else:
            existing_purchases_ids_list.append(existing_purchase_data[0][0])
        print(f'added_purchases_ids_list: {added_purchases_ids_list}')
    if not is_clearing and added_purchases_ids_list:
        print(map(str, added_purchases_ids_list))
        purchases_ids_str = ','.join(map(str, added_purchases_ids_list))
        print(f'purchases_ids_str: {purchases_ids_str}')
        id_list_of_ids_got_by_lastrowid = cur.execute('INSERT INTO items001 (comment) VALUES (?)',
                                                      (purchases_ids_str,)).lastrowid
        print(f'id_list_of_ids_got_by_lastrowid: {id_list_of_ids_got_by_lastrowid}')
        id_list_of_ids = cur.execute('SELECT id FROM items001 WHERE comment IS ?',
                                     (purchases_ids_str,)).fetchall()[0][0]
        print(f'id_list_of_ids, got by SELECT WHERE comment IS...: {id_list_of_ids}')
    base.commit()
    print('___ sql_add_command ____FINISH')
    # Возвращаем индекс, под которым хранятся индексы добавленных покупок:
    return [id_list_of_ids, existing_purchases_ids_list, new_purchases_text]


async def sql_read_list_of_purchases():
    data = cur.execute('SELECT id, name, comment FROM items001').fetchall()
    return data


async def sql_read_purchase(purchase_id):
    purchase_data = cur.execute('SELECT * FROM items001 WHERE id IS ?', (purchase_id,)).fetchall()
    return purchase_data


async def make_text_and_count_of_list_for_category(category_id, specific_purchases_ids_list, counter_starts_from):
    request = 'SELECT link.purchase_id FROM link_categories_and_purchases link, items001 ' \
              'WHERE link.purchase_id=items001.id AND link.category_id=? ORDER BY items001.name;'
    purchases_ids_data = cur.execute(request, (category_id,)).fetchall()
    text_and_count = {}
    purchases_ids_list = []
    for purchase_id_data in purchases_ids_data:
        if specific_purchases_ids_list:
            if purchase_id_data[0] in specific_purchases_ids_list:
                purchases_ids_list.append(purchase_id_data[0])
        else:
            purchases_ids_list.append(purchase_id_data[0])
    text = ''
    row_counter = counter_starts_from
    counter = 1
    for purchase_id in purchases_ids_list:
        purchase_name = cur.execute('SELECT name FROM items001 WHERE id IS ?', (purchase_id,)).fetchall()[0][0]
        text += f'{row_counter}. {purchase_name}'
        if counter != len(purchases_ids_list):
            text += '\n'
            counter += 1
            row_counter += 1
    category_name = cur.execute('SELECT name FROM categories WHERE id=?', (category_id,)).fetchall()[0][0]
    text_and_count.update({'text': text})
    text_and_count.update({'count': len(purchases_ids_list)})
    text_and_count.update({'category_name': f'___{category_name}'})
    return text_and_count


async def sql_make_text_of_list_by_categories(used_categories_ids, purchases_ids_list=[]):
    print('___ sql_make_text_of_list_by_categories ____START')
    text = ''
    categories_length = len(used_categories_ids)
    counter = 1
    counter_starts_from = 1
    print(f'used_categories_ids: {used_categories_ids}')
    for category_id in used_categories_ids:
        if category_id >= 0:
            category = cur.execute('SELECT name FROM categories WHERE id IS ?', (category_id,)).fetchall()[0][0]
        else:
            category = 'Без категории'
        text_and_count_of_list_for_category = await make_text_and_count_of_list_for_category(
            category_id, purchases_ids_list, counter_starts_from)
        counter_starts_from += text_and_count_of_list_for_category['count']
        if text_and_count_of_list_for_category['text'] != '':
            text += f'____ <b>{str(category)}</b> \n'
            text += text_and_count_of_list_for_category['text']
        if counter != categories_length:
            text = text + '\n'
        counter += 1
    print('___ sql_make_text_of_list_by_categories ____FINISH')
    return text


async def sql_update_purchase(purchase_id, purchase_name):
    cur.execute('UPDATE items001 SET name = ? WHERE id IS ?', (purchase_name, purchase_id))
    base.commit()


async def sql_delete_purchase(purchase_id):
    # purchase_id = str(purchase_id)
    all = await sql_read_list_of_purchases()
    cur.execute('DELETE FROM items001 WHERE id=?', (str(purchase_id),))
    cur.execute('DELETE FROM link_categories_and_purchases WHERE purchase_id=?', (str(purchase_id),))
    base.commit()
    if len(all) == 1:
        await sql_add_command(["The list is empty."], is_clearing=True)


async def sql_clear_all():
    cur.execute('DELETE FROM items001')
    cur.execute('DELETE FROM link_categories_and_purchases')
    base.commit()
    return True
