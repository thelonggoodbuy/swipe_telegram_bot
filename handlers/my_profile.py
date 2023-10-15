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

from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

router = Router()
router.message.middleware(auth_middlewares.IsAuthenticatedMiddleware())
router.message.middleware(auth_middlewares.GetJWTAuthenticationMiddleware())

mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')

class AdsFeedState(StatesGroup):
    # data states
    total_ads = State()
    total_ads_quantity = State()
    current_ads_index = State()
    # utility states
    message_id_ads_quantity = State()


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
            
import json
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from pymongo import MongoClient

client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection


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
            answer += "\nБудинок за адрессою {house}".format(house=house)
            floor = ads['accomodation_data']['floor']
            answer += "\nповерх {floor}".format(floor=floor)
            total_floors = ads['accomodation_data']['total_floors']
            answer += "\nвсього поверхів {total_floors}".format(total_floors=total_floors)
            area = ads['accomodation_data']['area']
            answer += "\nплоща {area}".format(area=area)
            cost = ads['cost']
            answer += "\nціна {cost}".format(cost=cost)
            description = ads['description']
            answer += "\nопис {description}".format(description=description)
            answer += f"\n\n{1} з {len(result)}"

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

from aiogram.types import InputMediaPhoto

@router.callback_query(F.data == "next_my_ads")
async def get_next_ads(callback: types.CallbackQuery, state: FSMContext):
    ads_data = await state.get_data()
    current_ads_index = ads_data['current_ads_index']
    last_ads_index = ads_data['total_ads_quantity']
    all_ads = ads_data['total_ads']

    if current_ads_index < last_ads_index:
        image_url = f"{ base_url_secret + all_ads[current_ads_index]['accomodation_data']['main_image']}"
        image_from_url = URLInputFile(image_url)

        ads = all_ads[current_ads_index]
        answer = ""
        house = ads['accomodation_data']['address']
        answer += "\nБудинок за адрессою {house}".format(house=house)
        floor = ads['accomodation_data']['floor']
        answer += "\nповерх {floor}".format(floor=floor)
        total_floors = ads['accomodation_data']['total_floors']
        answer += "\nвсього поверхів {total_floors}".format(total_floors=total_floors)
        area = ads['accomodation_data']['area']
        answer += "\nплоща {area}".format(area=area)
        cost = ads['cost']
        answer += "\nціна {cost}".format(cost=cost)
        description = ads['description']
        answer += "\nопис {description}".format(description=description)
        answer += f"\n\n{current_ads_index+1} з {last_ads_index}"

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
        await callback.message.answer(
            text=_("Це останнє оголошення")
        )


@router.callback_query(F.data == "previous_my_ads")
async def previous_next_ads(callback: types.CallbackQuery, state: FSMContext):
    ads_data = await state.get_data()
    current_ads_index = ads_data['current_ads_index']
    last_ads_index = ads_data['total_ads_quantity']
    all_ads = ads_data['total_ads']

    if current_ads_index > 1:
        image_url = f"{ base_url_secret + all_ads[current_ads_index-2]['accomodation_data']['main_image']}"
        image_from_url = URLInputFile(image_url)
        ads = all_ads[current_ads_index-2]
        answer = ""
        house = ads['accomodation_data']['address']
        answer += "\nБудинок за адрессою {house}".format(house=house)
        floor = ads['accomodation_data']['floor']
        answer += "\nповерх {floor}".format(floor=floor)
        total_floors = ads['accomodation_data']['total_floors']
        answer += "\nвсього поверхів {total_floors}".format(total_floors=total_floors)
        area = ads['accomodation_data']['area']
        answer += "\nплоща {area}".format(area=area)
        cost = ads['cost']
        answer += "\nціна {cost}".format(cost=cost)
        description = ads['description']
        answer += "\nопис {description}".format(description=description)
        answer += f"\n\n{current_ads_index-1} з {last_ads_index}"
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
        await callback.message.answer(
            text=_("Це оголошення найновіше")
        )


@router.message(F.text == __('Попереднє меню'))
async def go_to_main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=_("Головне меню"),
        reply_markup=make_main_keyboard()
    )












# # -----------------------------------------------------------------------------------
# list_of_test_texts = ['первый текст', 'второй текст']

# builder_for_editing = InlineKeyboardBuilder()
# builder_for_editing.add(types.InlineKeyboardButton(
#     text="change_current_inline_text",
#     callback_data="change_current_inline_text")
# )



# @router.message(F.text == 'Test update data inline button')
# async def start_test_update_data(message: types.Message):

#     await message.answer(text = list_of_test_texts[0],
#                          reply_markup=builder_for_editing.as_markup())
    


# @router.callback_query(F.data == "change_current_inline_text")
# async def change_text(callback: types.CallbackQuery):
#     if callback.message.text == list_of_test_texts[0]:
#         text = list_of_test_texts[1]
#     else:
#         text = list_of_test_texts[0]

#     await callback.message.edit_text(
#         text=text,
#         reply_markup=builder_for_editing.as_markup()
#     )





# from services.get_secret_values import return_secret_value
# bot_token_secret = return_secret_value("BOT_TOKEN")
# from aiogram import Bot

# bot = Bot(token=bot_token_secret, parse_mode="HTML")


# # simple message editing
# class ChangeSimpleButtonState(StatesGroup):
#     # data states
#     previous_message_id = State()


# @router.message(F.text == 'Test update simpe button')
# async def make_simple_message(message: types.Message, state: FSMContext):
#     await state.update_data(previous_message_id=message.message_id)
#     print('------message---id')
#     print(message.message_id)
#     print('------------------')
#     await message.answer(
#         text='BASE text status',
#         reply_markup=make_main_profile_keyboards()
#     )


# @router.message(F.text == 'UPDATE SIMPLE BUTTON')
# async def change_simple_button(message: types.Message, state: FSMContext):
#     data = await state.get_data()
    
#     print('----previous--message--id----')
#     print(data['previous_message_id'])
#     print('-----------------------------')
#     previous_message_id = data['previous_message_id']

#     bot.edit_message_text(chat_id=message.chat.id, message_id=previous_message_id, text="EDITED!!!!!")

#     await message.answer(
#         # message_id=previous_message_id,
#         text='you change smth!',
#         reply_markup=make_main_profile_keyboards()
#     )