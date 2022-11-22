from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from data_base.sql_main import *
from data_base.sql_categories import *


categories_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
categories_b1 = KeyboardButton(text='Добавить кат.')
categories_b2 = KeyboardButton(text='Удалить кат.')
categories_b3 = KeyboardButton(text='Изменить кат.')
categories_b4 = KeyboardButton(text='Обновить кат.')
categories_b5 = KeyboardButton(text='Группы')
categories_b6 = KeyboardButton(text='Покупки')
categories_b7 = KeyboardButton(text='Из группы')
categories_b8 = KeyboardButton(text='В группу')
categories_kb \
    .insert(categories_b1) \
    .insert(categories_b2) \
    .insert(categories_b3) \
    .insert(categories_b4) \
    .insert(categories_b5) \
    .insert(categories_b6) \
    .insert(categories_b7) \
    .insert(categories_b8)



stop_kb = ReplyKeyboardMarkup(resize_keyboard=True)
stop_b1 = KeyboardButton(text='Отмена кат.')
stop_kb \
    .insert(stop_b1)


stop_kb_for_upd = ReplyKeyboardMarkup(resize_keyboard=True)
stop_kb_for_upd1 = KeyboardButton(text='Отмена кат.')
stop_kb_for_upd2 = KeyboardButton(text='Без изменений')
stop_kb_for_upd \
    .insert(stop_kb_for_upd1) \
    .insert(stop_kb_for_upd2)


async def make_categorize_keyboard(id_list_of_ids, command_text='categorize '):
    categories = await sql_read_categories()
    categorize_keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
    for category in categories:
        category_id = category[0]
        keyboard_text = category[1]
        keyboard_command = command_text + str(id_list_of_ids) + ' ' + str(category_id)
        button = InlineKeyboardButton(text=keyboard_text, callback_data=keyboard_command)
        categorize_keyboard.insert(button)
    keyboard_command = f'{command_text}{id_list_of_ids} -1'
    categorize_keyboard.insert(InlineKeyboardButton(text='Без категории', callback_data=keyboard_command))
    return categorize_keyboard


comment_for_category = ReplyKeyboardMarkup(resize_keyboard=True)
comment_for_category_b1 = KeyboardButton(text='Отмена кат.')
comment_for_category_b2 = KeyboardButton(text='Без описания')
comment_for_category \
    .insert(comment_for_category_b1) \
    .insert(comment_for_category_b2)


comment_for_category_for_upd = ReplyKeyboardMarkup(resize_keyboard=True)
comment_for_category_for_upd_b1 = KeyboardButton(text='Отмена кат.')
comment_for_category_for_upd_b2 = KeyboardButton(text='Без описания')
comment_for_category_for_upd_b3 = KeyboardButton(text='Без изменений')
comment_for_category_for_upd \
    .insert(comment_for_category_for_upd_b1) \
    .insert(comment_for_category_for_upd_b2) \
    .insert(comment_for_category_for_upd_b3)