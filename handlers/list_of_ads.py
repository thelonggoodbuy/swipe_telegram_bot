from aiogram import F, Router, types
from middlewares import auth_middlewares

import httpx
import json

from pymongo import MongoClient

import pprint

from typing import Dict, Any
from keyboards.main_keyboard import make_main_keyboard


router = Router()
router.message.middleware(auth_middlewares.IsAuthenticatedMiddleware())
router.message.middleware(auth_middlewares.GetJWTAuthenticationMiddleware())


client = MongoClient("mongodb://localhost:27017/")
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection



# List of ads
@router.message(F.text == "Список оголошень")
async def list_of_ads_handler(message: types.Message, middleware_access_data: Dict[str, Any] | None):

    # await message.reply("Ви намагаєтеся отримати список оголошень. Функція пока не розроблена.")
    # await message.reply(middleware_access_data)

    await message.reply("Всі оголошення разом:")

    auth_data = bot_aut_collection.find_one({"chat_id": message.chat.id})

    print('----------------------')
    print(auth_data['access_token'])
    print('----------------------')

    # in doc header here
    with httpx.Client() as client:
        url = "http://127.0.0.1:8000/ads/ads-feed/"

        client.headers['Authorization'] = f"Bearer {auth_data['access_token']}"

        # data = {"email": auth_data['users_email'], "password": auth_data['users_password']}

        # (client)

        response = client.get(url, timeout=10.0)



        # response_dict = json.loads(response.text)

        match response.status_code:
            case 200:

                # auth_object = {"chat_id": message.chat.id,
                #                "email": response_dict["email"],
                #                "access_token": response_dict["tokens"]["access"],
                #                "refresh_token": response_dict["tokens"]["refresh"]}
                
                # bot_aut_collection.update_one({"chat_id": message.chat.id},\
                #                                {"$set": auth_object}, upsert=True)
                
                # response_text = f"Ви увійшли в бот як {response_dict['email']}"
                # await message.answer(
                # text = str(response.text)
                # )

                print('------------------------------------------------------------------------')
                pprint.pprint(response.text)
                print(type(response.text))
                result = json.loads(response.text)
                print('========================================================================')
                print(result)
                print('------------------------------------------------------------------------')
                await message.answer(
                text = "Все ок!",
                reply_markup=make_main_keyboard()
               )
                
            case 400:
                response_text = response.text
                await message.answer(
                text = str(response_text),
                reply_markup=make_main_keyboard()
                )

            case 401:
                print('-----401')
                data = {'refresh': auth_data['refresh_token']}

                url = "http://127.0.0.1:8000/api/token/refresh/"

                response = client.post(url, data=data, timeout=10.0)

                if response.status_code == 200:
                    response_data = json.loads(response.text)
                    new_access_token = response_data['access']
                    bot_aut_collection.update_one({"chat_id": message.chat.id},\
                                               {"$set": {"access_token": new_access_token}}, upsert=False)
                    
                    url = "http://127.0.0.1:8000/ads/ads-feed/"
                    client.headers['Authorization'] = f"Bearer {response_data['access']}"
                    response = client.get(url, timeout=10.0)
                    print('--------------YOU----FINISH----REFRESSH----TOKEN---!!!!-')
                    print(response.text)


                if response.status_code == 401:
                    print('=====SMTH===WITH====REFRESH=====')
                    print(response.text)
