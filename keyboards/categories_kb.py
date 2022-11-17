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


async def make_categorize_keyboard(id_list_of_ids):
    categories = await sql_read_categories()
    categorize_keyword = InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
    for category in categories:
        keyboard_text = category[1]
        keyboard_command = 'categorize ' + str(id_list_of_ids) + ' ' + str(category[0])
        button = InlineKeyboardButton(text=keyboard_text, callback_data=keyboard_command)
        categorize_keyword.insert(button)
    return categorize_keyword


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