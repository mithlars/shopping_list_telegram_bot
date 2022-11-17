from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from create_bot import bot, dp

from data_base.sql_purchases import sql_add_command, sql_read_list_of_purchases, sql_delete_purchase, sql_clear_all
from data_base.sql_purchases import sql_make_text_of_list_by_categories
from data_base.sql_categories import sql_read_used_categories_ids

from keyboards.purchases_kb import main_kb
from keyboards.categories_kb import make_categorize_keyboard
from keyboards.shared_kb import make_delete_from_list_inline_keyboard


async def start_message(message: types.Message):
    await bot.send_message(message.chat.id, "Отправляйте покупки отдельными сообщениями" \
                                            " или каждый пункт с новой строки.\n" \
                                            "Они будут добавлены в список покупок.\n" \
                                            "Например:\n" \
                                            "молоко\n" \
                                            "пиво\n" \
                                            "...\n\n" \
                                            "Для удаления напишите \'del \' и полное наименование" \
                                            "товара из списка (обязательно с проблеом после del)" \
                           , reply_markup=ReplyKeyboardRemove())


async def read_list_of_purchases(message: types.Message):
    used_categories_ids = await sql_read_used_categories_ids()
    text = await sql_make_text_of_list_by_categories(used_categories_ids)
    delete_keyboard_inline = await make_delete_from_list_inline_keyboard(used_categories_ids)
    if text == '':
        await bot.send_message(message.chat.id, 'Список покупок пуст', reply_markup=main_kb)
    else:
        await bot.send_message(message.chat.id, 'Актуальный список покупок:', reply_markup=main_kb)
        await bot.send_message(message.chat.id, text, reply_markup=delete_keyboard_inline)


async def delete_one(message: types.Message):
    purchase_id = message.text.replace("del ", "")
    await sql_delete_purchase(purchase_id)
    await read_list_of_purchases(message)


async def delete_one_inline(callback: types.CallbackQuery):
    purchase_id = callback.data.replace("del ", "")
    await sql_delete_purchase(purchase_id)
    await read_list_of_purchases(callback.message)


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
    await message.answer("Вы хотите очистить список?", reply_markup=keyboard)
    # await message.reply("Если Вы хотите очистить список --нажите эту ссылку /clear_all_the_list\n" \
    #                     "Если нет -- проигнорируйте это сообщение"
    #                     )


async def categorize_all_list(message, id_list_of_ids):
    categorize_keyword = await make_categorize_keyboard(id_list_of_ids)
    text = message.text + '\nВыберите категорию для товара(ов)'
    await bot.send_message(message.chat.id, text, reply_markup=categorize_keyword)


async def all(message: types.Message):
    purchases_for_add = message.text.split("\n")
    id_list_of_ids = await sql_add_command(purchases_for_add, is_clearing=False)
    await categorize_all_list(message, id_list_of_ids)
    data = await sql_read_list_of_purchases()         #    print("Data[0][1] = " + data[0][1])     print("Сейчас весь список выглядит так:\n" + str(data))
    if data[0][1] == 'The list is empty.':      #        print("Отправляем команду на удаление строки о том, что список пуст")
        await sql_delete_purchase(data[0][0])
    # await read_list_of_purchases(message)


def register_handlers_purchases(dp: Dispatcher):
    dp.register_message_handler(start_message, commands=['start', 'help'])

    dp.register_message_handler(read_list_of_purchases, commands=['list'])
    dp.register_message_handler(read_list_of_purchases, Text(equals='Список'))
    dp.register_message_handler(read_list_of_purchases, Text(equals='Покупки'))

    dp.register_message_handler(request_for_clearing, Text(startswith='Очистить', ignore_case=True))
    dp.register_callback_query_handler(delete_all, Text(equals='clear_all_the_list'))

    dp.register_callback_query_handler(delete_one_inline, Text(startswith='del '))

    dp.register_message_handler(all)

