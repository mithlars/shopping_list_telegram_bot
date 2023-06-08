from aiogram import types, Dispatcher
from create_bot import bot
from keyboards.categories_kb import *
from keyboards.shared_kb import *
from data_base.sql_categories import *
from aiogram.dispatcher.filters import Text
from handlers.purchases_list import read_list_of_purchases, categorize_all_list


async def list_of_categories(message: types.Message):
    categories_data = await sql_read_categories()
    categories_text = await make_text_from_select(categories_data, counter_starts_from=1)
    if categories_text == 'The list is empty.':
        await bot.send_message(message.chat.id, 'Список категорий пуст.', reply_markup=categories_kb)
    else:
        await bot.send_message(message.chat.id, 'Список категорий:')
        await bot.send_message(message.chat.id, categories_text, reply_markup=categories_kb)


async def list_for_delete_som_category(message: types.Message):
    data = await sql_read_categories()
    categories_text = await make_text_from_select(data, 1)
    if categories_text == 'The list is empty.':
        await bot.send_message(message.chat.id, 'Список категорий пуст.', reply_markup=categories_kb)
    else:
        exceptions_list = await make_used_categories_ids_list(data)
        delete_keyboard_buttons_and_counter = await make_inline_keyboard_and_buttons_list(data, 'category_remove ', exceptions_list, 1)
        delete_keyboard = delete_keyboard_buttons_and_counter['keyboard']
        delete_keyboard_buttons_counter = delete_keyboard_buttons_and_counter['buttons_counter']

        if delete_keyboard_buttons_counter == 0:
            message_text = '\nИспользуемые категории нельзя удалить\nВсе категории используются.\n.'
            await message.reply(message_text, reply_markup=categories_kb)
            await list_of_categories(message)
        elif delete_keyboard_buttons_counter != len(data):
            categories_text += '\nИспользуемые категории нельзя удалить'
            await bot.send_message(message.chat.id, 'Список категорий:', reply_markup=categories_kb)
            await bot.send_message(message.chat.id, categories_text, reply_markup=delete_keyboard)
        else:
            await bot.send_message(message.chat.id, 'Список категорий:', reply_markup=categories_kb)
            await bot.send_message(message.chat.id, categories_text, reply_markup=delete_keyboard)


async def delete_current_category_inline(callback: types.CallbackQuery):
    print('\n***********************************\ndelete_current_category_inline ____START\n')
    categories_count = len(await sql_read_categories())
    category_id = callback.data.replace("category_remove ", "")  # print(f"Удаляем категорию под id: '{category_id}'")
    is_deleted = await sql_delete_category(category_id)
    if is_deleted:
        if categories_count == 1:
            await sql_add_category('The list is empty.', '')
    else:
        bot.send_message(callback.message.chat.id, 'Категория уже используется\n')
    await list_for_delete_som_category(callback.message)
    print('\ndelete_current_category_inline ____FINISH\n***********************************\n')


async def dif_categorize(callback: types.CallbackQuery):
    id_of_list_of_purchases_ids = callback.data.replace('dif_categorize ', '')
    purchases_ids_str = cur.execute('SELECT comment FROM items001 WHERE id IS ?',
                                (id_of_list_of_purchases_ids,)).fetchall()[0][0]
    purchases_ids_str += ',-50'
    cur.execute("UPDATE items001 SET comment=? WHERE id=?", (purchases_ids_str, id_of_list_of_purchases_ids))
    base.commit()
    if callback.message is not None:  # строчка для теста, чтобы тест не спотыкался о то, что ет атрибута chat
        await categorize_all_list(callback.message, id_of_list_of_purchases_ids, '')


async def categorize(callback: types.CallbackQuery):
    print('\n***********************************\ncategorize ____START\n')
    print(callback.data)
    data = callback.data.replace('categorize ', '').split(' ')
    id_of_list_of_purchases_ids = data[0]
    category_id = data[1]
    purchase_name = await sql_categorize(id_of_list_of_purchases_ids, category_id)
    if purchase_name != '':  # Значит есть еще новые товары, которые следует категоризировать
        await categorize_all_list(callback.message, id_of_list_of_purchases_ids, '')
    else:
        await read_list_of_purchases(callback.message)
    print('\ncategorize ____FINISH\n***********************************\n')


