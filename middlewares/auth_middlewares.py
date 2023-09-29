import pymongo

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


import pprint


class IsAuthenticatedMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        auth_pymongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        auth_db = auth_pymongo_client.rptutorial
        auth_collection = auth_db.bot_aut_collection
        user_id = auth_collection.find_one({"chat_id": event.chat.id})

        if user_id:
            return await handler(event, data)
        else:
            return await event.answer(text="Ви не увійшли в систему. Будьласка увійдіть або зареєструйтеся.")
        

import pprint


class GetJWTAuthenticationMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        auth_pymongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        auth_db = auth_pymongo_client.rptutorial
        auth_collection = auth_db.bot_aut_collection
        user_obj = auth_collection.find_one({"chat_id": event.chat.id})

        try:
            middleware_access_data = {"access_token": user_obj["access_token"],
            "refresh_token": user_obj["refresh_token"],
            "email": user_obj["email"]}
            data['middleware_access_data'] = middleware_access_data
        except TypeError:
            pass

        if user_obj:
            return await handler(event, data)
        else:
            return await event.answer(text="Користувач з такими данними є заблоковним.")