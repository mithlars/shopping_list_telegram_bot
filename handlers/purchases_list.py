from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from create_bot import bot, dp

from data_base.sql_main import cur, base
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
                                            "товара из списка (обязательно с пробелом после del)"
                           , reply_markup=purchase_main_kb)


async def read_list_of_purchases(message: types.Message, purchases_ids_list=[]):
    print('___ read_list_of_purchases ____START')
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
            await bot.send_message(message.chat.id, text, reply_markup=delete_keyboard_inline, parse_mode="HTML")
    print('___ read_list_of_purchases ____FINISH')


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


async def categorize_all_list(message, id_of_list_of_purchases_ids, new_purchases_text, in_category=False):
    print('\n***********************************\ncategorize_all_list ____START\n')
    purchases_ids_str = cur.execute('SELECT comment FROM list001 WHERE id IS ?',
                                (id_of_list_of_purchases_ids,)).fetchall()[0][0]
    purchases_ids_list = purchases_ids_str.split(',')
    print(f'purchases_ids_list: {purchases_ids_list}')
    if purchases_ids_list[-1] == '-50':
        dif_button = False
        categorizable_purchase_id = purchases_ids_list[0]
        categorizable_purchase_name = cur.execute("SELECT name FROM list001 WHERE id IS ?",
                                                  (categorizable_purchase_id,)).fetchall()[0][0]
        message_text = f'{categorizable_purchase_name}'
    else:
        if len(purchases_ids_list) == 1:
            dif_button = False
            message_text = new_purchases_text
        else:
            dif_button = True
            message_text = new_purchases_text

    categorize_keyboard = await make_categorize_keyboard(id_of_list_of_purchases_ids, dif_button=dif_button)
    print(f'categorize_keyboard:')
    i = 1
    for key in categorize_keyboard["inline_keyboard"][0]:
        print(f'key{i}: {key}')
        i += 1

    print(f'message_text:\n{message_text}')
    if message.chat != 'test':  # Строчка для теста, чтобы тест не спотыкался о то, что ет атрибута chat
        if not in_category:
            categorize_keyboard.add(
                InlineKeyboardButton(text='Отмена', callback_data=f'cancel_adding_purchases {id_of_list_of_purchases_ids}'))
        await bot.send_message(message.chat.id, 'Выберите категорию для товара', reply_markup=purchase_main_kb)
        await bot.send_message(message.chat.id, message_text, reply_markup=categorize_keyboard)
    else:
        return categorize_keyboard, message_text
    print('\ncategorize_all_list ____FINISH\n***********************************\n')


async def all_messages(message: types.Message):
    print('\n***********************************\nall_messages ____START\n')
    purchases_for_add = message.text.splitlines()
    id_list_of_ids_and_list_of_existing_purchases = await sql_add_command(purchases_for_add, is_clearing=False)
    print('back into all_messages')
    id_list_of_ids = id_list_of_ids_and_list_of_existing_purchases[0]
    print(f'id_list_of_ids: {id_list_of_ids}')
    existing_purchases_ids_list = id_list_of_ids_and_list_of_existing_purchases[1]
    print(f'existing_purchases_ids_list: {existing_purchases_ids_list}')
    new_purchases_text = id_list_of_ids_and_list_of_existing_purchases[2]
    if id_list_of_ids > 0:
        if existing_purchases_ids_list:
            await read_list_of_purchases(message, existing_purchases_ids_list)
        await categorize_all_list(message, id_list_of_ids, new_purchases_text)
        data = await sql_read_list_of_purchases()
        if data[0][1] == 'The list is empty.':
            await sql_delete_purchase(data[0][0])
    elif id_list_of_ids < 0:
        await bot.send_message(message.chat.id, 'Все эти товары уже есть в списке', reply_markup=purchase_main_kb)
        await read_list_of_purchases(message)
    print('\nall_messages ____FINISH\n***********************************\n')



async def cancel_adding_purchases(callback: types.CallbackQuery):
    id_of_list_of_purchases_ids = callback.data.split()[1]
    purchases_ids_data = cur.execute('SELECT comment FROM list001 WHERE id IS ?', (id_of_list_of_purchases_ids,)).fetchall()
    purchases_ids_list = purchases_ids_data[0][0].split(',')
    for purchase_id in purchases_ids_list:
        await sql_delete_purchase(purchase_id)
    await bot.send_message(callback.message.chat.id, 'OK', reply_markup=purchase_main_kb)
    await read_list_of_purchases(callback.message)


def register_handlers_purchases(dp: Dispatcher):
    dp.register_message_handler(start_message, commands=['start', 'help'])
    dp.register_message_handler(start_message, Text(equals='Помощь'))
    dp.register_message_handler(start_message, Text(equals='❓'))

    dp.register_message_handler(read_list_of_purchases, commands=['list'])
    dp.register_message_handler(read_list_of_purchases, Text(equals='Список'))
    dp.register_message_handler(read_list_of_purchases, Text(equals='📜'))
    dp.register_message_handler(read_list_of_purchases, Text(equals='Покупки'))

    dp.register_message_handler(request_for_clearing, Text(startswith='Очистить', ignore_case=True))
    dp.register_message_handler(request_for_clearing, Text(startswith='🧹', ignore_case=True))
    dp.register_callback_query_handler(delete_all, Text(equals='clear_all_the_list'))
    dp.register_callback_query_handler(ok, Text(equals='OK'))

    dp.register_callback_query_handler(delete_one_inline, Text(startswith='del '))

    dp.register_message_handler(all_messages)
    dp.register_callback_query_handler(cancel_adding_purchases, Text(startswith='cancel_adding_purchases'))

