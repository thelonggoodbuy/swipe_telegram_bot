import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from pathlib import Path
from dotenv import load_dotenv

from handlers import invite, login, sign_up, list_of_ads, main_menu

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

    dp.include_router(invite.router)
    dp.include_router(login.router)
    dp.include_router(sign_up.router)
    dp.include_router(main_menu.router)
    dp.include_router(list_of_ads.router)
    

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())