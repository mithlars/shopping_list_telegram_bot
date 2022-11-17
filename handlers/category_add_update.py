from aiogram import types, Dispatcher
from create_bot import bot
from keyboards.categories_kb import *
from keyboards.shared_kb import *
from data_base.sql_categories import *
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from handlers.list_of_purchases import read_list_of_purchases
from handlers.categories import *


class FSMCategory(StatesGroup):
    name = State()
    comment = State()


# ##    making list of categories with delete inline keyboard:
async def update_som_category(message: types.Message):
    data = await sql_read_categories()
    categories_text = await make_text_from_select(data, 1)
    if categories_text == 'The list is empty.':
        await bot.send_message(message.chat.id, 'Список категорий пуст', reply_markup=categories_kb)
    else:
        categories_text = categories_text + '\nВыберите какую категорию Вы хотите изменить:'
        update_keyboard_buttons_and_counter = await make_inline_keyboard_and_buttons_list(data, 'update_category ', [], 1)
        update_keyboard = update_keyboard_buttons_and_counter['keyboard']
        await bot.send_message(message.chat.id, categories_text, reply_markup=update_keyboard)


# ##     start updating category state:
async def update_current_category(callback: types.CallbackQuery, state: FSMCategory.all_states):
    category_id = callback.data.replace("update_category ", "")
    ald_category = await sql_read_category(category_id)
    async with state.proxy() as data:
        data['id'] = category_id
        data['ald_name'] = ald_category[0][1]
        data['ald_comment'] = ald_category[0][2]
    await FSMCategory.name.set()
    await bot.send_message(callback.message.chat.id, 'Введите новое имя новой категории', reply_markup=stop_kb_for_upd)


# ##     start adding category state by starting getting name:
async def add_category(message: types.Message):
    await FSMCategory.name.set()
    await bot.send_message(message.chat.id, 'Введите имя новой категории', reply_markup=stop_kb)


# ##     abort state at any stage:
async def state_cancel_handler(message: types.Message, state: FSMCategory.all_childs):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK', reply_markup=categories_kb)


# ##     saving name and starting getting comment:
async def add_name_for_new_category(message: types.Message, state: FSMCategory.name):
    async with state.proxy() as data:
        if message.text == 'Без изменений':     data['name'] = data['ald_name']
        else:                                   data['name'] = message.text
    await FSMCategory.comment.set()
    if 'id' not in data.keys():
        await bot.send_message(message.chat.id, "Теперь введите описание", reply_markup=comment_for_category)
    else:
        await bot.send_message(message.chat.id, "Теперь введите новое описание", reply_markup=comment_for_category_for_upd)


# ##     analise all got and save new or changes to database:
async def add_comment_for_new_category(message: types.Message, state: FSMCategory.comment):
    async with state.proxy() as data:
        if message.text == 'Без описания':   data['comment'] = ''
        elif message.text == 'Без изменений':   data['comment'] = data['ald_comment']
        else:                                   data['comment'] = message.text
    if 'id' not in data.keys():
        await sql_add_category(data['name'], data['comment'])
        categories_data = await sql_read_categories()
        if categories_data[0][1] == 'The list is empty.':
            await sql_delete_category(categories_data[0][0])
        await message.reply("Категоря добавлена")
    elif data['name'] != data['ald_name'] or data['comment'] != data['ald_comment']:
        await sql_update_category(data['id'], data['name'], data['comment'])
        await message.reply("Категоря изменена")
    else:
        await message.reply("Все осталось без изменений")
    await state.finish()
    await list_of_categories(message)


def register_handlers_add_update_category(dp: Dispatcher):
    dp.register_message_handler(add_category, Text(equals='Добавить кат.', ignore_case=True), state=None)
    dp.register_message_handler(state_cancel_handler, Text(startswith='Отмена кат.', ignore_case=True), state='*')
    dp.register_message_handler(add_name_for_new_category, state=FSMCategory.name)
    dp.register_message_handler(add_comment_for_new_category, state=FSMCategory.comment)
    dp.register_message_handler(update_som_category, Text(equals='Изменить кат.', ignore_case=True))
    dp.register_callback_query_handler(update_current_category, Text(startswith='update_category '))