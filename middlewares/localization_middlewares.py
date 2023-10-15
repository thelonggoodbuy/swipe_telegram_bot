from aiogram.utils.i18n.middleware import SimpleI18nMiddleware
from aiogram.utils.i18n.middleware import I18nMiddleware
from typing import Any, Dict
import pymongo
from aiogram.types import TelegramObject
from aiogram import types

import pprint

class LanguageMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        auth_pymongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        auth_db = auth_pymongo_client.rptutorial
        auth_collection = auth_db.bot_aut_collection

        print('---------------EVENT IN MIDDLEWARE------------------------')
        # print(event.message.chat)
        print(type(event))
        print('----------------------------------------------------------')

        match type(event):
            case types.Message:
                chat_id = event.chat.id
            case types.CallbackQuery:
                chat_id = event.message.chat.id

        chat_data = auth_collection.find_one({"chat_id": chat_id})
        try:
            result = chat_data['chat_language_code']
        except KeyError:
            result = 'uk'
        return result