import asyncio
import logging

from aiogram import Bot, Dispatcher
from handlers import invite, login, sign_up, list_of_ads, main_menu
from services.get_secret_values import return_secret_value
from aiogram.fsm.storage.redis import RedisStorage



async def main():

    bot_token_secret = return_secret_value("BOT_TOKEN")
    redis_url_secret = return_secret_value("REDIS_STORAGE_URL")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
    bot = Bot(token=bot_token_secret, parse_mode="HTML")
    redis_storage = RedisStorage.from_url(redis_url_secret)
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