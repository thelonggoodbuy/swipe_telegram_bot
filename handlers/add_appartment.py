from aiogram import F, Router, types

from aiogram import types
from aiogram.utils.i18n import gettext as _
from pymongo import MongoClient
from services.get_secret_values import return_secret_value
from services.request_to_swipeapi import OrdinaryRequestSwipeAPI
import json
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.create_appartment_keyboard import choose_house_keyboard, choose_house_subordinate_obj_kb, choose_from_accomodation_model_dict_kb
from keyboards.create_ads_keyboard import create_ads_keyboard



mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')

type_status_dict = {
    "новобудова":"new_building",
    "вторинне житло":"resale_property",
    "коттедж":"cottage",
}
planing_dict = {
    "студія з санвузлом":"studio_appartment_with_barhroom",
    "студія з санвузлом і однією спальнею":"studio_appartment_with_barhroom_and_one bedroom",
    "двокімнатна":"two_bedroom",
    "двокімнатна зі своєю кришею":"two_bedroom_and_roof",
    "трьокімнатна":"three_bedroom",
    "трьокімнатна зі своєю кришею":"three_bedroom_and_roof",
}
living_condition_dict = {
    "вимагає ремонту":"need_repair",
    "готова для заселення":"reary_for_settlement",
}
heat_type_dict = {
    "газове":"gas",
    "електричний":"electric",
    "дров'яне опалення":"wood_heating",
}


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
    choosen_appartments_nember = State()

    appartments_type = State()
    planning_type = State()
    living_condition = State()
    heat_type = State()

    appartment_schema = State()
    appartment_addition_images = State()

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
    entrances_of_dict = json.loads(response.text)
    entrances_filtered_list = [
        {dictionary['title']: dictionary['id']} for dictionary in entrances_of_dict
        if dictionary['house'] == house_id
    ]
    await state.update_data(all_current_house_entrances=entrances_filtered_list)

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
        if message.text in house_build_dict:
            choose_building_id = house_build_dict[message.text]
            break
    await state.update_data(chosen_building_id=choose_building_id)

    await message.answer(
        text='Оберіть підїзд',
        reply_markup=choose_house_subordinate_obj_kb(current_data['all_current_house_entrances'])
    )
    await state.set_state(AccomodationState.choosen_house_entrances)


import pprint

# принимаем и сохраняем подьезд, запрашиваем этаж
@router.message(AccomodationState.choosen_house_entrances, ~F.text.in_(management_commands_set))
async def get_house_floor(message: types.Message, state: FSMContext):

    # сохраняем подьезд
    current_data = await state.get_data()
    all_current_house_entrances = current_data['all_current_house_entrances']
    for house_entrance_dict in all_current_house_entrances:
        if message.text in house_entrance_dict:
            choose_entrance_id = house_entrance_dict[message.text]
            break
    await state.update_data(choosen_house_entrances=choose_entrance_id)

    # запрашиваем этаж
    await message.answer(
        text='Оберіть поверх',
        reply_markup=choose_house_subordinate_obj_kb(current_data['all_current_house_floor'])
    )
    await state.set_state(AccomodationState.choosen_house_floor)



# принимаем и сохраняем этаж, запрашиваем стояк
@router.message(AccomodationState.choosen_house_floor, ~F.text.in_(management_commands_set))
async def get_house_riser(message: types.Message, state: FSMContext):


    # сохраняем этаж
    current_data = await state.get_data()
    all_current_house_floors = current_data['all_current_house_floor']

    for floor_dict in all_current_house_floors:
        if message.text in floor_dict:
            choose_floor_id = floor_dict[message.text]
            break
    await state.update_data(choosen_house_floor=choose_floor_id)

    # запрашиваем стояк
    await message.answer(
        text='Оберіть стояк',
        reply_markup=choose_house_subordinate_obj_kb(current_data['all_current_house_riser'])
    )
    await state.set_state(AccomodationState.choosen_house_riser)



