import sqlite3


base = sqlite3.connect('shopping_list.db')
cur = base.cursor()


def sql_start():
    base.execute('CREATE TABLE IF NOT EXISTS list001 ('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                 'name VARCHAR(50),'
                 'comment TEXT)')
    cur.execute(""" INSERT INTO list001 (id, name) 
                    SELECT '0', 'The list is empty.' 
                    WHERE NOT EXISTS (SELECT * FROM list001)""")

    base.execute('CREATE TABLE IF NOT EXISTS categories ('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                 'name VARCHAR(50),'
                 'description TEXT,'
                 'number INTEGER)')
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


