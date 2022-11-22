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
                 'description TEXT)')
    cur.execute(""" INSERT INTO categories (id, name) 
                    SELECT '-1', 'Без категории' 
                    WHERE NOT EXISTS (SELECT * FROM categories)""")

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
            if comment is None:
                comment = ""
            text = text + f"{str(counter)} {name}         {comment}"
            if i != len(data):
                text = text + "\n"
            counter += 1
            i += 1
        return text

