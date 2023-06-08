import sqlite3
import psycopg2


base = sqlite3.connect('shopping_list.db')
cur = base.cursor()

def sql_start():
    base.execute('CREATE TABLE IF NOT EXISTS users ('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                 'user_telegram_id INTEGER UNIQUE,'
                 'name VARCHAR(50),'
                 'access_lists_ids TEXT,'
                 'current_list_id INTEGER,'
                 'reg_date DATETIME,'
                 'last_visit_date DATETIME)')
    base.execute('CREATE TABLE IF NOT EXISTS lists ('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                 'name VARCHAR(50),'
                 'description TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS items001 ('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                 'name VARCHAR(50),'
                 'comment TEXT,'
                 'list_id INTEGER)')
    cur.execute(""" INSERT INTO items001 (id, name) 
                    SELECT '0', 'The list is empty.' 
                    WHERE NOT EXISTS (SELECT * FROM items001)""")
    base.execute('CREATE TABLE IF NOT EXISTS categories ('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                 'name VARCHAR(50),'
                 'description TEXT,'
                 'number INTEGER,'
                 'list_id INTEGER)')
    cur.execute(""" INSERT INTO categories (id, name, number) 
                    SELECT '-1', 'Без категории' , '0'
                    WHERE NOT EXISTS (SELECT * FROM categories)""")
    base.execute('CREATE TABLE IF NOT EXISTS link_categories_and_purchases ('
                 'category_id INTEGER, '
                 'purchase_id INTEGER)')
    base.commit()
    if base:
        return True
    else:
        return False


async def make_text_from_select(data, counter_starts_from, exceptions_ids=[]):
    if data[0][1] == "The list is empty.":
        return 'The list is empty.'
    else:
        text = ""
        counter = counter_starts_from
        i = 1
        for item in data:
            item_id = item[0]
            if item_id not in exceptions_ids:
                item_name = item[1]
                item_comment = item[2]
                if item_comment is None:
                    item_comment = ""
                text = text + f"{str(counter)}. {item_name}         {item_comment}"
                if i != len(data):
                    text = text + "\n"
                counter += 1
                i += 1
        return text


