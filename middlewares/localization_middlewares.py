from aiogram.utils.i18n.middleware import SimpleI18nMiddleware
from aiogram.utils.i18n.middleware import I18nMiddleware
from typing import Any, Dict
import pymongo
from aiogram.types import TelegramObject
from aiogram import types
from services.get_secret_values import return_secret_value

import pprint

mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')

class LanguageMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        auth_pymongo_client = pymongo.MongoClient(mongo_url_secret)
        auth_db = auth_pymongo_client.rptutorial
        auth_collection = auth_db.bot_aut_collection

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