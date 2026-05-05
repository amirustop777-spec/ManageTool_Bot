import asyncio
import logging
import time
from typing import Callable, Dict, Any, Awaitable

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.types import Message

from config import TOKEN
from app.handlers import router
from database import DataBase

# инициализируем базу данных
db = DataBase("manage_tool.db")

# Middleware для базы данных
class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, db_instance: DataBase):
        self.db = db_instance

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data['db'] = self.db  
        return await handler(event, data)

# Middleware против спама
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

async def main():
    # инициализация бота
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # настройка базы данных (создание таблицы )
    await db.setup()

    # регистрация Middleware
    dp.message.outer_middleware(ThrottlingMiddleware(limit=1))
    dp.message.middleware(DatabaseMiddleware(db))

    # подключение роутеров
    dp.include_router(router)

    logging.info("Бот запущен и база готова!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Выход')