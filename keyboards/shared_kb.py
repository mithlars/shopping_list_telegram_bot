from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data_base.sql_main import *


async def make_inline_keyboard_and_buttons_list(objects_ids_data, command_text, exceptions, counter_starts_from):
    button_text_counter = counter_starts_from
    buttons_counter = 0
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=8)       #, one_time_keyboard=True)
    buttons_list = []
    for Object_id_data in objects_ids_data:
        if Object_id_data[0] not in exceptions:
            button_text = str(button_text_counter)
            button_callback_text = f"{command_text}{Object_id_data[0]}"
            buttons_list.append(InlineKeyboardButton(text=button_text, callback_data=button_callback_text))
            keyboard.insert(InlineKeyboardButton(text=button_text, callback_data=button_callback_text))
            buttons_counter += 1
        button_text_counter += 1
    keyboard_and_buttons_list = {'keyboard': keyboard, 'buttons_list': buttons_list, 'buttons_counter': buttons_counter}
    return keyboard_and_buttons_list

