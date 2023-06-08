from create_bot import bot, dp
from handlers.purchases_list import register_handlers_purchases
from handlers.category_add_update import register_handlers_add_update_category
from handlers.categories import register_handlers_categories
from handlers.purchase_changing import register_handlers_purchase_changing
from handlers.category_in_out import register_handlers_category_in_out
from aiogram.utils import executor
from data_base.sql_main import sql_start
from classes.Middleware import Middleware


async def on_startup(_):
    await bot.send_message(129727111, 'Бот вышел в онлайн')
    if sql_start():
        await bot.send_message(129727111, 'Data base connected!')


register_handlers_add_update_category(dp)
register_handlers_categories(dp)
register_handlers_purchase_changing(dp)
register_handlers_category_in_out(dp)


register_handlers_purchases(dp)
dp.middleware.setup(Middleware())



executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


