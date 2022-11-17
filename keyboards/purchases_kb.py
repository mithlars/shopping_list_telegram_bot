from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
main_b1 = KeyboardButton(text='Помощь')
main_b2 = KeyboardButton(text='Список')
main_b3 = KeyboardButton(text='Очистить')
main_b4 = KeyboardButton(text='Категории')
main_kb \
    .insert(main_b1) \
    .insert(main_b2) \
    .insert(main_b3) \
    .insert(main_b4)