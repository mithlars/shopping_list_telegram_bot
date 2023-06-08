import pytest
from data_base.sql_main import sql_start
from data_base.sql_main import base, cur
from data_base.sql_categories import sql_categorize_or_uncategorize_current_purchase, make_used_categories_ids_list


def sql_prepare_for_test_sql_categorize_current_purchase():
    purchase_name = 'test_Туалетная бумага'
    cur.execute(
        'INSERT INTO items001 (name) SELECT ? '
        'WHERE NOT EXISTS '
        '(SELECT name FROM items001 WHERE name is ?)',
        (purchase_name, purchase_name))
    purchase_id = cur.execute('SELECT id FROM items001 WHERE name is ?', (purchase_name,)).fetchall()[0][0]

    category_name = 'test_Инструменты'
    cur.execute(
        'INSERT INTO categories (name) SELECT ? '
        'WHERE NOT EXISTS '
        '(SELECT name FROM categories WHERE name is ?)',
        (category_name, category_name))
    category_id = cur.execute('SELECT id FROM categories WHERE name is ?', (category_name,)).fetchall()[0][0]

    none_category_id = -1
    cur.execute('INSERT INTO link_categories_and_purchases (category_id, purchase_id) VALUES (?,?)',
                (none_category_id, purchase_id))
    cur.execute('INSERT INTO link_categories_and_purchases (category_id, purchase_id) SELECT ?,?'
                'WHERE NOT EXISTS '
                '(SELECT category_id, purchase_id FROM link_categories_and_purchases '
                'WHERE category_id=? AND purchase_id=?)',
                (category_id, purchase_id,
                 category_id, purchase_id))
    return purchase_id, category_id


def sql_clean_for_test_sql_categorize_current_purchase(purchase_id, category_id):

    cur.execute('DELETE FROM items001 WHERE id=?', (purchase_id,))

    cur.execute('DELETE FROM link_categories_and_purchases WHERE purchase_id=?', (purchase_id,))

    cur.execute('DELETE FROM categories WHERE id=?', (category_id,))

    base.commit()


@pytest.mark.asyncio
async def test_sql_categorize_current_purchase():
    sql_start()
    purchase_id, category_id = sql_prepare_for_test_sql_categorize_current_purchase()
    # print(f'\npurchase_id: {purchase_id}')
    # print(f'purchase_id: {category_id}')

    await sql_categorize_or_uncategorize_current_purchase(category_id, purchase_id)
    link_categories_and_purchases_data = \
        cur.execute('SELECT category_id, purchase_id FROM link_categories_and_purchases '
                    'WHERE category_id=? AND purchase_id=?',
                    (category_id, purchase_id,)).fetchall()
    # print(f'\nlink_categories_and_purchases_data:\n{link_categories_and_purchases_data}')
    sql_clean_for_test_sql_categorize_current_purchase(purchase_id, category_id)
    assert link_categories_and_purchases_data == [(category_id, purchase_id)]


def sql_prepare_for_test_make_used_categories_ids_list():
    categories_names = [
        'Продукты',
        'Алкоголь',
        'Фрукты',
        'Овощи'
    ]
    categories_ids = []

    purchases_names = [
        'Хлеб',
        'Вино',
        'Яблоки',
        'Картошка'
    ]
    purchases_ids = []

    for i in range(len(categories_names)):
        cur.execute('INSERT INTO categories (name, number) VALUES (?, ?)', (categories_names[i], i + 1))
        category_id = cur.execute('SELECT id FROM categories WHERE name=?', (categories_names[i],)).fetchall()[0][0]
        categories_ids.append(category_id)
        cur.execute('INSERT INTO items001 (name) VALUES (?)', (purchases_names[i],))
        purchase_id = cur.execute('SELECT id FROM items001 WHERE name=?', (purchases_names[i],)).fetchall()[0][0]
        purchases_ids.append(purchase_id)

    for i in range(len(categories_names)):

        cur.execute('INSERT INTO link_categories_and_purchases (category_id, purchase_id) VALUES (?, ?)',
                    (categories_ids[i * -1], purchases_ids[i]))



    category_name = 'Электроника'
    purchase_name = 'Таблетки от жадности'
    cur.execute('INSERT INTO categories (name, number) VALUES (?, ?)', (category_name, len(categories_names) + 1))
    category_id = cur.execute('SELECT id FROM categories WHERE name=?', (category_name,)).fetchall()[0][0]
    cur.execute('INSERT INTO items001 (name) VALUES (?)', (purchase_name,))
    purchase_id = cur.execute('SELECT id FROM items001 WHERE name=?', (purchase_name,)).fetchall()[0][0]

    base.commit()
    return categories_ids, purchases_ids, category_id, purchase_id


def sql_clear_for_test_make_used_categories_ids_list(categories_ids, purchases_ids, category_id, purchase_id):
    purchases_ids.append(purchase_id)
    for purchase_id in purchases_ids:
        cur.execute('DELETE FROM items001 WHERE id=?', (purchase_id,))
        cur.execute('DELETE FROM link_categories_and_purchases WHERE purchase_id=?', (purchase_id,))

    categories_ids.append(category_id)
    for category_id in categories_ids:
        cur.execute('DELETE FROM categories WHERE id=?', (category_id,))

    base.commit()


@pytest.mark.asyncio
async def test_make_used_categories_ids_list():
    sql_start()
    categories_ids, purchases_ids, category_id, purchase_id = sql_prepare_for_test_make_used_categories_ids_list()

    categories_data = cur.execute('SELECT * FROM categories').fetchall()
    print(f'\n\ncategories_data:\n{categories_data}')
    used_categories_ids_sorted_list = await make_used_categories_ids_list(categories_data)
    print(f'used_categories_ids_sorted_list:\n{used_categories_ids_sorted_list}')

    sql_clear_for_test_make_used_categories_ids_list(categories_ids, purchases_ids, category_id, purchase_id)
