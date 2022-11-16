import sqlite3


def sql_start():
    global base, cur
    base = sqlite3.connect('shopping_list.db')
    cur = base.cursor()
    base.execute('CREATE TABLE IF NOT EXISTS list001(name TEXT)')
    base.commit()
    if base:
        return True
    else:
        return False


async def sql_add_command(shoppings_for_add):
    for shopping in shoppings_for_add:
        cur.execute('INSERT INTO list001 (name) VALUES (?)', (shopping,))
    base.commit()



async def sql_read_all():
    data = cur.execute('SELECT id, name FROM list001').fetchall()
    return data


async def sql_delete_shopping(shopping):
    shopping = str(shopping)
    all = await sql_read_all()
    cur.execute(f"""DELETE FROM list001 WHERE id='{shopping}'""")
    base.commit()
    if len(all) == 1:
        await sql_add_command(["The list is cleared."])

async def sql_clear_all():
    cur.execute('DELETE FROM list001')
    base.commit()
    return True
