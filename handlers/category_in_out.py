from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text

from create_bot import bot

from data_base.sql_categories import sql_read_categories, sql_categorize_or_uncategorize_current_purchase
from data_base.sql_main import make_text_from_select, cur, base
from data_base.sql_purchases import make_text_and_count_of_list_for_category

from handlers.purchases_list import read_list_of_purchases, categorize_all_list

from keyboards.categories_kb import make_from_which_category_keyboard
from keyboards.purchases_kb import make_purchases_list_inline_keyboard

"""
Файл содержит набор handler-функций для назначения и удаления связей между товарами и категориями. 
"""


async def in_category_from_which_category(message: types.Message, test=False):
    """
    В категорию. START.

    Функция получает команду "В категорию" и запускает бизнес-процесс добавления товара в категорию.
    Отправляет сообщение пользователю с запросом выбрать категорию из которой нужно взять товар,
    для назначения связи с другой категорией.
    В качестве опции предлагается назначить категорию/рии всем товарам без категории.
    """
    print('\n***********************************\nin_category_from_which_category ____START\n')
    categories_data = await sql_read_categories()
    message_text = 'В какой категории присутствует товар, для которого Вы хотите добавить/изменить категорию?\n'
    message_text += await make_text_from_select(categories_data, counter_starts_from=1)
    count = len(message_text.split('\n'))
    message_text += f'\n{count} Без категории'
    keyboard = await make_from_which_category_keyboard('in_category_which_purchase ')
    keyboard.insert(InlineKeyboardButton(text=f'{count}', callback_data='in_category_which_purchase -1'))
    keyboard.add(InlineKeyboardButton(text='Все товары без категории',
                                      callback_data='categorize_all_single_purchases'))
    keyboard.insert(InlineKeyboardButton(text='Отмена', callback_data='in_category_finish'))
    if test:
        return {'keyboard': keyboard, 'text': message_text}
    else:
        await bot.send_message(message.chat.id, message_text, reply_markup=keyboard)
    print('\nin_category_from_which_category ____FINISH\n***********************************\n')


async def out_of_category(message: types.message, test=False):
    """
    Из категории. START.

    Функция получает команду "Из категории" и запускает бизнес-процесс удаления связи между товаром и категорией.
    Отправляет сообщение пользователю с запросом выбрать категорию из которой нужно удалить товар.
    """
    categories_data = await sql_read_categories()
    message_text = 'Из какой категории Вы хотите удалить товар?\n'
    message_text += await make_text_from_select(categories_data, counter_starts_from=1)
    keyboard = await make_from_which_category_keyboard('out_of_category_which_purchase ')
    keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='in_category_finish'))
    if test:
        return {'keyboard': keyboard, 'text': message_text}
    else:
        await bot.send_message(message.chat.id, message_text, reply_markup=keyboard)


async def categorize_all_single(callback: types.CallbackQuery, test=False):
    """
    Категоризировать все свободные товары.

    Функция запускает процесс назначения категории всем товарам без категории.
    Отправляет сообщение пользователю со списком таких товаров и с просьбой выбрать категорию для них.
    В качестве опции можно выбрать разные категории для всех товаров без категории.
    """
    uncategorized_purchases_ids = []
    uncategorized_purchases_text = ''
    uncategorized_purchases_ids_data = cur.execute(
        'SELECT purchase_id FROM link_categories_and_purchases WHERE category_id = -1').fetchall()
    for purchase_id_data in uncategorized_purchases_ids_data:
        uncategorized_purchases_ids.append(purchase_id_data[0])
    uncategorized_purchases_ids_str = ','.join(map(str, uncategorized_purchases_ids))
    cur.execute('INSERT INTO list001 (comment) VALUES (?)', (uncategorized_purchases_ids_str,))
    id_list_of_uncategorized_purchases_ids = cur.execute('SELECT id FROM list001 WHERE comment IS ?',
                                                         (uncategorized_purchases_ids_str,)).fetchall()[0][0]
    count = 1
    for purchase_id in uncategorized_purchases_ids:
        purchase_name = cur.execute('SELECT name FROM list001 WHERE id IS ?', (purchase_id,)).fetchall()[0][0]
        if count != len(uncategorized_purchases_ids):
            uncategorized_purchases_text += f'{purchase_name}\n'
        else:
            uncategorized_purchases_text += f'{purchase_name}'
        count += 1
    base.commit()
    if test:
        return {'uncategorized_purchases_ids_str': uncategorized_purchases_ids_str,
                'id_list_of_uncategorized_purchases_ids': str(id_list_of_uncategorized_purchases_ids),
                'uncategorized_purchases_text': uncategorized_purchases_text}
    else:
        await categorize_all_list(callback.message, id_list_of_uncategorized_purchases_ids, uncategorized_purchases_text)


