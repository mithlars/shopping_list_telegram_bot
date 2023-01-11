import pytest
from aiogram import types
from handlers.category_in_out import *
from data_base.sql_main import sql_start
from data_base.sql_main import base, cur

# !!!!! test_purchases и test_categories должны быть одной длинны
test_purchases = ['test_молоко', 'test_кофе']
test_categories = ['test_Продукты', 'test_Канцелярия']
test_purchases_ids = []
test_categories_ids = []

test_purchases_uncategorized = ['test_картошка', 'test_свекла']
test_purchases_uncategorized_ids = []


def sql_prepare():

    # Добавляем в Базу данных покупки из test_purchases и записываем их id в test_purchases_ids
    for purchase_name in test_purchases:
        cur.execute(
            'INSERT INTO list001 (name) SELECT ? '
            'WHERE NOT EXISTS '
            '(SELECT * FROM list001 WHERE name is ?)',
            (purchase_name, purchase_name))
        purchase_id = cur.execute('SELECT id FROM list001 WHERE name is ?', (purchase_name,)).fetchall()[0][0]
        test_purchases_ids.append(purchase_id)

    # Добавляем в Базу данных покупки из test_purchases_uncategorized
    # и записываем их id в test_purchases_uncategorized_ids
    for purchase_name in test_purchases_uncategorized:
        cur.execute(
            'INSERT INTO list001 (name) SELECT ? '
            'WHERE NOT EXISTS '
            '(SELECT * FROM list001 WHERE name is ?)',
            (purchase_name, purchase_name))
        purchase_id = cur.execute('SELECT id FROM list001 WHERE name is ?', (purchase_name,)).fetchall()[0][0]
        test_purchases_uncategorized_ids.append(purchase_id)

    # Добавляем в Базу данных категории из test_categories и записываем их id в test_categories_ids
    for category_name in test_categories:
        cur.execute(
            'INSERT INTO categories (name) SELECT ? '
            'WHERE NOT EXISTS '
            '(SELECT * FROM categories WHERE name is ?)',
            (category_name, category_name))
        category_id = cur.execute('SELECT id FROM categories WHERE name is ?', (category_name,)).fetchall()[0][0]
        test_categories_ids.append(category_id)

    # добавляем в базу данных связь между покупками из test_purchases_ids
    # и категориями из test_categories_ids
    i = 0
    while i < len(test_purchases_ids):
        purchase_id = test_purchases_ids[i]
        category_id = test_categories_ids[0]
        cur.execute('INSERT INTO link_categories_and_purchases (category_id, purchase_id) VALUES (?,?)',
                    (category_id, purchase_id))
        i += 1

    # добавляем в базу данные связь между покупками из test_purchases_uncategorized_ids
    # и категорией "Без категории"
    i = 0
    while i < len(test_purchases_uncategorized_ids):
        purchase_id = test_purchases_uncategorized_ids[i]
        category_id = -1
        cur.execute('INSERT INTO link_categories_and_purchases (category_id, purchase_id) VALUES (?,?)',
                    (category_id, purchase_id))
        i += 1

    base.commit()


def sql_clean():

    for purchase_id in test_purchases_ids:
        cur.execute('DELETE FROM list001 WHERE id=?', (purchase_id,))
        cur.execute('DELETE FROM link_categories_and_purchases WHERE purchase_id=?', (purchase_id,))

    for purchase_id in test_purchases_uncategorized_ids:
        cur.execute('DELETE FROM list001 WHERE id=?', (purchase_id,))
        cur.execute('DELETE FROM link_categories_and_purchases WHERE purchase_id=?', (purchase_id,))

    for category_id in test_categories_ids:
        cur.execute('DELETE FROM categories WHERE id=?', (category_id,))

    base.commit()


# OK
@pytest.mark.asyncio
async def test_in_category_from_which_category():
    sql_start()
    sql_prepare()
    message = types.Message()
    returned = await in_category_from_which_category(message, test=True)
    print(f'\n\nreturned:\n{returned}')
    keyboard = returned['keyboard']
    text = returned['text']

    print(f'\nkeyboard:')
    i = 1
    for key in keyboard["inline_keyboard"][0]:
        print(f'key{i}: {key}')
        i += 1
    print(f'\n\nTEXT:\n{text}')
    sql_clean()


# OK
@pytest.mark.asyncio
async def test_categorize_all_single():
    sql_start()
    sql_prepare()
    callback_query = types.CallbackQuery()

    returned = await categorize_all_single(callback_query, test=True)
    print(f'\n{returned}')
    id_list_of_uncategorized_purchases_ids = returned['id_list_of_uncategorized_purchases_ids']
    cur.execute('DELETE FROM list001 WHERE id=?', (id_list_of_uncategorized_purchases_ids,))

    sql_clean()


# OK
@pytest.mark.asyncio
async def test_in_category_which_purchase():
    sql_start()
    sql_prepare()
    callback_query = types.CallbackQuery()
    callback_query.data = f'in_category_which_purchase {test_categories_ids[0]}'
    returned = await in_category_which_purchase(callback_query, test=True)
    print('\n\nreturned:\n')
    for element in returned:
        if element != 'keyboard':
            print(f'{element}:\n{returned[element]}\n')
        else:
            print(f'{element}:\n')
            count = 1
            for key in returned[element]['inline_keyboard'][0]:
                print(f'key {count}: {key}')

    sql_clean()


# IN PROGRES
@pytest.mark.asyncio
async def test_in_category_in_which_category():
    sql_start()
    sql_prepare()
    callback = types.CallbackQuery()
    callback.data = f'in_category_in_which_category {test_purchases_ids[0]}'
    returned = await in_category_in_which_category(callback, test=True)
    message_text = returned['text']
    print(f'\nmessage_text:\n{message_text}')
    keys = returned['keyboard']['inline_keyboard'][0]
    count = 1
    for key in keys:
        print(f'key_{count}: {key}')

    sql_clean()


# OK
@pytest.mark.asyncio
async def test_in_category_categorize():
    sql_start()
    sql_prepare()
    category_id = test_categories_ids[0]
    purchase_id = test_purchases_ids[0]
    callback = types.CallbackQuery()
    callback.data = f'in_category_finish {category_id} {purchase_id}'
    print(f'\ncallback:\n{callback}')
    await in_category_categorize(callback, test=True)
    link_data = cur.execute('SELECT category_id, purchase_id FROM link_categories_and_purchases '
                            'WHERE category_id IS ? AND purchase_id IS ?', (category_id, purchase_id)).fetchall()
    print(f'\nlink_data:\n{link_data}')
    sql_clean()


# @pytest.mark.asyncio
# async def test_():
#     pass

