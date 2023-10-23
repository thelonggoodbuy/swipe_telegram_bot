from aiogram.utils.i18n.middleware import I18nMiddleware
from typing import Any, Dict
import pymongo
from aiogram.types import TelegramObject
from aiogram import types
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware

import pprint
import base64


from services.get_secret_values import return_secret_value
mongo_url_secret = return_secret_value('MONGO_URL')


class MediaGroupCounterMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]) -> Any:

        if event.media_group_id:
            media_grop_couter_client = pymongo.MongoClient(mongo_url_secret)
            db = media_grop_couter_client.rptutorial
            media_group_counter = db.media_group_counter
            chat_data = media_group_counter.find_one({"chat_id": event.chat.id})
            try:
                if chat_data["media_group_id"] == event.media_group_id:
                    image_number = chat_data["counter"] + 1
                    image_list = chat_data["image_list_id"]
                    image_list.append(event.photo[-1].file_id)

                    data_obj = {
                        "chat_id": event.chat.id,
                        "media_group_id": event.media_group_id,
                        "counter": image_number,
                        "image_list_id": image_list
                        }
                    media_group_counter.update_one({"chat_id": event.chat.id},\
                                            {"$set": data_obj}, upsert=True)
                elif chat_data["media_group_id"] != event.media_group_id:
                    image_list_id = [event.photo[-1].file_id,]
                    data_obj = {
                        "chat_id": event.chat.id,
                        "media_group_id": event.media_group_id,
                        "counter": 1,
                        "image_list_id": image_list_id
                        }
                    media_group_counter.update_one({"chat_id": event.chat.id},\
                                            {"$set": data_obj}, upsert=True)
                return await handler(event, data)
            
            except TypeError:
                image_list_id = [event.photo[-1].file_id,]
                data_obj = {
                        "chat_id": event.chat.id,
                        "media_group_id": event.media_group_id,
                        "counter": 1,
                        "image_list_id": image_list_id
                        }
                media_group_counter.update_one({"chat_id": event.chat.id},\
                                            {"$set": data_obj}, upsert=True)
                return await handler(event, data)
            
        else:
             return await handler(event, data)






class StopMediaGroupReplicationMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]) -> Any:

        if event.media_group_id:

            media_grop_pymongo_client = pymongo.MongoClient(mongo_url_secret)
            db = media_grop_pymongo_client.rptutorial
            media_group_collection = db.media_group

            chat_data = media_group_collection.find_one({"chat_id": event.chat.id})

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
                media_group_collection.update_one({"chat_id": event.chat.id},\
                                        {"$set": data_obj}, upsert=True)
                return await handler(event, data)

        else:
            return await handler(event, data)