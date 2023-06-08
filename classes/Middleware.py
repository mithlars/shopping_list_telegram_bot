from create_bot import bot, dp
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram import types
from constants import ACCESS_IDs


class Middleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        if message.from_user.id not in ACCESS_IDs:
            await bot.send_message(message.chat.id, 'Бот находится в разработке, Вы не в списке тестового доступа.')
            raise CancelHandler()
