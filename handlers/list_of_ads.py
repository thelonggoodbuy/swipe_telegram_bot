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

from aiogram.methods.send_location import SendLocation



from aiogram.fsm.context import FSMContext

from aiogram.utils.keyboard import InlineKeyboardBuilder


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


builder = InlineKeyboardBuilder()

builder.add(types.InlineKeyboardButton(
        text="<<",
        callback_data="previous_ads")
    )
builder.add(types.InlineKeyboardButton(
        text="показати геолокацію",
        callback_data="get_me_geo")
    )
builder.add(types.InlineKeyboardButton(
        text=">>",
        callback_data="next_ads")
    )

builder_without_geo = InlineKeyboardBuilder()

builder_without_geo.add(types.InlineKeyboardButton(
        text="<<",
        callback_data="previous_ads")
    )
builder_without_geo.add(types.InlineKeyboardButton(
        text=">>",
        callback_data="next_ads")
    )

# List of ads
@router.message(F.text == "Оголошення")
async def list_of_ads_handler(message: types.Message, middleware_access_data: Dict[str, Any] | None, state: FSMContext):

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
                basic_url = 'http://127.0.0.1:8000'
            

                await state.update_data(total_ads=result,
                                        total_ads_quantity=len(result),
                                        current_ads_index=0)

                # state_data = await state.get_data()
                # print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                # print(state_data)
                # print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')



                # for ads in result:
                #     await message.answer(
                #         text=str(ads)
                #     )
                #     await message.answer(
                #         text = f"link to image is { basic_url + ads['accomodation_data']['main_image']}"
                #     )
                #     image_url = f"{ basic_url + ads['accomodation_data']['main_image']}"

                #     image_from_url = URLInputFile(image_url)

                #     await message.answer_photo(
                #         image_from_url,
                #         caption="Зображення будинку",
                #     )
                #     # await message.reply_location(latitude=50.4442097549618, longitude=30.549555457035364)
                #     await message.reply_location(latitude=ads['accomodation_data']['location_x'],
                #                                  longitude=ads['accomodation_data']['location_y'])


                
                first_ads = await state.get_data()

                # print('==================================================')
                # pprint.pprint(first_ads)
                # print('==================================================')

                image_url = f"{ basic_url + first_ads['total_ads'][0]['accomodation_data']['main_image']}"

                image_from_url = URLInputFile(image_url)

                await message.answer_photo(
                    image_from_url,
                    caption=first_ads['total_ads'][0]['description'],
                    reply_markup=builder.as_markup()
                )
                

                await message.answer(
                text=f"{1} з {len(result)}"
                    )
                second_ads_id = first_ads['current_ads_index'] + 1

                await state.update_data(total_ads=result,
                                        total_ads_quantity=len(result),
                                        current_ads_index=second_ads_id)


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

                if response.status_code == 401:
                    print(response.text)



@router.callback_query(F.data == "next_ads")
async def get_next_ads(callback: types.CallbackQuery, state: FSMContext):
    ads_data = await state.get_data()
    current_ads_index = ads_data['current_ads_index']
    last_ads_index = ads_data['total_ads_quantity']
    all_ads = ads_data['total_ads']

    if current_ads_index < last_ads_index:
        basic_url = 'http://127.0.0.1:8000'
        image_url = f"{ basic_url + all_ads[current_ads_index]['accomodation_data']['main_image']}"
        image_from_url = URLInputFile(image_url)
        await callback.message.answer_photo(
            image_from_url,
            caption=all_ads[current_ads_index]['description'],
            reply_markup=builder.as_markup()
        )
        await callback.message.answer(
            text=f"{current_ads_index+1} з {last_ads_index}"
        )
        await state.update_data(current_ads_index=(current_ads_index+1))
        ads_data = await state.get_data()
    else:
        await callback.message.answer(
            text="Це останнє оголошення"
        )



@router.callback_query(F.data == "previous_ads")
async def previous_next_ads(callback: types.CallbackQuery, state: FSMContext):
    ads_data = await state.get_data()
    current_ads_index = ads_data['current_ads_index']
    last_ads_index = ads_data['total_ads_quantity']
    all_ads = ads_data['total_ads']

    if current_ads_index > 1:
        basic_url = 'http://127.0.0.1:8000'

        image_url = f"{ basic_url + all_ads[current_ads_index-2]['accomodation_data']['main_image']}"
        image_from_url = URLInputFile(image_url)
        await callback.message.answer_photo(
            image_from_url,
            caption=all_ads[current_ads_index-2]['description'],
            reply_markup=builder.as_markup()
        )
        await callback.message.answer(
            text=f"{current_ads_index-1} з {last_ads_index}"
        )
        await state.update_data(current_ads_index=(current_ads_index-1))
    else:
        await callback.message.answer(
            text="Це оголошення найновіше"
        )


@router.callback_query(F.data == "get_me_geo")
async def get_geolocation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print('===========================================================')
    pprint.pprint(data)
    print('===========================================================')
    current_ads_index = data['current_ads_index']
    current_ads = data['total_ads'][current_ads_index - 1]


    await callback.message.reply_location(latitude=current_ads['accomodation_data']['location_x'],
                                                 longitude=current_ads['accomodation_data']['location_y'],
                                                 reply_markup=builder_without_geo.as_markup())