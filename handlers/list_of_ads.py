from typing import Dict, Any

from aiogram import F, Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import URLInputFile

import httpx
import json

from pymongo import MongoClient

from keyboards.main_keyboard import make_main_keyboard
from services.get_secret_values import return_secret_value

from middlewares import auth_middlewares

from services.request_to_swipeapi import OrdinaryRequestSwipeAPI

from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

router = Router()
router.message.middleware(auth_middlewares.IsAuthenticatedMiddleware())
router.message.middleware(auth_middlewares.GetJWTAuthenticationMiddleware())


mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')

client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection


class AdsFeedState(StatesGroup):
    total_ads = State()
    total_ads_quantity = State()
    current_ads_index = State()
    warning_message_id = State()




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
# --------------------------------------------------------------------------
# List of ads
@router.message(F.text == __("Оголошення"))
async def list_of_ads_handler(message: types.Message, middleware_access_data: Dict[str, Any] | None, state: FSMContext):

    auth_data = bot_aut_collection.find_one({"chat_id": message.chat.id})

    # in doc header here
    ads_request = OrdinaryRequestSwipeAPI()
    method = 'get'
    url = f"{base_url_secret}/ads/ads-feed/"
    chat_id = message.chat.id
    ads_dict = {"headers":{
        'Authorization': f"Bearer {auth_data['access_token']}"
    }}
    response = ads_request(method, url, chat_id, **ads_dict)

    match response.status_code:
        case 200:
            result = json.loads(response.text)
            await state.update_data(total_ads=result,
                                    total_ads_quantity=len(result),
                                    current_ads_index=0)
            
            first_ads = await state.get_data()
            image_url = f"{ base_url_secret + first_ads['total_ads'][0]['accomodation_data']['main_image']}"
            image_from_url = URLInputFile(image_url)
            new_caption = f"{first_ads['total_ads'][0]['description']}" + f"\n\n1 з {len(result)}"

            await message.answer_photo(
                image_from_url,
                caption=new_caption,
                reply_markup=builder.as_markup()
            )     
            # await message.answer(
            # text=f"{1} з {len(result)}"
            #     )
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



from aiogram.types import InputMediaPhoto
@router.callback_query(F.data == "next_ads")
async def get_next_ads(callback: types.CallbackQuery, state: FSMContext):
    ads_data = await state.get_data()
    current_ads_index = ads_data['current_ads_index']
    last_ads_index = ads_data['total_ads_quantity']
    all_ads = ads_data['total_ads']

    if current_ads_index < last_ads_index:
        if 'warning_message_id' in ads_data and ads_data['warning_message_id'] != None:
            await callback.message.bot.delete_message(chat_id=callback.message.chat.id,
                                                message_id=ads_data['warning_message_id'])
            await state.update_data(warning_message_id=None)
        image_url = f"{ base_url_secret + all_ads[current_ads_index]['accomodation_data']['main_image']}"

        image_from_url = URLInputFile(image_url)

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=image_from_url
            )
        )

        new_caption = f"{all_ads[current_ads_index]['description']}" + f"\n\n{current_ads_index+1} з {last_ads_index}"

        await callback.message.edit_caption(
            caption=new_caption,
            reply_markup=builder.as_markup()
        )

        await state.update_data(current_ads_index=(current_ads_index+1))
        ads_data = await state.get_data()
    else:
        
        if ('warning_message_id' not in ads_data) or (ads_data['warning_message_id']== None):
            warning_message = await callback.message.answer(
                text=_("Це останнє оголошення")
            )
            await state.update_data(warning_message_id=warning_message.message_id)



@router.callback_query(F.data == "previous_ads")
async def previous_next_ads(callback: types.CallbackQuery, state: FSMContext):
    ads_data = await state.get_data()
    current_ads_index = ads_data['current_ads_index']
    last_ads_index = ads_data['total_ads_quantity']
    all_ads = ads_data['total_ads']

    if current_ads_index > 1:

        if 'warning_message_id' in ads_data and ads_data['warning_message_id'] != None:
            await callback.message.bot.delete_message(chat_id=callback.message.chat.id,
                                                message_id=ads_data['warning_message_id'])
            await state.update_data(warning_message_id=None)

        image_url = f"{ base_url_secret + all_ads[current_ads_index-2]['accomodation_data']['main_image']}"
        image_from_url = URLInputFile(image_url)

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=image_from_url
            )
        )
        new_caption = f"{all_ads[current_ads_index-2]['description']}" + f"\n\n{current_ads_index-1} з {last_ads_index}"

        await callback.message.edit_caption(
            caption=new_caption,
            reply_markup=builder.as_markup()
        )
        
        await state.update_data(current_ads_index=(current_ads_index-1))
    else:
        if ('warning_message_id' not in ads_data) or (ads_data['warning_message_id']== None):
            warning_message = await callback.message.answer(
                text=_("Це оголошення найновіше")
            )           
            await state.update_data(warning_message_id=warning_message.message_id)



@router.callback_query(F.data == "get_me_geo")
async def get_geolocation(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_ads_index = data['current_ads_index']
    current_ads = data['total_ads'][current_ads_index - 1]


    await callback.message.reply_location(latitude=current_ads['accomodation_data']['location_x'],
                                                 longitude=current_ads['accomodation_data']['location_y'],
                                                 reply_markup=builder_without_geo.as_markup())
    




