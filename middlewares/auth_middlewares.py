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
        # print('-------------2---------------')
        # print(event.chat.id)
        # print('----------STOP---------------')
        # auth_pymongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        # auth_db = auth_pymongo_client["rptutorial"]
        # auth_collection = auth_db["bot_auth_collection"]


        auth_pymongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        auth_db = auth_pymongo_client.rptutorial
        auth_collection = auth_db.bot_aut_collection


        # user_id = auth_collection.find_one({"chat_id": event.chat.id})
        user_id = auth_collection.find_one({"chat_id": event.chat.id})
        print('-------1--------')
        print(auth_pymongo_client)
        print('-------2--------')
        print(auth_db)
        print('-------3--------')
        print(auth_collection)
        print('-------4--------')
        print('---||||||||-----')
        print(type(event.chat.id))
        print('-------5--------')
        print(user_id)
        print('-------6--------')
        print(auth_collection.find())
        for auth_position in auth_collection.find():
            pprint.pprint(auth_position)
        print('-----FINISH-----')

        if user_id:
            return await handler(event, data)
        else:
            return await event.answer(text="Ви не увійшли в систему. Будьласка увійдіть або зареєструйтеся.")