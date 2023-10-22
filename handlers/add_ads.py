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

from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _



class AdsState(StatesGroup):
    free_accomodation_list = State()
    accomodation_id = State()
    appartment_area = State()
    cost = State()
    agent_commission = State()
    version_of_calculation = State()
    description = State()
    is_all_fields_filled = State()

management_commands_set = [__('відміна'), __('зберігти оголошення'), __('підтвердити зміну'),
                           __('змінити вартість'), __('зміники коміссію агента'), __('змінити тип оплати'),
                           __('змінити опис')]

client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection

router = Router()

@router.message(F.text == __('Створити оголошення'))
async def create_ad(message: types.Message, state: FSMContext):
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
        text=_("Оберіть квартиру для оголошення"),
        reply_markup=create_ads_keyboard(accomodation_list_of_dict)
    )


@router.message(F.text.startswith('№'), ~F.text.in_(management_commands_set))
async def create_ads(message: types.Message, state: FSMContext):
    accomodation_list_of_dict = await state.get_data()
    accomodation_data = message.text
    accomodation_number = accomodation_data.split(',')[0][1:]
    accomodation_address = message.text.lstrip(f'№{accomodation_number}, ')

    for accomodation in accomodation_list_of_dict['free_accomodation_list']: 
        if accomodation['number'] == int(accomodation_number) and accomodation['house_address'] == accomodation_address:
            choosen_appartment_id = accomodation['id']
            choosen_appartment_area = accomodation['area']

    await state.update_data(accomodation_id=choosen_appartment_id,
                            appartment_area=choosen_appartment_area)    
    await message.answer(
        text=_("Введіть вартість квартири в грн."),
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AdsState.cost)
    


@router.message(AdsState.cost, ~F.text.in_(management_commands_set))
async def get_cost(message: types.Message, state: FSMContext) -> None:
    await state.update_data(cost=message.text)
    accomodation_list_of_dict = await state.get_data()
    # first gatting price
    if 'is_all_fields_filled' not in accomodation_list_of_dict:
        await message.answer(
            text=_("Введіть коміссію агента в процентах")
        )
        await state.set_state(AdsState.agent_commission)
    # updating price gatting price
    elif 'is_all_fields_filled' in accomodation_list_of_dict:
        ads_data = ''
        ads_data +=__("Ціна: {cost}".format(cost=accomodation_list_of_dict['cost']))
        ads_data +=__("\nКомміссія: {agent_commission}".format(agent_commission=accomodation_list_of_dict['agent_commission']))
        ads_data +=__("\nТип оплати: {version_of_calculation}".format(version_of_calculation=accomodation_list_of_dict['version_of_calculation']))
        ads_data +=__("\nОпис: {description}".format(description=accomodation_list_of_dict['description']))
        await message.answer(
            text=ads_data
        )
        await message.answer(
            text=_("Зберігти оголошення, чи змінити данні?"),
            reply_markup = save_or_change_ads_kayboard()
        )



@router.message(AdsState.agent_commission, ~F.text.in_(management_commands_set))
async def get_version_of_calculation(message: types.Message, state: FSMContext) -> None:
    await state.update_data(agent_commission=message.text)
    accomodation_list_of_dict = await state.get_data()
    if 'is_all_fields_filled' not in accomodation_list_of_dict:
        await message.answer(
            text=_("Оберіть тип оплати"),
            reply_markup=choose_version_of_calculation()
        )
        await state.set_state(AdsState.version_of_calculation)
    elif 'is_all_fields_filled' in accomodation_list_of_dict:
        ads_data = ''
        ads_data +=__("Ціна: {cost}".format(cost=accomodation_list_of_dict['cost']))
        ads_data +=__("\nКомміссія: {agent_commission}".format(agent_commission=accomodation_list_of_dict['agent_commission']))
        ads_data +=__("\nТип оплати: {version_of_calculation}".format(version_of_calculation=accomodation_list_of_dict['version_of_calculation']))
        ads_data +=__("\nОпис: {description}".format(description=accomodation_list_of_dict['description']))
        await message.answer(
            text=ads_data
        )
        await message.answer(
            text=_("Зберігти оголошення, чи змінити данні?"),
            reply_markup = save_or_change_ads_kayboard()
        )



