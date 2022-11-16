from create_bot import bot, dp
from handlers import list
from aiogram.utils import executor
from data_base.sql_main import sql_start


async def on_startup(_):
    await bot.send_message(129727111, 'Бот вышел в онлайн')
    if sql_start():
        await bot.send_message(129727111, 'Data base connected!')

list.register_handlers_list(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


