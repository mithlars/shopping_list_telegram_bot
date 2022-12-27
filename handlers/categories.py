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
        exceptions_list = await make_categories_delete_exceptions_list(data)
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
    category_id = callback.data.replace("category_remove ", "")              # print(f"Удаляем категорию под id: '{category_id}'")
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
    purchases_ids_str = cur.execute('SELECT comment FROM list001 WHERE id IS ?',
                                (id_of_list_of_purchases_ids,)).fetchall()[0][0]
    # categorizable_purchase_id = purchases_ids_str.split(',')[0]
    # categorizable_purchase_name = cur.execute("SELECT name FROM list001 WHERE id IS ?",
    #                                           (categorizable_purchase_id,)).fetchall()[0][0]
    purchases_ids_str += ',-50'
    cur.execute("UPDATE list001 SET comment=? WHERE id=?", (purchases_ids_str, id_of_list_of_purchases_ids))
    base.commit()
    if callback.message is not None:  # строчка для теста, чтобы тест не спотыкался о то, что ет атрибута chat
        await categorize_all_list(callback.message, id_of_list_of_purchases_ids, '')
    # categorize_keyboard = await make_categorize_keyboard(id_of_list_of_purchases_ids)
    # categorize_keyboard["inline_keyboard"].pop(-1)    # Удаляем из клавиатуры кнопку "Разные категории"
    # message_text = 'Выберите категорию для товара:\n' + categorizable_purchase_name
    # if callback.message is not None:  # строчка для теста, чтобы тест не спотыкался о то, что ет атрибута chat
    #     await bot.send_message(callback.message.chat.id, message_text, reply_markup=categorize_keyboard)


# Нужно изменить категоризирование так, чтобы можно было добавить несколько категорий для каждой покупки
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


def register_handlers_categories(dp: Dispatcher):
    dp.register_message_handler(list_of_categories, Text(equals='Категории', ignore_case=True))
    dp.register_message_handler(list_of_categories, Text(equals='Обновить кат.', ignore_case=True))

    dp.register_message_handler(list_for_delete_som_category, Text(equals='Удалить кат.', ignore_case=True))
    dp.register_callback_query_handler(delete_current_category_inline, Text(startswith='category_remove', ignore_case=True))

    dp.register_callback_query_handler(categorize, Text(startswith='categorize '))
    dp.register_callback_query_handler(dif_categorize, Text(startswith='dif_categorize '))

