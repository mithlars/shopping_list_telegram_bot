from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from create_bot import bot

from data_base.sql_purchases import sql_make_text_of_list_by_categories, sql_read_purchase, sql_update_purchase
from data_base.sql_categories import  sql_read_used_categories_ids, sql_get_categories_ids_for_purchase

from handlers.purchases_list import read_list_of_purchases

from keyboards.purchases_kb import purchase_main_kb, make_purchases_list_inline_keyboard, stop_kb_for_upd_purchase_name


class FSMPurchase(StatesGroup):
    name = State()
    category = State()


async def update_som_purchase(message: types.Message):
    used_categories_ids = await sql_read_used_categories_ids()
    text = await sql_make_text_of_list_by_categories(used_categories_ids)
    delete_keyboard_inline = await make_purchases_list_inline_keyboard(
                                                            used_categories_ids, command_text='update_current_purchase ')
    if text == '':
        await bot.send_message(message.chat.id, 'Список покупок пуст', reply_markup=purchase_main_kb)
    else:
        await bot.send_message(message.chat.id, 'Выберите, какую запись Вы хотите изменить:', reply_markup=purchase_main_kb)
        await bot.send_message(message.chat.id, text, reply_markup=delete_keyboard_inline, parse_mode="HTML")


# ##     start updating purchase state:
async def update_current_purchase(callback: types.CallbackQuery, state: FSMPurchase.all_states):
    purchase_id = callback.data.replace('update_current_purchase ', '')
    purchase = await sql_read_purchase(purchase_id)
    async with state.proxy() as data:
        data['id'] = purchase_id
        data['old_name'] = purchase[0][1]
        data['old_comment'] = purchase[0][2]
        data['old_categories_ids'] = await sql_get_categories_ids_for_purchase(purchase_id)
    await FSMPurchase.name.set()
    # Удаление кнопки "Отмена пок.":
    if stop_kb_for_upd_purchase_name["keyboard"][0][0]["text"] == "Отмена пок.":
        del stop_kb_for_upd_purchase_name["keyboard"][0][0]
    await bot.send_message(
        callback.message.chat.id,
        'Введите новое имя новой покупки. \n'
        'Старое имя можно скопировать нажатием левоя кнопки мыши.',
        reply_markup=stop_kb_for_upd_purchase_name
    )
    # Отправка сообщения со старым именем покупки свозможностью копирования одним кликом:
    await bot.send_message(callback.message.chat.id, f"`{data['old_name']}`", parse_mode=types.ParseMode.MARKDOWN_V2)


# ##     abort state at any stage:
async def state_cancel_handler(message: types.Message, state: FSMPurchase.all_childs):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK', reply_markup=purchase_main_kb)


# ##     saving name and starting getting comment:
async def getting_new_name_for_purchase(message: types.Message, state: FSMPurchase.name):
    async with state.proxy() as data:
        if message.text == 'Без изменений': data['name'] = data['old_name']
        else:                               data['name'] = message.text

    if data['name'] == data['old_name']:
        await bot.send_message(message.chat.id, 'Запись осталась без изменений')
    else:
        await sql_update_purchase(purchase_id=data['id'], purchase_name=data['name'])
        await bot.send_message(message.chat.id, 'Запись изменена')

    await state.finish()
    await read_list_of_purchases(message)


def register_handlers_purchase_changing(dp: Dispatcher):

    dp.register_message_handler(update_som_purchase, Text(equals='Изменить'))
    dp.register_message_handler(update_som_purchase, Text(equals='✏️'))
    dp.register_callback_query_handler(update_current_purchase, Text(startswith='update_current_purchase '), state=None)
    dp.register_message_handler(state_cancel_handler, Text(equals='Отмена пок.'), state='*')
    dp.register_message_handler(getting_new_name_for_purchase, state=FSMPurchase.name)


