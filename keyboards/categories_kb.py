from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from data_base.sql_main import *
from data_base.sql_categories import *


categories_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
categories_b1 = KeyboardButton(text='Добавить кат.')
categories_b2 = KeyboardButton(text='Удалить кат.')
categories_b3 = KeyboardButton(text='Изменить кат.')
categories_b4 = KeyboardButton(text='Обновить кат.')
# categories_b5 = KeyboardButton(text='Группы')
categories_b6 = KeyboardButton(text='Покупки')
# categories_b7 = KeyboardButton(text='Из группы')
# categories_b8 = KeyboardButton(text='В группу')
categories_b9 = KeyboardButton(text='Сортировка категорий')
categories_kb \
    .insert(categories_b1) \
    .insert(categories_b2) \
    .insert(categories_b3) \
    .insert(categories_b4) \
    .insert(categories_b9) \
    .insert(categories_b6)
    # .insert(categories_b7)  # .insert(categories_b8)



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


async def make_categorize_keyboard(id_list_of_ids, command_text='categorize ', dif_button=False):
    categories = await sql_read_categories()
    categorize_keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
    for category in categories:
        category_id = category[0]
        button_text = category[1]
        button_command = command_text + str(id_list_of_ids) + ' ' + str(category_id)
        button = InlineKeyboardButton(text=button_text, callback_data=button_command)
        categorize_keyboard.insert(button)
    kb_command = f'{command_text}{id_list_of_ids} -1'
    categorize_keyboard.insert(InlineKeyboardButton(text='Без категории', callback_data=kb_command))
    if dif_button:
        different_button_command = f'dif_categorize {id_list_of_ids}'
        categorize_keyboard.insert(InlineKeyboardButton(text='Разные категории', callback_data=different_button_command))
    return categorize_keyboard


async def make_from_which_category_keyboard(command_text, exceptions_ids=[]):
    categories = await sql_read_categories()
    categorize_keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=8)
    count = 1
    for category in categories:
        category_id = category[0]
        category_name = category[1]
        if category_id not in exceptions_ids:
            button_text = f'{count}'
            count += 1
            button_command = f'{command_text}{category_id}'
            button = InlineKeyboardButton(text=button_text, callback_data=button_command)
            categorize_keyboard.insert(button)
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