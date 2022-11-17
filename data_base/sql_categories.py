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
    purchases_ids_str = cur.execute('SELECT comment FROM list001 WHERE id IS ?',
                                    (str(id_of_list_of_purchases_ids),)).fetchall()[0][0]
    cur.execute('DELETE FROM list001 WHERE id IS ?', (str(id_of_list_of_purchases_ids),))        # print("Удаляем из строки со списком индексов скобки")
    purchases_ids_str = str(purchases_ids_str).replace("[", "").replace(']', "")
    # print("Строка со списком индексов после удаления скобок: " + indexes_str)         print("Разделяем строку на массив индексов")

    purchases_ids_list = purchases_ids_str.split(", ")
    # for purchase_id in purchases_ids_list: # Цикл для преобразования массива строк в массив цифр
    #     purchase_index = purchases_ids_list.index(purchase_id)  # Получаем индекс элемента массива
    #     purchases_ids_list[purchase_index] = int(purchases_ids_list[purchase_index])  # Преобразуем тип элемента массива в int

    for purchase_id in purchases_ids_list:
        cur.execute("INSERT INTO link_categories_and_purchases (category_id, purchase_id) VALUES (?, ?)",
                    (category_id, int(purchase_id)))
    base.commit()


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


async def sql_read_used_categories_ids():
    # data = cur.execute('SELECT DISTINCT category_id FROM list001 WHERE category_id IS NOT NULL').fetchall()
    used_categories_ids_data = cur.execute('SELECT DISTINCT category_id FROM link_categories_and_purchases').fetchall()
    used_categories_ids = []
    for category_id_data in used_categories_ids_data:
        used_categories_ids.append(category_id_data[0])
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