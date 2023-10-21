from aiogram import F, Router, types

from aiogram import types
from aiogram.utils.i18n import gettext as _
from pymongo import MongoClient
from services.get_secret_values import return_secret_value
from services.request_to_swipeapi import OrdinaryRequestSwipeAPI
import json
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.create_appartment_keyboard import choose_house_keyboard, \
                                                choose_house_subordinate_obj_kb,\
                                                choose_from_accomodation_model_dict_kb,\
                                                save_or_change_accomodation_kb
from keyboards.create_ads_keyboard import create_ads_keyboard
from keyboards.main_keyboard import make_main_keyboard


from middlewares.stop_media_group_replication_middleware import StopMediaGroupReplicationMiddleware, MediaGroupCounterMiddleware


import pymongo
import base64
from aiogram.utils.media_group import MediaGroupBuilder



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
    chosen_house_title = State()
    houses_hash_dict = State()

    all_current_house_buildings = State()
    chosen_building_title = State()
    chosen_building_id = State()

    all_current_house_entrances = State()
    choosen_house_entrances_title = State()
    choosen_house_entrances = State()

    all_current_house_floor = State()
    choosen_house_floor_title = State()
    choosen_house_floor = State()

    all_current_house_riser = State()
    choosen_house_riser_title = State()
    choosen_house_riser = State()

    all_used_appartments_numbers = State()
    choosen_appartments_nember = State()

    appartments_type = State()
    planning_type = State()
    living_condition = State()
    heat_type = State()

    appartment_schema = State()
    appartment_addition_images = State()

    saved_media_group_id = State()

    is_all_fields_filled = State()


management_commands_set = ['відміна', 'зберігти квартиру', 'Зробити оголошення з існуючою квартирою',
                           'змінити будинок і номер квартири', 'змінити тип нерухомості', 'змінити тип планування',
                           'змінити життєві умови', 'змінити тип опалення', 'змінити схему квартири']





client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection

router = Router()



router.message.outer_middleware(MediaGroupCounterMiddleware())
router.message.outer_middleware(StopMediaGroupReplicationMiddleware())



@router.message(F.text == 'Додати квартиру')
@router.message(F.text == 'змінити будинок і номер квартири')
async def add_appartment(message: types.Message, state: FSMContext):
    if message.text == 'Додати квартиру':
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
    await state.update_data(chosen_house_title=message.text)
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
    await state.update_data(chosen_building_id=choose_building_id, chosen_building_title=message.text)

    await message.answer(
        text='Оберіть підїзд',
        reply_markup=choose_house_subordinate_obj_kb(current_data['all_current_house_entrances'])
    )
    await state.set_state(AccomodationState.choosen_house_entrances)



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
    await state.update_data(choosen_house_entrances=choose_entrance_id, 
                            choosen_house_entrances_title=message.text)

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
    await state.update_data(choosen_house_floor=choose_floor_id, 
                            choosen_house_floor_title=message.text)

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
    all_current_house_risers = current_data['all_current_house_riser']

    for riser_dict in all_current_house_risers:
        if message.text in riser_dict:
            choose_riser_id = riser_dict[message.text]
            break
    await state.update_data(choosen_house_riser=choose_riser_id, 
                            choosen_house_riser_title=message.text)


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
    
    await message.answer(
        text=f'Використовуються такі номера: {used_numbers_str}',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AccomodationState.choosen_appartments_nember)


# принимаем и сохраняем номер квартиры, запрашиваем тип квартиры
@router.message(AccomodationState.choosen_appartments_nember, ~F.text.in_(management_commands_set))
async def get_appartment_type(message: types.Message, state: FSMContext):
    await state.update_data(choosen_appartments_nember=message.text)

    
    current_data = await state.get_data()
    # editing appartment

    if 'is_all_fields_filled' in current_data:
        accomodation_data = await generate_final_capture(state)
        media_data = await return_presaved_image_data(state)
        await message.answer_media_group(media=media_data)
        await message.answer(
            text=f'Бажаєте збирігти, чи відредагувати оголошення?\n\n{accomodation_data}',
            reply_markup=save_or_change_accomodation_kb()
        )
    else:
    # creating appartment
        await message.answer(
            text='Оберіть тип нерухомості',
            reply_markup=choose_from_accomodation_model_dict_kb(type_status_dict)
        )

        await state.set_state(AccomodationState.appartments_type)