async def in_category_which_purchase(callback: types.CallbackQuery, test=False):
    """
    Выбор товара для категоризации.

    Функция получает категорию из которой нужно выбрать товар для НАЗНАЧЕНИЯ новой связи с другой категорией.
    Отправляет сообщение пользователю со списком товаров из этой категории с просьбой выбрать один из них.
    """
    category_id = callback.data.replace('in_category_which_purchase ', '')
    message_text = 'Для какого товара Вы хотите добавить/изменить категорию?\n'
    command_text = f'in_category_in_which_category {category_id} '
    keyboard = await make_purchases_list_inline_keyboard([category_id], command_text=command_text)

    text_and_count_of_list_for_category = await make_text_and_count_of_list_for_category(category_id, [],
                                                                                         counter_starts_from=1)
    message_text += text_and_count_of_list_for_category['text']

    if test:
        return {
            'category_id': category_id,
            'message_text': message_text,
            'keyboard': keyboard
        }
    else:
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='in_category_finish'))
        await bot.send_message(callback.message.chat.id, message_text, reply_markup=keyboard)


async def out_of_category_which_purchase(callback: types.CallbackQuery, test=False):
    """
    Выбор товара для УДАЛЕНИЯ связи с категорией.

    Функция получает категорию из которой нужно выбрать товар для УДАЛЕНИЯ связи с категорией.
    Отправляет сообщение пользователю со списком товаров из этой категории с просьбой выбрать один из них.
    """
    category_id = callback.data.replace('out_of_category_which_purchase ', '')
    category_name = cur.execute('SELECT name FROM categories WHERE id IS ?', (category_id,)).fetchall()[0][0]
    message_text = f'Какой товар Вы хотите удалить из категории {category_name}?\n'
    command_text = f'out_of_category_finish {category_id} '
    keyboard = await make_purchases_list_inline_keyboard([category_id], command_text=command_text)

    text_and_count_of_list_for_category = await make_text_and_count_of_list_for_category(category_id, [],
                                                                                         counter_starts_from=1)
    message_text += text_and_count_of_list_for_category['text']

    if test:
        return {
            'category_id': category_id,
            'message_text': message_text,
            'keyboard': keyboard
        }
    else:
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='in_category_finish'))
        await bot.send_message(callback.message.chat.id, message_text, reply_markup=keyboard)


async def in_category_in_which_category(callback: types.CallbackQuery, test=False):
    """
    Выбор новой категории.

    Функция получает id товара и категории с которой он связан.
    Возможно этот товар связан и с другой категорией, но это функцией игнорируется.

    """
    ids_list = callback.data.replace('in_category_in_which_category ', '').split(' ')
    prev_category_id = ids_list[0]
    purchase_id = ids_list[1]
    purchase_name = cur.execute('SELECT name FROM list001 WHERE id IS ?', (purchase_id,)).fetchall()[0][0]
    print(f'purchase_id: {purchase_name}')
    keyboard = await make_from_which_category_keyboard(f'in_category_categorize {prev_category_id} {purchase_id} ',
                                                       exceptions_ids=[prev_category_id])
    message_text = f'Выберите новую категорию для покупки {purchase_name}:'
    categories_data = await sql_read_categories()
    message_text += await make_text_from_select(categories_data, counter_starts_from=1)
    if test:
        return {'text': message_text,
                'keyboard': keyboard}
    else:
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data='in_category_finish'))
        await bot.send_message(callback.message.chat.id, message_text, reply_markup=keyboard)


