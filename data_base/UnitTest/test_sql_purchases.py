from unittest import TestCase, main
from data_base.sql_purchases import *
from data_base.sql_main import cur, base, sql_start


# sql_start()
# """ Добавляем в базу данных тестовый товар, чтобы проверить его id в ответе функции"""
# cur.execute("INSERT INTO items001 (name) VALUES ('test_milk')")
# test_milk_id = cur.execute("SELECT id FROM items001 WHERE name IS 'test_milk'").fetchall()[0][0]
# print(f'\ntest_milk_id: {test_milk_id}')
# purchases_for_add = [
#     'test_milk',
#     'test_coffee',
#     'test_bread'
# ]
# print(f'\npurchases_for_add: \n{purchases_for_add}')
# waited_text = '1 test_milk\n' \
#               '2 test_coffee\n' \
#               '3 test_bread'
# print(f'\nwaited_text: \n{waited_text}')
# returned = test_test(purchases_for_add, is_clearing=False)
# print(f'\nreturned:\n{returned}')
# # id_list_of_ids = returned[0]
# # existing_purchases_ids_list = returned[1]
# # text = returned[2]


# class sql_add_command_test(TestCase):
#     """
#     Тестируем функцию sql_add_command
#     """
#     actual = test_test(['test_milk', 'test_coffee', 'test_bread'], is_clearing=False)
#     expected = ['1 test_coffee\n2 test_bread', 2, '']
#     def test_plus(self):
#         # assert self.actual.columns == ['1 test_coffee\n2 test_bread', 2, '']
#         assert all([a == b for a, b in zip(self.actual, self.expected)])


"""Удаляем из базы данных тестовую позицию"""
# cur.execute('DELETE FROM items001 WHERE id IS ?', (test_milk_id,))


if __name__ == '__main__':
    main()