# принимаем и сохраняем тип квартиры, запрашиваем тип планировки
@router.message(AccomodationState.appartments_type, ~F.text.in_(management_commands_set))
async def get_planing_type(message: types.Message, state: FSMContext):
    await state.update_data(appartments_type=message.text)
    current_data = await state.get_data()
    if 'is_all_fields_filled' in current_data:
        media_data = await return_presaved_image_data(state)
        await message.answer_media_group(media=media_data)
        accomodation_data = await generate_final_capture(state)
        await message.answer(
            text=f'Бажаєте збирігти, чи відредагувати оголошення?\n\n{accomodation_data}',
            reply_markup=save_or_change_accomodation_kb()
        )
    else:
        await message.answer(
            text='Оберіть планування',
            reply_markup=choose_from_accomodation_model_dict_kb(planing_dict)
        )

        await state.set_state(AccomodationState.planning_type)


# принимаем и сохраняем тип планировки, запрашиваем жилые условия
@router.message(AccomodationState.planning_type, ~F.text.in_(management_commands_set))
async def get_conditions_type(message: types.Message, state: FSMContext):
    await state.update_data(planning_type=message.text)
    current_data = await state.get_data()
    if 'is_all_fields_filled' in current_data:
        media_data = await return_presaved_image_data(state)
        await message.answer_media_group(media=media_data)
        accomodation_data = await generate_final_capture(state)
        await message.answer(
            text=f'Бажаєте збирігти, чи відредагувати оголошення?\n\n{accomodation_data}',
            reply_markup=save_or_change_accomodation_kb()
        )
    else:
        await message.answer(
            text='Оберіть умови житла',
            reply_markup=choose_from_accomodation_model_dict_kb(living_condition_dict)
        )
        await state.set_state(AccomodationState.living_condition)


# принимаем и сохраняем условия, запрашиваем тип отопления
@router.message(AccomodationState.living_condition, ~F.text.in_(management_commands_set))
async def get_heat_type(message: types.Message, state: FSMContext):
    await state.update_data(living_condition=message.text)
    current_data = await state.get_data()
    if 'is_all_fields_filled' in current_data:
        media_data = await return_presaved_image_data(state)
        await message.answer_media_group(media=media_data)
        accomodation_data = await generate_final_capture(state)
        await message.answer(
            text=f'Бажаєте збирігти, чи відредагувати оголошення?\n\n{accomodation_data}',
            reply_markup=save_or_change_accomodation_kb()
        )
    else:
        await message.answer(
            text='Оберіть тип опалення',
            reply_markup=choose_from_accomodation_model_dict_kb(heat_type_dict)
        )

        await state.set_state(AccomodationState.heat_type)


