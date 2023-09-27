from datetime import datetime

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, html, F

from pathlib import Path
import os

from dotenv import load_dotenv
from pathlib import Path

from handlers import common

from aiogram.fsm.storage.redis import RedisStorage



# runing pullong proccess new updates
async def main():
    dotenv_path = Path(__file__).parent
    real_path = dotenv_path.joinpath(dotenv_path, '.env')
    load_dotenv(dotenv_path=real_path)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )

    bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode="HTML")

    redis_storage = RedisStorage.from_url('redis://localhost:6379')

    dp = Dispatcher(storage=redis_storage)

    # ---------work-----area----------
    dp.include_router(common.router)
    # -------end--work---area---------

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())