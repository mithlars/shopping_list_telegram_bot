from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from data_base.sql_main import cur
from keyboards.shared_kb import make_inline_keyboard_and_buttons_list


purchase_main_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
main_b1 = KeyboardButton(text='Помощь')
main_b2 = KeyboardButton(text='Список')
main_b3 = KeyboardButton(text='Очистить')
main_b4 = KeyboardButton(text='Изменить')
main_b5 = KeyboardButton(text='Категории')
main_b6 = KeyboardButton(text='Из категории')
main_b7 = KeyboardButton(text='В категорию')
purchase_main_kb \
    .insert(main_b1) \
    .insert(main_b2) \
    .insert(main_b3) \
    .insert(main_b4) \
    .insert(main_b5) \
    .insert(main_b6) \
    .insert(main_b7)


async def make_purchases_list_inline_keyboard(categories_ids, command_text):
    print('___ make_purchases_list_inline_keyboard ____START')
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=8)
    counter_starts_from = 1
    for category_id in categories_ids:
        purchases_ids_data = cur.execute('SELECT purchase_id FROM link_categories_and_purchases WHERE category_id IS ?',
                                         (category_id,)).fetchall()
        keyboard_and_buttons_list = await make_inline_keyboard_and_buttons_list(
            purchases_ids_data, command_text, [], counter_starts_from)
        buttons_list = keyboard_and_buttons_list['buttons_list']
        counter_starts_from += keyboard_and_buttons_list['buttons_counter']
        for button in buttons_list:
            keyboard.insert(button)
    print('___ make_purchases_list_inline_keyboard ____FINISH')
    return keyboard


stop_kb_for_upd_purchase_name = ReplyKeyboardMarkup(resize_keyboard=True)
stop_kb_for_upd_purchase_name_b1 = KeyboardButton(text='Отмена пок.')
stop_kb_for_upd_purchase_name_b2 = KeyboardButton(text='Без изменений')
stop_kb_for_upd_purchase_name \
    .insert(stop_kb_for_upd_purchase_name_b1) \
    .insert(stop_kb_for_upd_purchase_name_b2)


# stop_kb_for_upd_purchase_categories = ReplyKeyboardMarkup(resize_keyboard=True)
# stop_kb_for_upd_purchase_categories_b1 = KeyboardButton(text='Отмена пок.')
# stop_kb_for_upd_purchase_categories.insert(stop_kb_for_upd_purchase_categories_b1)

