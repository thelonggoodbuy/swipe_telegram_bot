from aiogram import F, Router, types

from aiogram import types
from aiogram.utils.i18n import gettext as _
from pymongo import MongoClient
from services.get_secret_values import return_secret_value
from services.request_to_swipeapi import OrdinaryRequestSwipeAPI
import json
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.create_ads_keyboard import create_ads_keyboard, choose_version_of_calculation, save_or_change_ads_kayboard
from keyboards.main_keyboard import make_main_keyboard


mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')


class AdsState(StatesGroup):
    chosen_house_id = State()

    all_current_house_buildings = State()
    chosen_building_id = State()

    all_current_house_entrances = State()
    choosen_house_entrances = State()

    all_current_house_floor = State()
    choosen_house_floor = State()

    all_current_house_riser = State()
    choosen_house_riser = State()

    all_used_appartments_numbers = State()
    choosen_appartments_nembers = State()

    appartments_type = State
    planning_type = State()
    living_condition = State()
    heat_type = State()

    is_all_fields_filled = State()


management_commands_set = ['відміна', 'зберігти квартиру',
                           'змінити будинок', 'зміники корпус', 'змінити підїзд',
                           'змінити поверх', 'змінити номер квартири']

client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection


client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection

router = Router()



# @router.message(F.text == 'Створити оголошення')
# async def create_ad(message: types.Message, state: FSMContext):
#     await state.clear()
#     auth_data = bot_aut_collection.find_one({"chat_id": message.chat.id})
#     free_appartments_request = OrdinaryRequestSwipeAPI()
#     method = 'get'
#     url = f"{base_url_secret}/houses/houses/"
#     ads_dict = {"headers":{
#         'Authorization': f"Bearer {auth_data['access_token']}"
#     }}


#     response = free_appartments_request(method, url, message.chat.id, **ads_dict)
#     house_list_of_dict = json.loads(response.text)
#     await state.clear()

#     await state.update_data(
#         free_accomodation_list=accomodation_list_of_dict
#     )
#     await message.answer(
#         text="Оберіть квартиру для оголошення",
#         reply_markup=create_ads_keyboard(accomodation_list_of_dict)
#     )