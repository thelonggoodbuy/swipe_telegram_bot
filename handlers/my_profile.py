from aiogram import F, Router, types
from typing import Dict, Any

import json
from aiogram.fsm.state import State, StatesGroup

from keyboards.main_my_profile_keyboard import make_main_profile_keyboards
from keyboards.main_keyboard import make_main_keyboard
from middlewares import auth_middlewares
from services.get_secret_values import return_secret_value
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.request_to_swipeapi import OrdinaryRequestSwipeAPI
from aiogram.types import URLInputFile

from aiogram.types import InputMediaPhoto

import json
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from pymongo import MongoClient



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
    # data states
    total_ads = State()
    total_ads_quantity = State()
    current_ads_index = State()
    # utility states
    message_id_ads_quantity = State()
    warning_message_id = State()


builder_without_geo = InlineKeyboardBuilder()

builder_without_geo.add(types.InlineKeyboardButton(
        text="<<",
        callback_data="previous_my_ads")
    )
builder_without_geo.add(types.InlineKeyboardButton(
        text=">>",
        callback_data="next_my_ads")
    )

@router.message(F.text == __("Мій профіль"))
async def profile_main_menu(message: types.Message, middleware_access_data: Dict[str, Any] | None):

    await message.answer(
        text=_('Оберіть дію'),
        reply_markup=make_main_profile_keyboards()
    )

import pprint
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
    result_dict[_("ім'я")] = response_dict["first_name"]
    result_dict[_("прізвище")] = response_dict["second_name"]
    result_dict[_("телефон")] = response_dict["phone"]
    match response_dict["phone"]:
        case "for_user":
            result_dict[_("тип оповіщення")] = _("оповещения пользователю")
        case "for_user_and_agent":
            result_dict[_("тип оповіщення")] = _("оповещения пользователю и агенту")
        case "for_agent":
            result_dict[_("тип оповіщення")] = _("оповещению агенту")
        case "disabled":
            result_dict[_("тип оповіщення")] = _("отключить оповещения")

    for field in result_dict.keys():
        if result_dict[field] and result_dict[field] != 'null':
            user_data_string += f"{field}: {result_dict[field]}\n"
        else:
            user_data_string += "{field}: не вказано\n".format(field=field)

    match response.status_code:
        case 200:

            if photo_link:
                await message.answer_photo(
                    photo=image_from_url,
                    caption=user_data_string,
                    reply_markup=make_main_profile_keyboards()
                )
            else:
                await message.answer(
                    text=user_data_string,
                    reply_markup=make_main_profile_keyboards()
                )

        case _:
            await message.answer(
                text=f"{response.text}"
                )
            


@router.message(F.text == __("Мої оголошення"))
async def list_of_my_ads_handler(message: types.Message, middleware_access_data: Dict[str, Any] | None, state: FSMContext):
    auth_data = bot_aut_collection.find_one({"chat_id": message.chat.id})
    ads_request = OrdinaryRequestSwipeAPI()
    method = 'get'
    url = f"{base_url_secret}/ads/ads/"
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
            
            ads_data = await state.get_data()
            image_url = f"{ base_url_secret + ads_data['total_ads'][0]['accomodation_data']['main_image']}"
            image_from_url = URLInputFile(image_url)

            ads = ads_data['total_ads'][0]
            answer = ""
            house = ads['accomodation_data']['address']
            answer += _("Будинок за адрессою {house}".format(house=house))
            floor = ads['accomodation_data']['floor']
            answer += _("\nповерх {floor}".format(floor=floor))
            total_floors = ads['accomodation_data']['total_floors']
            answer += _("\nвсього поверхів {total_floors}".format(total_floors=total_floors))
            area = ads['accomodation_data']['area']
            answer += _("\nплоща {area}".format(area=area))
            cost = ads['cost']
            answer += _("\nціна {cost}".format(cost=cost))
            description = ads['description']
            answer += _("\nопис {description}".format(description=description))
            answer += _("\n\n1 з {len_result}".format(len_result=len(result)))

            await message.answer_photo(
                image_from_url,
                caption=answer,
                reply_markup=builder_without_geo.as_markup()
            )     

            second_ads_id = ads_data['current_ads_index'] + 1
            await state.update_data(total_ads=result,
                                    total_ads_quantity=len(result),
                                    current_ads_index=second_ads_id)

        case 400:
            response_text = response.text
            await message.answer(
            text = str(response_text),
            reply_markup=make_main_profile_keyboards()
            )



@router.callback_query(F.data == "next_my_ads")
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

        ads = all_ads[current_ads_index]
        answer = ""
        house = ads['accomodation_data']['address']
        answer += _("Будинок за адрессою {house}".format(house=house))
        floor = ads['accomodation_data']['floor']
        answer += _("\nповерх {floor}".format(floor=floor))
        total_floors = ads['accomodation_data']['total_floors']
        answer += _("\nвсього поверхів {total_floors}".format(total_floors=total_floors))
        area = ads['accomodation_data']['area']
        answer += _("\nплоща {area}".format(area=area))
        cost = ads['cost']
        answer += _("\nціна {cost}".format(cost=cost))
        description = ads['description']
        answer += _("\nопис {description}".format(description=description))
        answer += _("\n\n{current_ads} з {last_ads_index}".format(current_ads=current_ads_index+1, last_ads_index=last_ads_index))

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=image_from_url
            ),
            reply_markup=builder_without_geo.as_markup()
        )
        await callback.message.edit_caption(
            caption=answer,
            reply_markup=builder_without_geo.as_markup()
        )
        await state.update_data(current_ads_index=(current_ads_index+1))
        ads_data = await state.get_data()
    else:
        if ('warning_message_id' not in ads_data) or (ads_data['warning_message_id']== None):
            warning_message = await callback.message.answer(
                text=_("Це останнє оголошення")
            )
            await state.update_data(warning_message_id=warning_message.message_id)


@router.callback_query(F.data == "previous_my_ads")
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
        ads = all_ads[current_ads_index-2]
        answer = ""
        house = ads['accomodation_data']['address']
        answer += _("Будинок за адрессою {house}".format(house=house))
        floor = ads['accomodation_data']['floor']
        answer += _("\nповерх {floor}".format(floor=floor))
        total_floors = ads['accomodation_data']['total_floors']
        answer += _("\nвсього поверхів {total_floors}".format(total_floors=total_floors))
        area = ads['accomodation_data']['area']
        answer += _("\nплоща {area}".format(area=area))
        cost = ads['cost']
        answer += _("\nціна {cost}".format(cost=cost))
        description = ads['description']
        answer += _("\nопис {description}".format(description=description))
        answer += _("\n\n{current_ads} з {last_ads_index}".format(current_ads=current_ads_index-1, last_ads_index=last_ads_index))
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=image_from_url
            ),
            reply_markup=builder_without_geo.as_markup()
        )
        await callback.message.edit_caption(
            caption=answer,
            reply_markup=builder_without_geo.as_markup()
        )

        await state.update_data(current_ads_index=(current_ads_index-1))
    else:
        if ('warning_message_id' not in ads_data) or (ads_data['warning_message_id']== None):
            warning_message = await callback.message.answer(
                text=_("Це оголошення найновіше")
            )           
            await state.update_data(warning_message_id=warning_message.message_id)



@router.message(F.text == __('Попереднє меню'))
async def go_to_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=_("Головне меню"),
        reply_markup=make_main_keyboard()
    )


