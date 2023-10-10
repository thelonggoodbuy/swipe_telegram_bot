import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from handlers import invite, login, sign_up, list_of_ads, main_menu, my_profile, change_language
from services.get_secret_values import return_secret_value
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n


# indrnationalization meddleware import =================================
from aiogram.utils.i18n.middleware import I18nMiddleware
from typing import Any, Awaitable, Callable, Dict, Optional, Set
import pymongo
from aiogram.types import TelegramObject, User
# =======================================================================

# indrnationalization middleware=========================================
class LanguageMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        # print('!!!!!language_middleware!!!!!!')
        auth_pymongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        auth_db = auth_pymongo_client.rptutorial
        auth_collection = auth_db.bot_aut_collection
        chat_data = auth_collection.find_one({"chat_id": event.chat.id})
        try:
            result = chat_data['chat_language_code']
        except KeyError:
            result = 'uk'
        return result
# ========================================================================

async def main():

    WORKDIR = Path(__file__).parent
    i18n = I18n(path=WORKDIR / "locales", default_locale="uk", domain="messages")
    # i18b_middleware = I18nMiddleware(i18n)



    bot_token_secret = return_secret_value("BOT_TOKEN")
    redis_url_secret = return_secret_value("REDIS_STORAGE_URL")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
    bot = Bot(token=bot_token_secret, parse_mode="HTML")
    redis_storage = RedisStorage.from_url(redis_url_secret)
    dp = Dispatcher(storage=redis_storage)

    dp.message.outer_middleware(LanguageMiddleware(i18n))
    dp.inline_query.outer_middleware(LanguageMiddleware(i18n))
    # dp.message.outer_middleware(LanguageMiddleware(i18n))
    # dp.message.middleware(LanguageMiddleware(i18n))

    dp.include_router(invite.router)
    dp.include_router(login.router)
    dp.include_router(sign_up.router)
    dp.include_router(main_menu.router)
    dp.include_router(list_of_ads.router)
    dp.include_router(my_profile.router)
    dp.include_router(change_language.router)

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())