from create_bot import bot, dp
from handlers.purchases_list import register_handlers_purchases
from handlers.category_add_update import register_handlers_add_update_category
from handlers.categories import register_handlers_categories
from handlers.purchase_changing import register_handlers_purchase_changing
from handlers.category_in_out import register_handlers_category_in_out
from aiogram.utils import executor
from data_base.sql_main import sql_start
from classes.Middleware import Middleware
# from data_base.googlesheet import GoogleSheet

# If modifying these scopes, delete the file token.json.
scopes = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
sample_spreadsheet_id = '1YG1GZsT2-8enOke64SUtDanfWgFLI14q-eUSBdwfkXo'
sample_range_name = 'Лист1!A2:B'

google_sheet = None


async def on_startup(_):
    await bot.send_message(129727111, "Бот вышел в онлайн")

    if sql_start():
        await bot.send_message(129727111, 'Data base connected!')

    # google_sheet = GoogleSheet(scopes, sample_spreadsheet_id, sample_range_name)
    #
    # cells_from_sheet = google_sheet.read(sample_range_name)
    # print(cells_from_sheet)


register_handlers_add_update_category(dp)
register_handlers_categories(dp)
register_handlers_purchase_changing(dp)
register_handlers_category_in_out(dp)


register_handlers_purchases(dp)
dp.middleware.setup(Middleware())



executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


