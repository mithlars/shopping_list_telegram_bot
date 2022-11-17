from data_base.sql_main import cur, base, make_text_from_select
from data_base.sql_categories import sql_read_used_categories_ids


async def sql_add_command(purchases_for_add, is_clearing):
    indexes_list = []
    index = -1
    for purchase in purchases_for_add:
        cur.execute('INSERT INTO list001 (name) VALUES (?)', (purchase,))
        current_index = cur.execute('SELECT id FROM list001 WHERE name IS ?', (purchase,)).fetchall()[0][0] # Тип данных индекса: int
        indexes_list.insert(0, current_index)
        #        print("Тип данных текущего индекса товара из списка: " + str(type(current_index)))
        #        print("добавили " + shopping)
        # print("Получили массив индексов товаров, добавленных в базу данных:\n" + str(index_list) + "\n")
    if not is_clearing:
        cur.execute('INSERT INTO list001 (comment) VALUES (?)', (str(indexes_list),))
        index = cur.execute('SELECT id FROM list001 WHERE comment IS ?', (str(indexes_list),)).fetchall()[0][0] #        print("Массив индексов содержется в таблице под индексом: " + str(index))
    base.commit()
    return index        # Возвращаем индекс, под которым хранятся индексы добавленных покупок



async def sql_read_list_of_purchases():
    data = cur.execute('SELECT id, name, comment FROM list001').fetchall()
    return data


async def make_text_and_count_of_list_for_category(category_id, counter_starts_from):
    purchases_ids_data = cur.execute('SELECT purchase_id FROM link_categories_and_purchases WHERE category_id IS ?',
                                     (category_id,))
    text_and_count = {}
    purchases_ids_list = []
    for purchase_id_data in purchases_ids_data:
        purchases_ids_list.append(purchase_id_data[0])

    text = ''
    counter_row_text = counter_starts_from
    counter = 1
    for purchase_id in purchases_ids_list:
        purchase_name = cur.execute('SELECT name FROM list001 WHERE id IS ?', (purchase_id,)).fetchall()[0][0]
        text += f'{counter_row_text}. {purchase_name}'
        if counter != len(purchases_ids_list):
            text += '\n'
            counter += 1
            counter_row_text += 1
    text_and_count.update({'text': text})
    text_and_count.update({'count': len(purchases_ids_list)})
    return text_and_count


async def sql_make_text_of_list_by_categories(used_categories_ids):
    text = ''
    categories_length = len(used_categories_ids)
    counter = 1
    counter_starts_from = 1
    for category_id in used_categories_ids:
        category = cur.execute('SELECT name FROM categories WHERE id IS ?', (category_id,)).fetchall()[0][0]
        text = text + '____  ' + str(category) + ' ______________' + '\n'
        text_and_count_of_list_for_category = await make_text_and_count_of_list_for_category(
                                                                category_id, counter_starts_from=counter_starts_from)
        counter_starts_from += text_and_count_of_list_for_category['count']
        text = text + text_and_count_of_list_for_category['text']
        if counter != categories_length:
            text = text + '\n'
        counter += 1
    return text


async def sql_delete_purchase(purchase_id):
    # purchase_id = str(purchase_id)
    all = await sql_read_list_of_purchases()
    cur.execute('DELETE FROM list001 WHERE id=?', (str(purchase_id),))
    cur.execute('DELETE FROM link_categories_and_purchases WHERE purchase_id=?', (str(purchase_id),))
    base.commit()
    if len(all) == 1:
        await sql_add_command(["The list is empty."], is_clearing=True)


async def sql_clear_all():
    cur.execute('DELETE FROM list001')
    cur.execute('DELETE FROM link_categories_and_purchases')
    base.commit()
    return True