# принимаем и сохраняем стояк, запрашиваем номер квартиры
@router.message(AccomodationState.choosen_house_riser, ~F.text.in_(management_commands_set))
async def get_appartment_number(message: types.Message, state: FSMContext):

    # сохраняем стояк
    current_data = await state.get_data()
    # -----
    all_current_house_risers = current_data['all_current_house_riser']

    for riser_dict in all_current_house_risers:
        if message.text in riser_dict:
            choose_riser_id = riser_dict[message.text]
            break
    await state.update_data(choosen_house_riser=choose_riser_id)


    # делаем запрос на список квартир
    auth_data = bot_aut_collection.find_one({"chat_id": message.chat.id})
    appartment_request = OrdinaryRequestSwipeAPI()
    method = 'get'
    url = f"{base_url_secret}/ads/accomodation/"
    house_dict = {"headers":{
        'Authorization': f"Bearer {auth_data['access_token']}"
    }}
    response = appartment_request(method, url, message.chat.id, **house_dict)

    list_of_used_numbers = []
    response_list_of_dict = json.loads(response.text)

    for appartment in response_list_of_dict:
        if appartment['house'] == current_data['chosen_house_id']:
            list_of_used_numbers.append(appartment['number'])

    list_of_used_numbers.sort()
    list_of_used_numbers_str = [str(number) for number in list_of_used_numbers]
    used_numbers_str = ', '.join(list_of_used_numbers_str)
    

    # # запрашиваем стояк
    # await message.answer(text='Введіть номер квартири, який не є використаним.')
    # list_of_used_numbers.sort()
    await message.answer(
        text=f'Використовуються такі номера: {used_numbers_str}',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AccomodationState.choosen_appartments_nember)
    # await state.set_state(AccomodationState.choosen_house_riser)


# принимаем и сохраняем номер квартиры, запрашиваем тип квартиры
@router.message(AccomodationState.choosen_appartments_nember, ~F.text.in_(management_commands_set))
async def get_appartment_type(message: types.Message, state: FSMContext):
    await state.update_data(choosen_appartments_nember=message.text)

    await message.answer(
        text='Оберіть тип нерухомості',
        reply_markup=choose_from_accomodation_model_dict_kb(type_status_dict)
    )

    await state.set_state(AccomodationState.appartments_type)



# принимаем и сохраняем тип квартиры, запрашиваем тип планировки
@router.message(AccomodationState.appartments_type, ~F.text.in_(management_commands_set))
async def get_planing_type(message: types.Message, state: FSMContext):
    await state.update_data(appartments_type=message.text)

    await message.answer(
        text='Оберіть планування',
        reply_markup=choose_from_accomodation_model_dict_kb(planing_dict)
    )

    await state.set_state(AccomodationState.planning_type)


# принимаем и сохраняем тип планировки, запрашиваем жилые условия
@router.message(AccomodationState.planning_type, ~F.text.in_(management_commands_set))
async def get_conditions_type(message: types.Message, state: FSMContext):
    await state.update_data(planning_type=message.text)

    await message.answer(
        text='Оберіть умови житла',
        reply_markup=choose_from_accomodation_model_dict_kb(living_condition_dict)
    )

    await state.set_state(AccomodationState.living_condition)


# принимаем и сохраняем условия, запрашиваем тип отопления
@router.message(AccomodationState.living_condition, ~F.text.in_(management_commands_set))
async def get_heat_type(message: types.Message, state: FSMContext):
    await state.update_data(living_condition=message.text)

    await message.answer(
        text='Оберіть тип опалення',
        reply_markup=choose_from_accomodation_model_dict_kb(heat_type_dict)
    )

    await state.set_state(AccomodationState.heat_type)


# принимаем тип отопления, запрашиваем тип схему
@router.message(AccomodationState.heat_type, ~F.text.in_(management_commands_set))
async def get_schema_image(message: types.Message, state: FSMContext):
    await state.update_data(heat_type=message.text)
    await message.answer(
        text='завантажте схему квартири',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AccomodationState.appartment_schema)


# принимаем схему и запрашиваем дополнительные фотографии
@router.message(AccomodationState.appartment_schema, ~F.text.in_(management_commands_set), F.photo)
async def get_appartment_schema(message: types.Message, state: FSMContext):
    await state.update_data(appartment_schema=message.photo[-1].file_id)
    await message.answer(
        text='завантажте додаткові фотографії квартири',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AccomodationState.appartment_addition_images)


# принимаем дополнительные фото и даем результаты
@router.message(AccomodationState.appartment_addition_images, ~F.text.in_(management_commands_set), F.media_group)
async def get_additional_photo(message: types.Message, state: FSMContext):

    print('===========================================')
    pprint.pprint(message.media_group_id)
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print('===========================================')

    data = await state.get_data()
    str_data = str(data)
    await message.answer(
        text=f'Відомості про стани\n\n{str_data}',
        reply_markup=choose_from_accomodation_model_dict_kb(heat_type_dict)
    )
    # await message.reply_photo(
    #     message.photo[-1].file_id
    # )



# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------







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