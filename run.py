import asyncio
import logging

from aiogram import Dispatcher

from app.handlers import router
from database.db_operations import init_db
from config_reader import bot

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def main():
    logger.info("Запуск бота...")
    dp = Dispatcher()
    dp.include_router(router)
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
