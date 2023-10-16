from aiogram import F, Router, types

from aiogram import types
from aiogram.utils.i18n import gettext as _
from pymongo import MongoClient
from services.get_secret_values import return_secret_value
from services.request_to_swipeapi import OrdinaryRequestSwipeAPI
import json
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.create_appartment_keyboard import choose_house_keyboard, choose_house_subordinate_obj_kb
from keyboards.create_ads_keyboard import create_ads_keyboard


mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')


class AccomodationState(StatesGroup):
    chosen_house_id = State()
    houses_hash_dict = State()

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


management_commands_set = ['відміна', 'зберігти квартиру', 'Зробити оголошення з існуючою квартирою',
                           'змінити будинок', 'зміники корпус', 'змінити підїзд',
                           'змінити поверх', 'змінити номер квартири']


client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection

router = Router()


@router.message(F.text == 'Додати квартиру')
async def add_appartment(message: types.Message, state: FSMContext):
    await state.clear()
    auth_data = bot_aut_collection.find_one({"chat_id": message.chat.id})
    users_houses_request = OrdinaryRequestSwipeAPI()
    method = 'get'
    url = f"{base_url_secret}/houses/houses/"
    house_dict = {"headers":{
        'Authorization': f"Bearer {auth_data['access_token']}"
    }}
    response = users_houses_request(method, url, message.chat.id, **house_dict)
    house_list_of_dict = json.loads(response.text)
    house_buttons_list = []
    houses_hash_dict = {}
    for house in house_list_of_dict:
        house_buttons_list.append((house['id'], house['description'], house['address']))
        hash_key = f"{house['description']}__{house['address']}"
        houses_hash_dict[hash_key] = house['id']
    await state.update_data(houses_hash_dict=houses_hash_dict)
    await message.answer(
        text="Оберіть будинок",
        reply_markup=choose_house_keyboard(house_buttons_list)
    )
    await state.set_state(AccomodationState.chosen_house_id)




@router.message(AccomodationState.chosen_house_id, ~F.text.in_(management_commands_set))
async def get_house_data_and_choose_house_builing(message: types.Message, state: FSMContext):
    appartment_string = message.text
    appartment_clean_string = appartment_string.lstrip('ЖК ')
    appartment_clean_list = appartment_clean_string.split(' за адресою ')
    appartment_hash = '__'.join(appartment_clean_list)
    state_data = await state.get_data()
    house_id = state_data['houses_hash_dict'][appartment_hash]

    #  get and filter house buildings
    auth_data = bot_aut_collection.find_one({"chat_id": message.chat.id})
    get_house_buildings_request = OrdinaryRequestSwipeAPI()
    method = 'get'
    url = f"{base_url_secret}/houses/houses_building/"
    ads_dict = {"headers":{
        'Authorization': f"Bearer {auth_data['access_token']}"
    }}
    response = get_house_buildings_request(method, url, message.chat.id, **ads_dict)
    house_building_list_of_dict = json.loads(response.text)
    house_building_filtered_list = [
        {dictionary['title']: dictionary['id']} for dictionary in house_building_list_of_dict
        if dictionary['house'] == house_id
    ]
    await state.update_data(all_current_house_buildings=house_building_filtered_list)

   #  get and filter risers
    get_risers_request = OrdinaryRequestSwipeAPI()
    method = 'get'
    url = f"{base_url_secret}/houses/house_riser/"
    ads_dict = {"headers":{
        'Authorization': f"Bearer {auth_data['access_token']}"
    }}
    response = get_risers_request(method, url, message.chat.id, **ads_dict)
    riser_list_of_dict = json.loads(response.text)
    riser_filtered_list = [
        {dictionary['title']: dictionary['id']} for dictionary in riser_list_of_dict
        if dictionary['house'] == house_id
    ]
    await state.update_data(all_current_house_riser=riser_filtered_list)

    #  get and filter floor
    get_risers_request = OrdinaryRequestSwipeAPI()
    method = 'get'
    url = f"{base_url_secret}/houses/house_floor/"
    ads_dict = {"headers":{
        'Authorization': f"Bearer {auth_data['access_token']}"
    }}
    response = get_risers_request(method, url, message.chat.id, **ads_dict)
    floor_list_of_dict = json.loads(response.text)
    floor_filtered_list = [
        {dictionary['title']: dictionary['id']} for dictionary in floor_list_of_dict
        if dictionary['house'] == house_id
    ]
    await state.update_data(all_current_house_floor=floor_filtered_list)

    #  get and filter entrances
    get_entrances_request = OrdinaryRequestSwipeAPI()
    method = 'get'
    url = f"{base_url_secret}/houses/house_entrance/"
    entrances_dict = {"headers":{
        'Authorization': f"Bearer {auth_data['access_token']}"
    }}
    response = get_entrances_request(method, url, message.chat.id, **entrances_dict)
    floor_entrances_of_dict = json.loads(response.text)
    floor_filtered_list = [
        {dictionary['title']: dictionary['id']} for dictionary in floor_entrances_of_dict
        if dictionary['house'] == house_id
    ]
    await state.update_data(all_current_house_entrances=floor_entrances_of_dict)

    state_data = await state.get_data()

    await state.update_data(chosen_house_id = house_id)
    await message.answer(
        text='Оберіть корпус',
        reply_markup=choose_house_subordinate_obj_kb(house_building_filtered_list)
    )
    await state.set_state(AccomodationState.chosen_building_id)