async def uncategorize(callback: types.CallbackQuery):
    ids_list = callback.data.replace('uncategorize ', '').split(' ')
    category_id = ids_list[0]
    category_name = cur.execute('SELECT name FROM categories WHERE id IS ?', (category_id,)).fetchall()[0][0]
    purchase_id = ids_list[1]
    purchase_name = cur.execute('SELECT name FROM items001 WHERE id IS ?', (purchase_id,)).fetchall()[0][0]
    await sql_categorize_or_uncategorize_current_purchase(category_id, purchase_id, uncategorize=True)
    await bot.send_message(callback.message.chat.id, f'Была удалена связь товара {purchase_name} с категорией {category_name}.')
    await read_list_of_purchases(callback.message, [])


async def sort_categories(message: types.Message):
    print('\n***********************************\nsort_categories ____START\n')
    categories_data = cur.execute("SELECT id, name, number FROM categories ORDER BY number").fetchall()
    print(f'categories_data:\n{categories_data}')
    categories_sort_keyboard = await make_categories_sorting_inline_keyboard(categories_data)
    await bot.send_message(message.chat.id,
                           "Выберите действия для изменения сортировки категорий:",
                           reply_markup=categories_sort_keyboard
                           )
    print('\nsort_categories ____FINISH\n***********************************\n')


async def categories_sorting_move_callback_move(callback_query: types.CallbackQuery):
    categories_data = cur.execute("SELECT id, name, number FROM categories ORDER BY number").fetchall()
    category_id, direction = callback_query.data.split(" ")[1:]
    cur.execute("SELECT number FROM categories WHERE id=?", (category_id,))
    current_sort_number = cur.fetchone()[0]
    if direction == "up":
        if current_sort_number > 0:
            cur.execute("UPDATE categories SET number=number+1 WHERE number=?", (current_sort_number-1,))
            cur.execute("UPDATE categories SET number=? WHERE id=?", (current_sort_number - 1, category_id))
    else:
        if current_sort_number < len(categories_data):
            cur.execute("UPDATE categories SET number=number-1 WHERE number=?", (current_sort_number+1,))
            cur.execute("UPDATE categories SET number=? WHERE id=?", (current_sort_number + 1, category_id))
    base.commit()
    print(f'categories_data:\n{categories_data}')
    categories_data = cur.execute("SELECT id, name, number FROM categories ORDER BY number").fetchall()
    categories_sort_keyboard = await make_categories_sorting_inline_keyboard(categories_data)
    await bot.edit_message_reply_markup(callback_query.message.chat.id,
                                        callback_query.message.message_id,
                                        reply_markup=categories_sort_keyboard)


def register_handlers_categories(dp: Dispatcher):
    dp.register_message_handler(list_of_categories, Text(equals='Категории', ignore_case=True))
    dp.register_message_handler(list_of_categories, Text(equals='📁', ignore_case=True))
    dp.register_message_handler(list_of_categories, Text(equals='Обновить кат.', ignore_case=True))

    dp.register_message_handler(list_for_delete_som_category, Text(equals='Удалить кат.', ignore_case=True))
    dp.register_callback_query_handler(delete_current_category_inline, Text(startswith='category_remove', ignore_case=True))

    dp.register_callback_query_handler(categorize, Text(startswith='categorize '))
    dp.register_callback_query_handler(dif_categorize, Text(startswith='dif_categorize '))

    dp.register_callback_query_handler(uncategorize, Text(startswith='uncategorize '))

    dp.register_message_handler(sort_categories, Text(startswith='Сортировка категорий'))
    dp. register_callback_query_handler(categories_sorting_move_callback_move, Text(startswith='category_sorting_move'))

