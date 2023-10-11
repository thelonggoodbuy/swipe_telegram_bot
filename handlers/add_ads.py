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



mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')


class AdsState(StatesGroup):
    free_accomodation_list = State()
    accomodation_id = State()
    cost = State()
    agent_commission = State()
    version_of_calculation = State()
    description = State()


client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection

router = Router()

@router.message(F.text == 'Створити оголошення')
async def create_ad(message: types.Message, state: FSMContext):

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


@router.message(F.text.startswith('№'))
async def create_ads(message: types.Message, state: FSMContext):
    accomodation_list_of_dict = await state.get_data()

    accomodation_data = message.text
    accomodation_number = accomodation_data.split(',')[0][1:]
    accomodation_address = message.text.lstrip(f'№{accomodation_number}, ')

    for accomodation in accomodation_list_of_dict['free_accomodation_list']: 
        if accomodation['number'] == int(accomodation_number) and accomodation['house_address'] == accomodation_address:
            choosen_appartment_id = accomodation['id']

    await state.update_data(accomodation_id=choosen_appartment_id)    
    await message.answer(
        text="Введіть вартість квартири в грн."
    )
    await state.set_state(AdsState.cost)
    


@router.message(AdsState.cost)
async def get_cost(message: types.Message, state: FSMContext) -> None:
    await state.update_data(cost=message.text)
    await message.answer(
        text="Введіть коміссію агента в процентах"
    )
    await state.set_state(AdsState.agent_commission)



@router.message(AdsState.agent_commission)
async def get_version_of_calculation(message: types.Message, state: FSMContext) -> None:
    await state.update_data(agent_commission=message.text)
    await message.answer(
        text="Оберіть тип оплати",
        reply_markup=choose_version_of_calculation()
    )
    await state.set_state(AdsState.version_of_calculation)



@router.message(AdsState.version_of_calculation)
async def get_description(message: types.Message, state: FSMContext) -> None:

    match message.text:
        case 'кредит':
            calculation = 'credit'
        case 'тільки готівка':
            calculation = 'only_cash'
        case 'іпотека':
            calculation = 'mortgage'

    await state.update_data(version_of_calculation=calculation)
    await message.answer(
        text="Введіть опис для оголошення"
    )
    await state.set_state(AdsState.description)


@router.message(AdsState.description)
async def save_or_update_menu(message: types.Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    ads_data = ""
    ads_dictionary = await state.get_data()

    print('-------------------STATE---DATA_---------------')
    print(ads_dictionary)
    print(type(ads_dictionary))
    print('----------------------------------------------')
    cost = ads_dictionary['cost']
    agent_commission = ads_dictionary['agent_commission']
    version_of_calculation = ads_dictionary['version_of_calculation']
    description = ads_dictionary['description']

    ads_data +="Ціна: {cost}",format(cost=cost)
    ads_data +="\nКомміссія: {agent_commission}".format(agent_commission=agent_commission)
    ads_data +="\nТип оплати: {version_of_calculation}".format(version_of_calculation=version_of_calculation)
    ads_data +="\nОпис: {description}".format(description=description)


    await message.answer(
        text=ads_data
    )
    await message.answer(
        text="Зберігти оголошення, чи змінити данні?",
        reply_markup = save_or_change_ads_kayboard()
    )