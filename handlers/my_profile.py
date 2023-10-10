from aiogram import F, Router, types
from typing import Dict, Any

import json

from keyboards.main_my_profile_keyboard import make_main_profile_keyboards
from middlewares import auth_middlewares
from services.get_secret_values import return_secret_value

from services.request_to_swipeapi import OrdinaryRequestSwipeAPI
from aiogram.types import URLInputFile

from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

router = Router()
router.message.middleware(auth_middlewares.IsAuthenticatedMiddleware())
router.message.middleware(auth_middlewares.GetJWTAuthenticationMiddleware())

mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')





@router.message(F.text == __("Мій профіль"))
async def profile_main_menu(message: types.Message, middleware_access_data: Dict[str, Any] | None):


    await message.answer(
        text=_('Оберіть дію'),
        reply_markup=make_main_profile_keyboards()
    )


@router.message(F.text == __("Мої дані"))
async def get_user_data(message: types.Message, middleware_access_data: Dict[str, Any] | None):
    my_profile_request = OrdinaryRequestSwipeAPI()
    method = "get"
    user_id = middleware_access_data['user_id']
    url = f"{base_url_secret}/users/simple_user_update_and_detail/{user_id}/"
    chat_id = message.chat.id
    my_profile_dictionary = {"headers":{
        'Authorization': f"Bearer {middleware_access_data['access_token']}"
    }}
    response = my_profile_request(method, url, chat_id, **my_profile_dictionary)
    user_data_string = ""
    response_dict = json.loads(response.text)

    photo_link = response_dict['photo']

    image_from_url = URLInputFile(photo_link)

    result_dict = {}
    result_dict["ім'я"] = response_dict["first_name"]
    result_dict["прізвище"] = response_dict["second_name"]
    result_dict["телефон"] = response_dict["phone"]
    match response_dict["phone"]:
        case "for_user":
            result_dict["тип оповіщення"] = "оповещения пользователю"
        case "for_user_and_agent":
            result_dict["тип оповіщення"] = "оповещения пользователю и агенту"
        case "for_agent":
            result_dict["тип оповіщення"] = "оповещению агенту"
        case "disabled":
            result_dict["тип оповіщення"] = "отключить оповещения"

    for field in result_dict.keys():
        if result_dict[field] and result_dict[field] != 'null':
            user_data_string += f"{field}: {result_dict[field]}\n"
        else:
            user_data_string += f"{field}: не вказано\n"

    match response.status_code:
        case 200:
            await message.answer_photo(
                image_from_url,
                caption=user_data_string,
                reply_markup=make_main_profile_keyboards()
            )    

        case _:
            await message.answer(
                text=f"{response.text}"
                )
            


@router.message(F.text == __("Мої оголошення"))
async def return_my_ads_list(message: types.Message, middleware_access_data: Dict[str, Any] | None):
    my_ads_list_request = OrdinaryRequestSwipeAPI()
    method = "get"
    # user_id = middleware_access_data['user_id']
    url = f"{base_url_secret}/ads/ads/"
    chat_id = message.chat.id
    my_profile_dictionary = {"headers":{
        'Authorization': f"Bearer {middleware_access_data['access_token']}"
    }}
    response = my_ads_list_request(method, url, chat_id, **my_profile_dictionary)
    await message.answer(
        text=response.text,
        reply_markup=make_main_profile_keyboards()
    )
    