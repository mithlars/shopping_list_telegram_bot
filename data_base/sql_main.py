import sqlite3
# from data_base.sql_purchases import *


base = sqlite3.connect('shopping_list.db')
cur = base.cursor()


def sql_start():
    # global base, cur
    base.execute('CREATE TABLE IF NOT EXISTS list001 (' \
                 'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
                 'name VARCHAR(50),' \
                 'comment TEXT)')
    # Добавить заполнение пустой базы

    base.execute('CREATE TABLE IF NOT EXISTS categories (' \
                 'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                 'name VARCHAR(50),' \
                 'description TEXT)')
    # Добавить заполнение пустой базы

    base.execute('CREATE TABLE IF NOT EXISTS link_categories_and_purchases ('
                 'category_id INTEGER, '
                 'purchase_id INTEGER)')
    base.commit()
    if base:
        return True
    else:
        return False


async def make_text_from_select(data, counter_starts_from):
    print(data)
    if data[0][1] == "The list is empty.":
        return 'The list is empty.'
    else:
        text = ""
        counter = counter_starts_from
        i = 1
        for purchase in data:
            name = purchase[1]
            comment = purchase[2]
            if comment == None:
                comment = ""
            text = text + f"{str(counter)} {name}         {comment}"
            if i != len(data):
                text = text + "\n"
            counter += 1
            i += 1
        return text