@router.message(AccomodationState.chosen_building_id, ~F.text.in_(management_commands_set))
async def get_house_entrance(message: types.Message, state: FSMContext):
    current_data = await state.get_data()
    choosen_house_buildig = current_data['all_current_house_buildings']
    for house_build_dict in choosen_house_buildig:
        if house_build_dict[message.text]:
            choose_building_id = house_build_dict[message.text]
            break
    await state.update_data(chosen_building_id=choose_building_id)


    await message.answer(
        text='Оберіть підїзд',
        reply_markup=choose_house_subordinate_obj_kb(current_data['all_current_house_entrances'])
    )
    await state.set_state(AccomodationState.choosen_house_entrances)


# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------

# принимаем и сохраняем подьез, запрашиваем этаж
@router.message(AccomodationState.choosen_house_entrances, ~F.text.in_(management_commands_set))
async def get_house_entrance(message: types.Message, state: FSMContext):
    current_data = await state.get_data()
    choosen_house_floors = current_data['choosen_house_floor']


    for house_floor_dict in choosen_house_floors:
        if house_floor_dict[message.text]:
            choose_floor_id = house_floor_dict[message.text]
            break
    await state.update_data(choosen_house_floor=choose_floor_id)


    await message.answer(
        text='Оберіть підїзд',
        reply_markup=choose_house_subordinate_obj_kb(current_data['all_current_house_entrances'])
    )
    await state.set_state(AccomodationState.choosen_house_entrances)





@router.message(F.text == 'Зробити оголошення з існуючою квартирою')
async def return_to_previous_menu(message: types.Message, state: FSMContext):
    await state.clear()
    auth_data = bot_aut_collection.find_one({"chat_id": message.chat.id})
    free_appartments_request = OrdinaryRequestSwipeAPI()
    method = 'get'
    url = f"{base_url_secret}/ads/accomodation_without_ads/"
    ads_dict = {"headers":{
        'Authorization': f"Bearer {auth_data['access_token']}"
    }}
    response = free_appartments_request(method, url, message.chat.id, **ads_dict)
    accomodation_list_of_dict = json.loads(response.text)
    await state.clear()
    await state.update_data(
        free_accomodation_list=accomodation_list_of_dict
    )
    await message.answer(
        text="Оберіть квартиру для оголошення",
        reply_markup=create_ads_keyboard(accomodation_list_of_dict)
    )