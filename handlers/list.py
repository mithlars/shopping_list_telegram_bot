from create_bot import bot, dp
from aiogram import types, Dispatcher
from data_base.sql_main import sql_add_command, sql_read_all, sql_delete_shopping, sql_clear_all
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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

async def read_shopping_list(message: types.Message):
    data = await sql_read_all()
    text = ""
    counter = 1
    delete_keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=8)#, one_time_keyboard=True
    for shopping in data:
        button_text = str(counter)
        button_callback_text = f"del {shopping[0]}"
        delete_keyboard.insert(InlineKeyboardButton(text=button_text, callback_data=button_callback_text))

        text = text + f"{str(counter)} {shopping[1]}"
        if shopping[0] != len(data):
            text = text + "\n"
        counter += 1

    await bot.send_message(message.chat.id, text, reply_markup=delete_keyboard)


# async def read_shopping_list(message: types.Message):
#     print("Получили команду на чтение")
#     # text = await sql_read_all()
#     # print("Присвоили результата чтения из базы переменной")
#     # text = text.replace("1 The list", "The list")
#     # await bot.send_message(message.chat.id, text, reply_markup=delete_keyboard)
#     # print("Вывети результат в чат")
#     delete_keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=6)#, one_time_keyboard=True
#     list = await sql_read_all()
#     print("Получили list со списком товаров из базы данных")
#     print("Формируем inline клавиатуру на основании списка")
#     text = ""
#     i = 0
#     buttons_len = 0
#     while i < len(list[0]):
#         button_text = str(i+1)
#         button_callback_text = f"del {str(list[i][0])}"
#         print(f"insert(InlineKeyboardButton(text=" + button_text + ", callback_data=" + button_callback_text + "))")
#         delete_keyboard.insert(InlineKeyboardButton(text=button_text, callback_data=button_callback_text))
#         print(f"Кнопка на удаление из списка \"{str(list[i][0])}\" готова")
#         buttons_len += len(button_callback_text.encode('utf-8')) + len(button_text.encode('utf-8'))
#         text = text + f"{i+1} " + str(list[i][0])
#         if i != len(list) - 1:
#             text = text + "\n"
#         i += 1
#     print("Формирование клавиатуры завершено."
#           "\nОтправляем сообщение с пронумерованным списком товаров и inLine-клавиатурой")
#     print("Суммарная длина кнопок: " + str(buttons_len))
#     await bot.send_message(message.chat.id, text, reply_markup=delete_keyboard)


async def delete_one(message: types.Message):
    shopping = message.text.replace("del ", "")
    await sql_delete_shopping(shopping)
    await read_shopping_list(message)


async def delete_one_inline(callback: types.CallbackQuery):
    shoppingID = callback.data.replace("del ", "")
    await sql_delete_shopping(shoppingID)
    await read_shopping_list(callback.message)


async def delete_all(message: types.Message):
    if await sql_clear_all():
        await message.reply("Список покупок очищен")
        text = []
        text.append("The list is cleared.")
        await sql_add_command(text)


async def request_for_clearing(message: types.Message):
    await message.reply("Если Вы хотите очистить список --нажите эту ссылку /clear_all_the_list\n" \
                        "Если нет -- проигнорируйте это сообщение"
                        )


async def all(message: types.Message):
    shoppingsForAdd = message.text.split("\n")
    await sql_add_command(shoppingsForAdd)
    await sql_delete_shopping("The list is cleared.")
    await read_shopping_list(message)


def register_handlers_list(dp: Dispatcher):
    dp.register_message_handler(start_message, commands=['start', 'help'])

    dp.register_message_handler(read_shopping_list, commands=['list'])
    dp.register_message_handler(read_shopping_list, Text(equals='list', ignore_case=True))

    dp.register_message_handler(delete_one, Text(startswith='del ', ignore_case=True))
    dp.register_callback_query_handler(delete_one_inline, Text(startswith='del '))

    dp.register_message_handler(request_for_clearing, commands=['clear', 'clr'])
    dp.register_message_handler(request_for_clearing, commands=['delete', 'del', 'd'])
    dp.register_message_handler(request_for_clearing, Text(startswith='clear', ignore_case=True))
    dp.register_message_handler(request_for_clearing, Text(equals='clear', ignore_case=True))
    dp.register_message_handler(request_for_clearing, Text(startswith='delet', ignore_case=True))

    dp.register_message_handler(delete_all, commands=['clear_all_the_list'])

    dp.register_message_handler(all)