@router.message(AdsState.version_of_calculation, ~F.text.in_(management_commands_set))
async def get_description(message: types.Message, state: FSMContext) -> None:

    if message.text == _('кредит'):
        calculation = 'credit'
    elif message.text == _('тільки готівка'):
        calculation = 'only_cash'
    elif message.text == _('іпотека'):
        calculation = 'mortgage'

    # match message.text:
    #     case _('кредит'):
    #         calculation = 'credit'
    #     case _('тільки готівка'):
    #         calculation = 'only_cash'
    #     case _('іпотека'):
    #         calculation = 'mortgage'

    await state.update_data(version_of_calculation=calculation)
    accomodation_list_of_dict = await state.get_data()
    if 'is_all_fields_filled' not in accomodation_list_of_dict:
        await message.answer(
            text=_("Введіть опис для оголошення"), 
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(AdsState.description)

    elif 'is_all_fields_filled' in accomodation_list_of_dict:
        ads_data = ''
        ads_data +=__("Ціна: {cost}".format(cost=accomodation_list_of_dict['cost']))
        ads_data +=__("\nКомміссія: {agent_commission}".format(agent_commission=accomodation_list_of_dict['agent_commission']))
        ads_data +=__("\nТип оплати: {version_of_calculation}".format(version_of_calculation=accomodation_list_of_dict['version_of_calculation']))
        ads_data +=__("\nОпис: {description}".format(description=accomodation_list_of_dict['description']))
        await message.answer(
            text=ads_data
        )
        await message.answer(
            text=_("Зберігти оголошення, чи змінити данні?"),
            reply_markup = save_or_change_ads_kayboard()
        )

    
@router.message(AdsState.description, ~F.text.in_(management_commands_set))
async def save_or_update_menu(message: types.Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    ads_data = ""
    ads_dictionary = await state.get_data()

    cost = ads_dictionary['cost']
    agent_commission = ads_dictionary['agent_commission']
    version_of_calculation = ads_dictionary['version_of_calculation']
    description = ads_dictionary['description']

    await  state.update_data(is_all_fields_filled='true')

    ads_data +=__("Ціна: {cost}".format(cost=cost))
    ads_data +=__("\nКомміссія: {agent_commission}".format(agent_commission=agent_commission))
    ads_data +=__("\nТип оплати: {version_of_calculation}".format(version_of_calculation=version_of_calculation))
    ads_data +=__("\nОпис: {description}".format(description=description))


    await message.answer(
        text=ads_data
    )
    await message.answer(
        text=_("Зберігти оголошення, чи змінити данні?"),
        reply_markup = save_or_change_ads_kayboard()
    )




@router.message(F.text == __("зберігти оголошення"))
async def save_ads(message: types.Message, state: FSMContext) -> None:

     
    create_ads_request = OrdinaryRequestSwipeAPI()
    method = 'post'
    url = f"{base_url_secret}/ads/ads/"
    chat_id = message.chat.id
    ads_dictionary = await state.get_data()

    cost = ads_dictionary['cost']
    area = ads_dictionary['appartment_area']
    agent_commission = ads_dictionary['agent_commission']
    version_of_calculation = ads_dictionary['version_of_calculation']
    description = ads_dictionary['description']
    accomodation_id = ads_dictionary["accomodation_id"]

    raw_data = {
            "accomodation": accomodation_id, 
            "agent_commission": agent_commission,
            "cost": cost,
            "cost_per_metter": round(float(cost)/float(area), 2),
            "version_of_calculation": version_of_calculation,
            "description": description
            }
    
    data = json.dumps(raw_data, indent=4)

    request_dict = {'data': data, 'headers': {'Content-Type': 'application/json'}}
    
    response = create_ads_request(method, url, chat_id, **request_dict)

    response_dict = json.loads(response.text)

    match response.status_code:
        case 201:
            response_text = _("Ви додали оголошення!")
            await message.answer(
                text = response_text,
                reply_markup=make_main_keyboard()
            )
        case 400:
            # try:
            response_text=""
            # response_text = response_dict.values()['non_field_errors'][0]
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


@router.message(F.text == __("відміна"))
async def save_ads(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=_("Головне меню"),
        reply_markup = make_main_keyboard()
    )


@router.message(F.text == __("змінити вартість"))
async def change_email(message: types.Message, state: FSMContext):
    await message.answer(_("Введіть нову вартість"))
    await state.set_state(AdsState.cost) 


@router.message(F.text == __("зміники коміссію агента"))
async def change_email(message: types.Message, state: FSMContext):
    await message.answer(_("Введіть нову коміссію"),
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AdsState.agent_commission) 


@router.message(F.text == __("змінити тип оплати"))
async def change_email(message: types.Message, state: FSMContext):
    await message.answer(_("оберіть новий тип оплати"),
                         reply_markup=choose_version_of_calculation())
    await state.set_state(AdsState.version_of_calculation,
                          ) 


@router.message(F.text == __("змінити опис"))
async def change_email(message: types.Message, state: FSMContext):
    await message.answer(_("введіть новий опис"))
    await state.set_state(AdsState.description) 

