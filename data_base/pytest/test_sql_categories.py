import pytest
from data_base.sql_main import sql_start
from data_base.sql_main import base, cur
from data_base.sql_categories import sql_categorize_or_uncategorize_current_purchase


def sql_prepare():
    purchase_name = 'test_Туалетная бумага'
    cur.execute(
        'INSERT INTO list001 (name) SELECT ? '
        'WHERE NOT EXISTS '
        '(SELECT name FROM list001 WHERE name is ?)',
        (purchase_name, purchase_name))
    purchase_id = cur.execute('SELECT id FROM list001 WHERE name is ?', (purchase_name,)).fetchall()[0][0]

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


def sql_clean(purchase_id, category_id):

    cur.execute('DELETE FROM list001 WHERE id=?', (purchase_id,))

    cur.execute('DELETE FROM link_categories_and_purchases WHERE purchase_id=?', (purchase_id,))

    cur.execute('DELETE FROM categories WHERE id=?', (category_id,))

    base.commit()


@pytest.mark.asyncio
async def test_sql_categorize_current_purchase():
    sql_start()
    purchase_id, category_id = sql_prepare()
    # print(f'\npurchase_id: {purchase_id}')
    # print(f'purchase_id: {category_id}')

    await sql_categorize_or_uncategorize_current_purchase(category_id, purchase_id)
    link_categories_and_purchases_data = \
        cur.execute('SELECT category_id, purchase_id FROM link_categories_and_purchases '
                    'WHERE category_id=? AND purchase_id=?',
                    (category_id, purchase_id,)).fetchall()
    # print(f'\nlink_categories_and_purchases_data:\n{link_categories_and_purchases_data}')
    sql_clean(purchase_id, category_id)
    assert link_categories_and_purchases_data == [(category_id, purchase_id)]
