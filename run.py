import asyncio
import logging
import aiohttp 
from aiogram import Bot, Dispatcher
from aiohttp_socks import ProxyConnector

from config import TOKEN
from app.handlers import router

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
import time
import os



async def main():

    bot = Bot(token=TOKEN)   
    dp = Dispatcher()
    dp.message.outer_middleware(ThrottlingMiddleware(limit=1))
    dp.include_router(router)
    
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 1):
        self.limit = limit
        self.caches = {} 

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()

        if user_id in self.caches:
            last_time = self.caches[user_id]
            if current_time - last_time < self.limit:
                return 

        self.caches[user_id] = current_time
        return await handler(event, data)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main()) 
    except KeyboardInterrupt:
        print('Выход')