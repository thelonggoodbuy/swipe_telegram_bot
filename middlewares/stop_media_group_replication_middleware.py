from aiogram.utils.i18n.middleware import I18nMiddleware
from typing import Any, Dict
import pymongo
from aiogram.types import TelegramObject
from aiogram import types
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware

import pprint




class StopMediaGroupReplicationMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]) -> Any:
        if event.media_group_id:

            media_grop_pymongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
            db = media_grop_pymongo_client.rptutorial
            media_group_collection = db.media_group




            chat_data = media_group_collection.find_one({"chat_id": event.chat.id})
            # print('---------MEDIA---GROUP---IN---MIDDLEWARE---------------')
            # print(chat_data)
            # print('-------------------------------------------------------')

            data_obj = {
                "chat_id": event.chat.id,
                "media_group_id": event.media_group_id
            }
            
            try:
                if chat_data["media_group_id"] == event.media_group_id:
                    pass
                elif chat_data["media_group_id"] != event.media_group_id:
                    media_group_collection.update_one({"chat_id": event.chat.id},\
                                        {"$set": data_obj}, upsert=True)
                    return await handler(event, data)
            except TypeError:
            # if chat_data and "chat_id" not in chat_data:
                media_group_collection.update_one({"chat_id": event.chat.id},\
                                        {"$set": data_obj}, upsert=True)
                return await handler(event, data)
            # try:
                # chat_data["chat_id"]
            # data_obj = {
            #     "chat_id": event.chat.id,
            #     "media_group_id": event.media_group_id
            # }
            # media_group_collection.update_one({"chat_id": event.chat.id},\
            #                             {"$set": data_obj}, upsert=True)
            # except KeyError:
                
            # return await handler(event, data)
        
        else:
            # print('---------WITHIOUT-----MEDIA------GROUP-----AIOGRAMM-----')
            return await handler(event, data)