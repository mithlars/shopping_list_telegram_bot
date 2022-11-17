from aiogram import types, Dispatcher
from create_bot import bot
from keyboards.categories_kb import categories_kb
from keyboards.shared_kb import *
from data_base.sql_categories import *
# from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from handlers.list_of_purchases import read_list_of_purchases


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
    categories_count = len(await sql_read_categories())
    category_id = callback.data.replace("category_remove ", "")              # print(f"Удаляем категорию под id: '{category_id}'")
    is_deleted = await sql_delete_category(category_id)
    if is_deleted:
        if categories_count == 1:
            await sql_add_category('The list is empty.', '')
    else:
        bot.send_message(callback.message.chat.id, 'Категория уже используется\n')
    await list_for_delete_som_category(callback.message)


async def categorize(callback: types.CallbackQuery):
    print('Категоризируем')
    data = callback.data.replace('categorize ', '').split(' ')
    id_of_list_of_purchases_ids = data[0]
    category_id = data[1]
    await sql_categorize(id_of_list_of_purchases_ids, category_id)
    await read_list_of_purchases(callback.message)


def register_handlers_categories(dp: Dispatcher):
    dp.register_message_handler(list_of_categories, Text(equals='Категории', ignore_case=True))
    dp.register_message_handler(list_of_categories, Text(equals='Обновить кат.', ignore_case=True))

    dp.register_message_handler(list_for_delete_som_category, Text(equals='Удалить кат.', ignore_case=True))
    dp.register_callback_query_handler(delete_current_category_inline, Text(startswith='category_remove', ignore_case=True))

    dp.register_callback_query_handler(categorize, Text(startswith='categorize '))