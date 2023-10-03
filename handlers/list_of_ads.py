from aiogram import F, Router, types
from aiogram.fsm.state import State, StatesGroup

from typing import Dict, Any

import httpx
import json
import pprint

from pymongo import MongoClient

from keyboards.main_keyboard import make_main_keyboard
from middlewares import auth_middlewares
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile



router = Router()
router.message.middleware(auth_middlewares.IsAuthenticatedMiddleware())
router.message.middleware(auth_middlewares.GetJWTAuthenticationMiddleware())


client = MongoClient("mongodb://localhost:27017/")
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection


class AdsFeedState(StatesGroup):
    total_ads = State()
    total_ads_quantity = State()
    current_ads_index = State()


# List of ads
@router.message(F.text == "Список оголошень")
async def list_of_ads_handler(message: types.Message, middleware_access_data: Dict[str, Any] | None):

    await message.reply("Всі оголошення разом:")

    auth_data = bot_aut_collection.find_one({"chat_id": message.chat.id})

    # in doc header here
    with httpx.Client() as client:
        url = "http://127.0.0.1:8000/ads/ads-feed/"
        client.headers['Authorization'] = f"Bearer {auth_data['access_token']}"
        response = client.get(url, timeout=10.0)
        match response.status_code:
            case 200:
                result = json.loads(response.text)
                print('========================================================================')
                print(result)
                print('------------------------------------------------------------------------')

                basic_url = 'http://127.0.0.1:8000'

                for ads in result:
                    await message.answer(
                        text=str(ads)
                    )
                    await message.answer(
                        text = f"link to image is { basic_url + ads['accomodation_data']['main_image']}"
                    )
                    image_url = f"{ basic_url + ads['accomodation_data']['main_image']}"

                    image_from_url = URLInputFile(image_url)

                    await message.answer_photo(
                        image_from_url,
                        caption="Зображення будинку"
                    )

                
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
                    print(response.text)
