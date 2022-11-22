from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from create_bot import bot, dp

from data_base.sql_purchases import sql_add_command, sql_read_list_of_purchases, sql_delete_purchase, sql_clear_all
from data_base.sql_purchases import sql_make_text_of_list_by_categories
from data_base.sql_categories import sql_read_used_categories_ids

from keyboards.categories_kb import make_categorize_keyboard
from keyboards.purchases_kb import purchase_main_kb, make_purchases_list_inline_keyboard


async def start_message(message: types.Message):
    await bot.send_message(message.chat.id, "Отправляйте покупки отдельными сообщениями"
                                            " или каждый пункт с новой строки.\n"
                                            "Они будут добавлены в список покупок.\n"
                                            "Например:\n"
                                            "молоко\n"
                                            "пиво\n"
                                            "...\n\n"
                                            "Для удаления напишите \'del \' и полное наименование"
                                            "товара из списка (обязательно с проблеом после del)"
                           , reply_markup=purchase_main_kb)


async def read_list_of_purchases(message: types.Message, purchases_ids_list=[]):
    print('read_list_of_purchases____START')
    used_categories_ids = await sql_read_used_categories_ids(purchases_ids_list)
    text = await sql_make_text_of_list_by_categories(used_categories_ids, purchases_ids_list)
    delete_keyboard_inline = await make_purchases_list_inline_keyboard(used_categories_ids, command_text='del ')
    if text == '':
        await bot.send_message(message.chat.id, 'Список покупок пуст', reply_markup=purchase_main_kb)
    else:
        if purchases_ids_list:
            await bot.send_message(message.chat.id, 'Товары, которые уже есть в списке:', reply_markup=purchase_main_kb)
            await bot.send_message(message.chat.id, text)
        else:
            await bot.send_message(message.chat.id, 'Актуальный список покупок:', reply_markup=purchase_main_kb)
            await bot.send_message(message.chat.id, text, reply_markup=delete_keyboard_inline)
    print('read_list_of_purchases____FINISH')


async def delete_one(message: types.Message):
    purchase_id = message.text.replace("del ", "")
    await sql_delete_purchase(purchase_id)
    await read_list_of_purchases(message)


async def delete_one_inline(callback: types.CallbackQuery):
    print('\n***********************************\ndelete_one_inline ____START\n')
    purchase_id = callback.data.replace("del ", "")
    await sql_delete_purchase(purchase_id)
    await read_list_of_purchases(callback.message)
    print('\ndelete_one_inline ____FINISH\n***********************************\n')


async def delete_all(callback: types.CallbackQuery):
    if await sql_clear_all():
        await bot.send_message(callback.message.chat.id, "Список покупок очищен")
        text = []
        text.append("The list is empty.")
        await sql_add_command(text, is_clearing=True)


async def request_for_clearing(message: types.Message):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    keyboard.\
        insert(InlineKeyboardButton(text='Да', callback_data='clear_all_the_list')). \
        insert(InlineKeyboardButton(text='Нет', callback_data='OK'))
    await message.answer("Вы хотите очистить список?", parse_mode='MarkdownV2', reply_markup=keyboard)


async def ok(callback: types.CallbackQuery):
    await callback.message.answer(text='OK', reply_markup=purchase_main_kb)


async def categorize_all_list(message, id_list_of_ids, text):
    print('\ncategorize_all_list')
    categorize_keyboard = await make_categorize_keyboard(id_list_of_ids)
    text = 'Выберите категорию для товара(ов):\n' + text
    await bot.send_message(message.chat.id, text, reply_markup=categorize_keyboard)


async def all_messages(message: types.Message):
    print('\n***********************************\nall_messages ____START\n')
    purchases_for_add = message.text.split("\n")
    id_list_of_ids_and_list_of_existing_purchases = await sql_add_command(purchases_for_add, is_clearing=False)
    print('back into all_messages')
    id_list_of_ids = id_list_of_ids_and_list_of_existing_purchases[0]
    print(f'id_list_of_ids: {id_list_of_ids}')
    existing_purchases_ids_list = id_list_of_ids_and_list_of_existing_purchases[1]
    print(f'existing_purchases_ids_list: {existing_purchases_ids_list}')
    text = id_list_of_ids_and_list_of_existing_purchases[2]
    if id_list_of_ids > 0:
        if existing_purchases_ids_list:
            await read_list_of_purchases(message, existing_purchases_ids_list)
        await categorize_all_list(message, id_list_of_ids, text)
        data = await sql_read_list_of_purchases()
        if data[0][1] == 'The list is empty.':
            await sql_delete_purchase(data[0][0])
    elif id_list_of_ids < 0:
        if existing_purchases_ids_list:
            await bot.send_message(message.chat.id, 'Все эти товары уже есть в списке:', reply_markup=purchase_main_kb)
            await read_list_of_purchases(message)
    print('\nall_messages ____FINISH\n***********************************\n')



def register_handlers_purchases(dp: Dispatcher):
    dp.register_message_handler(start_message, commands=['start', 'help'])
    dp.register_message_handler(start_message, Text(equals='Помощь'))

    dp.register_message_handler(read_list_of_purchases, commands=['list'])
    dp.register_message_handler(read_list_of_purchases, Text(equals='Список'))
    dp.register_message_handler(read_list_of_purchases, Text(equals='Покупки'))

    dp.register_message_handler(request_for_clearing, Text(startswith='Очистить', ignore_case=True))
    dp.register_callback_query_handler(delete_all, Text(equals='clear_all_the_list'))
    dp.register_callback_query_handler(ok, Text(equals='OK'))

    dp.register_callback_query_handler(delete_one_inline, Text(startswith='del '))

    dp.register_message_handler(all_messages)