async def in_category_categorize(callback: types.CallbackQuery, test=False):
    """
    Категоризирование.

    Функция получает id товара, новой и старой категории.
    Создается связь товара с новой категорией.
    В случае, если предыдущая категория не "Без категории", отправляется сообщение с предложением удалить или
    оставить связь товара с предыдущей категорией.
    """
    print('\n***********************************\nin_category_categorize ____START\n')
    ids_list = callback.data.replace('in_category_categorize ', '').split(' ')
    print(f'ids_list: {ids_list}')
    prev_category_id = ids_list[0]
    print(f'prev_category_id: {prev_category_id}')
    if prev_category_id == '-1':
        prev_category_name = 'Без категории'
    else:
        prev_category_name = cur.execute('SELECT name FROM categories WHERE id IS ?', (prev_category_id,)).fetchall()[0][0]
    purchase_id = ids_list[1]
    print(f'purchase_id: {purchase_id}')
    purchase_name = cur.execute('SELECT name FROM list001 WHERE id IS ?', (purchase_id,)).fetchall()[0][0]
    category_id = ids_list[2]
    print(f'category_id: {category_id}')
    category_name = cur.execute('SELECT name FROM categories WHERE id IS ?', (category_id,)).fetchall()[0][0]
    print(f'category_name: {category_name}')
    await sql_categorize_or_uncategorize_current_purchase(category_id, purchase_id)
    if not test:
        if prev_category_id == '-1':
            message_text = f'Покупка {purchase_name} добавлена в категорию {category_name}.\n'
            await bot.send_message(callback.message.chat.id, message_text)
            await read_list_of_purchases(callback.message, [])
        else:
            message_text = f'Покупка {purchase_name} добавлена в категорию {category_name}.\n' \
                           f'Хотите удалить покупку {purchase_name} из предыдущей категории {prev_category_name}?'
            uncategorize_keyword = InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
            uncategorize_keyword.insert(InlineKeyboardButton(text='Удалить',
                                                             callback_data=f'uncategorize {prev_category_id} {purchase_id}'))
            uncategorize_keyword.insert(InlineKeyboardButton(text='Оставить', callback_data='in_category_finish'))
            uncategorize_keyword.add(InlineKeyboardButton(text='Отмена', callback_data='in_category_finish'))
            await bot.send_message(callback.message.chat.id, message_text, reply_markup=uncategorize_keyword)
    print('\nin_category_categorize ____FINISH\n***********************************\n')


async def in_category_finish(callback: types.CallbackQuery, test=False):
    """
    Если пользователь предпочитает оставить связь выбранного товара с предыдущей категорией просто выводится актуальный
    список товаров, разбитый по категориям
    """
    await read_list_of_purchases(callback.message, [])


async def out_of_category_finish(callback: types.CallbackQuery, test=False):
    """
    Удаление связи товара с категорией.
    Функция получает id товара и новой категории и удаляет связь между ними.
    В случае, если других связей товара с категориями нет -- создается связь с категорией "Без категории"
    Отправляется сообщение пользователю об удачном удалении связи и актуальный список товаров, разбитый по категориям.
    """
    print(f'type(callback.data): {type(callback.data)}')
    ids_list = callback.data.replace('out_of_category_finish ', '').split(' ')
    category_id = ids_list[0]
    category_name = cur.execute('SELECT name FROM categories WHERE id IS ?', (category_id,)).fetchall()[0][0]
    purchase_id = ids_list[1]
    purchase_name = cur.execute('SELECT name FROM list001 WHERE id IS ?', (purchase_id,)).fetchall()[0][0]
    await sql_categorize_or_uncategorize_current_purchase(category_id, purchase_id, uncategorize=True)
    if not test:
        message_text = f'Удалена связи товара {purchase_name}  с категорией {category_name}.\n'
        await bot.send_message(callback.message.chat.id, message_text)
        await read_list_of_purchases(callback.message, [])


def register_handlers_category_in_out(dp: Dispatcher):
    dp.register_message_handler(in_category_from_which_category, Text(startswith='В категорию'))
    dp.register_message_handler(in_category_from_which_category, Text(startswith='➡️📁'))
    dp.register_callback_query_handler(categorize_all_single, Text(equals='categorize_all_single_purchases'))
    dp.register_callback_query_handler(in_category_which_purchase, Text(startswith='in_category_which_purchase '))
    dp.register_callback_query_handler(in_category_in_which_category, Text(startswith='in_category_in_which_category '))
    dp.register_callback_query_handler(in_category_categorize, Text(startswith='in_category_categorize '))
    dp.register_callback_query_handler(in_category_finish, Text(equals='in_category_finish'))

    dp.register_message_handler(out_of_category, Text(equals='Из категории'))
    dp.register_message_handler(out_of_category, Text(equals='⬅️📁'))
    dp.register_callback_query_handler(out_of_category_which_purchase, Text(startswith='out_of_category_which_purchase'))
    dp.register_callback_query_handler(out_of_category_finish, Text(startswith='out_of_category_finish '))