# принимаем тип отопления, запрашиваем тип схему
@router.message(AccomodationState.heat_type, ~F.text.in_(management_commands_set))
async def get_schema_image(message: types.Message, state: FSMContext):
    await state.update_data(heat_type=message.text)
    current_data = await state.get_data()
    if 'is_all_fields_filled' in current_data:
        media_data = await return_presaved_image_data(state)
        await message.answer_media_group(media=media_data)
        accomodation_data = await generate_final_capture(state)
        await message.answer(
            text=f'Бажаєте збирігти, чи відредагувати оголошення?\n\n{accomodation_data}',
            reply_markup=save_or_change_accomodation_kb()
        )
    else:
        await message.answer(
            text='завантажте схему квартири',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(AccomodationState.appartment_schema)


# принимаем схему и запрашиваем дополнительные фотографии
@router.message(AccomodationState.appartment_schema, ~F.text.in_(management_commands_set), F.photo)
async def get_appartment_schema(message: types.Message, state: FSMContext):
    await state.update_data(appartment_schema=message.photo[-1].file_id)
    current_data = await state.get_data()
    if 'is_all_fields_filled' in current_data:
        media_data = await return_presaved_image_data(state)
        await message.answer_media_group(media=media_data)
        accomodation_data = await generate_final_capture(state)
        await message.answer(
            text=f'Бажаєте збирігти, чи відредагувати оголошення?\n\n{accomodation_data}',
            reply_markup=save_or_change_accomodation_kb()
        )
    else:
        await message.answer(
            text='завантажте додаткові фотографії квартири',
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(AccomodationState.appartment_addition_images)


import pprint
# принимаем дополнительные фото и даем результаты
@router.message(AccomodationState.appartment_addition_images, ~F.text.in_(management_commands_set))
async def get_additional_photo(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    media_grop_couter_client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = media_grop_couter_client.rptutorial
    media_group_counter = db.media_group_counter
    chat_data = media_group_counter.find_one({"media_group_id": message.media_group_id})
    await state.update_data(saved_media_group_id = message.media_group_id)
    image_data_id = chat_data['image_list_id']
    await state.update_data(appartment_addition_images=image_data_id)
    media = []
    main_image_id = state_data['appartment_schema']
    accomodation_data = await generate_final_capture(state)
    media.append(
        types.InputMediaPhoto(media=main_image_id)
    )
    for image_id in image_data_id:
        media.append(types.InputMediaPhoto(media=image_id))
    await message.answer_media_group(media=media)
    await state.update_data(
        is_all_fields_filled='true'
    )
    await message.answer(
        text=f'Бажаєте збирігти, чи відредагувати оголошення?\n\n{accomodation_data}',
        reply_markup=save_or_change_accomodation_kb()
    )


import random
@router.message(F.text == 'зберігти квартиру')
async def save_appartment(message: types.Message, state: FSMContext):
    create_appartment_request = OrdinaryRequestSwipeAPI()
    method = 'post'
    url = f"{base_url_secret}/ads/accomodation/"

    chat_id = message.chat.id
    appartment_dictionary = await state.get_data()

    raw_data = {
        "type_status": type_status_dict[appartment_dictionary["appartments_type"]],
        "number": appartment_dictionary["choosen_appartments_nember"],
        "house": appartment_dictionary["chosen_house_id"],
        "house_building": appartment_dictionary["chosen_building_id"],
        "house_entrance": appartment_dictionary["choosen_house_entrances"],
        "floor": appartment_dictionary["choosen_house_floor"],
        "riser": appartment_dictionary["choosen_house_riser"],

        "area": random.randrange(50, 100),
        "area_kitchen": random.randrange(10, 25),
        "have_balcony": "true",

        "planing": planing_dict[appartment_dictionary['planning_type']],
        "living_condition": living_condition_dict[appartment_dictionary['living_condition']],
        "heat_type": heat_type_dict[appartment_dictionary['heat_type']]
    }

    schema_file = await message.bot.get_file(appartment_dictionary["appartment_schema"])
    result = await message.bot.download_file(schema_file.file_path)
    schema_base_64 = base64.b64encode(result.read())
    raw_data["raw_data"] = schema_base_64.decode()

    image_field = []

    for index, image_id in enumerate(appartment_dictionary["appartment_addition_images"]):

        image_file = await message.bot.get_file(image_id)
        result = await message.bot.download_file(image_file.file_path)
        image_base_64_b = base64.b64encode(result.read())
        image_base_64 = image_base_64_b.decode()

        image_field.append({
            "image": image_base_64,
            "obj_order": index
        })
    raw_data["image_field"] = image_field

    data = json.dumps(raw_data, indent=4)
    request_dict = {'data': data, 'headers': {'Content-Type': 'application/json'}}
    response = create_appartment_request(method, url, chat_id, **request_dict)
    response_dict = json.loads(response.text)

    match response.status_code:
        case 201:
            response_text = "Ви додали квартиру!"
            await message.answer(
                text = response_text,
                reply_markup=make_main_keyboard()
            )
        case 400:
            # try:
            response_text=""
            for field, message_error in response_dict.items():
                if len(response_dict[field]) > 1:
                    for error_text in response_dict[field]: response_text += f'{field}: {error_text}'
                else:
                    response_text += f'{field}: {response_dict[field][0]}'
            await message.answer(
                text = response_text
            )

        case _:
            response_text = response.text
            await message.answer(
                text = response_text
            )





    # editing fumctions

@router.message(F.text == 'змінити тип нерухомості')
async def edit_accomodation_type(message: types.Message, state: FSMContext):
    await message.answer(
        text='Оберіть тип нерухомості',
        reply_markup=choose_from_accomodation_model_dict_kb(type_status_dict)
    )
    await state.set_state(AccomodationState.appartments_type)


@router.message(F.text == 'змінити тип планування')
async def edit_planning_type(message: types.Message, state: FSMContext):
    await message.answer(
            text='Оберіть планування',
            reply_markup=choose_from_accomodation_model_dict_kb(planing_dict)
        )

    await state.set_state(AccomodationState.planning_type)



@router.message(F.text == 'змінити життєві умови')
async def edit_living_conditions_type(message: types.Message, state: FSMContext):
    await message.answer(
            text='Оберіть умови житла',
            reply_markup=choose_from_accomodation_model_dict_kb(living_condition_dict)
        )
    await state.set_state(AccomodationState.living_condition)


@router.message(F.text == 'змінити тип опалення')
async def edit_heating_type(message: types.Message, state: FSMContext):
    await message.answer(
            text='Оберіть тип опалення',
            reply_markup=choose_from_accomodation_model_dict_kb(heat_type_dict)
        )
    await state.set_state(AccomodationState.heat_type)


@router.message(F.text == 'змінити схему квартири')
async def edit_accomofation_schema_type(message: types.Message, state: FSMContext):
    await message.answer(
        text='завантажте схему квартири',
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AccomodationState.appartment_schema)


@router.message(F.text == 'змінити фотографії')
async def edit_photo_type(message: types.Message, state: FSMContext):
    await message.answer(
            text='завантажте додаткові фотографії квартири',
            reply_markup=types.ReplyKeyboardRemove()
        )
    await state.set_state(AccomodationState.appartment_addition_images)


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


async def generate_final_capture(state: FSMContext):
    state_data = await state.get_data()
   
    choosen_house = state_data["chosen_house_title"]
    final_capture = f"Будинок: {choosen_house}"
    choosent_house_building = state_data["chosen_building_title"]
    final_capture += f"\nКорпус: {choosent_house_building}"
    choosen_entrance = state_data["choosen_house_entrances_title"]
    final_capture += f"\nПідїзд: {choosen_entrance}"
    choosen_floor = state_data["choosen_house_floor_title"]
    final_capture += f"\nПоверх: {choosen_floor}"
    choosen_riser = state_data["choosen_house_riser_title"]
    final_capture += f"\nСтояк: {choosen_riser}"
    choosen_appartment_number = state_data["choosen_appartments_nember"]
    final_capture += f"\nКвартира №{choosen_appartment_number}"
    appartments_type = state_data["appartments_type"]
    final_capture += f"\nТип нерухомості: {appartments_type}"
    conditions_type = state_data["living_condition"]
    final_capture += f"\nСтан нерухомості: {conditions_type}"
    planning_type = state_data["planning_type"]
    final_capture += f"\nТип планування: {planning_type}"
    heat_type = state_data["heat_type"]
    final_capture += f"\nТип опалення: {heat_type}"

    return final_capture




async def return_presaved_image_data(state: FSMContext):
    state_data = await state.get_data()
    media_grop_couter_client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = media_grop_couter_client.rptutorial
    media_group_counter = db.media_group_counter

    chat_data = media_group_counter.find_one({"media_group_id": state_data['saved_media_group_id']})
    image_data_id = chat_data['image_list_id']
    await state.update_data(appartment_addition_images=image_data_id)
    media = []
    main_image_id = state_data['appartment_schema']
    # accomodation_data = await generate_final_capture(state)
    media.append(
        types.InputMediaPhoto(media=main_image_id)
    )
    for image_id in image_data_id:
        media.append(types.InputMediaPhoto(media=image_id))

    return media

    

        # file = await message.bot.get_file(image_id)
        # result = await message.bot.download_file(file.file_path)
        # photo64 = base64.b64encode(result.read())
