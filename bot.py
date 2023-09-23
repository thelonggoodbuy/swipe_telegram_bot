from datetime import datetime

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, html, F
from aiogram.filters.command import Command

from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.filters import CommandObject
from aiogram.fsm.storage.memory import MemoryStorage
# from config_reader import config

from pathlib import Path
import os

from dotenv import load_dotenv
from pathlib import Path

# from handlers import group_games, usernames,\
#                      checkin, common, ordering_food

from handlers import group_games, usernames,\
                     checkin, common, ordering_food


from middlewares.weekend import WeekendCallbackMiddleware


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
    dp = Dispatcher(storage=MemoryStorage())

    # ---------work-----area----------

    # dp.include_router(group_games.router)
    # dp.include_router(usernames.router)
    # dp.include_router(checkin.router)
    dp.include_router(common.router)
    # dp.include_router(ordering_food.router)

    # dp.callback_query.outer_middleware(WeekendCallbackMiddleware())

    # -------end--work---area---------

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())