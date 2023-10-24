import httpx
import json

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, KeyboardBuilder

from pymongo import MongoClient

from filters.correct_email_filter import EmailValidationFilter
from keyboards.simple_row import make_row_keyboard
from keyboards.main_keyboard import make_main_keyboard
from keyboards.invite_keyboard import make_invite_keyboard
from services.request_to_swipeapi import OrdinaryRequestSwipeAPI, LoginRequestSwipeAPI

from filters.state_still_in_validation_filter import IsNotDefaultStateFilter
from aiogram.filters.state import StateFilter
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _


from services.get_secret_values import return_secret_value



router = Router()

mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')



client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection



# --------------work area-----------------------

class LoginState(StatesGroup):
    users_email = State()
    users_password = State()
    is_not_default_state = State()


# request and wait email state
@router.message(F.text == __("Увійти в бот"))
async def sign_in(message: types.Message, state: FSMContext):

    await message.reply(_("Введіть емейл користувача"), reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(is_not_default_state='true')
    await state.set_state(LoginState.users_email)


# save emails state if email is valid
@router.message(LoginState.users_email, EmailValidationFilter())
async def save_email(message: Message, state: FSMContext) -> None:
    await state.update_data(users_email=message.text)
    await message.answer(
        text=_("Введіть пароль")
    )
    await state.set_state(LoginState.users_password)


@router.message(LoginState.users_email, ~StateFilter(default_state))
async def handling_uncorrect_email(message: Message, state: FSMContext) -> None:
        await message.answer(
        text=_("Помилка в емейлі. Такой адресси електронної пошти не може існувати. Введіть існуючу.")
    )
 

# save passwor state if password string is valid
@router.message(LoginState.users_password, F.text)
async def process_password(message: Message, state: FSMContext) -> None:
    await state.update_data(users_password=message.text)
    auth_data = await state.get_data()

    login_request = LoginRequestSwipeAPI()
    method = 'post'
    url = f"{base_url_secret}/users/auth/login_simple_user/"
    chat_id = message.chat.id
    data = {"email": auth_data['users_email'], "password": auth_data['users_password']}
    login_dict = {'data': data}
    response = login_request(method, url, chat_id, **login_dict)

    print('-------------------------')
    print(response)
    print(response.status_code)
    print(response.text)
    print('-------------------------')

    response_dict = json.loads(response.text)

    match response.status_code:
        case 200:
            auth_object = {"chat_id": message.chat.id,
                            "email": response_dict["email"],
                            "user_id": response_dict["id"],
                            "access_token": response_dict["tokens"]["access"],
                            "refresh_token": response_dict["tokens"]["refresh"]}
            
            bot_aut_collection.update_one({"chat_id": message.chat.id},\
                                        {"$set": auth_object}, upsert=True)
        
            response_text = _("Ви увійшли в бот як {email}").format(email=response_dict['email'])
            await message.answer(
                text = response_text,
                reply_markup=make_main_keyboard()
            )
        case 400:
            await message.answer(
                text = _('Помилка в email або в пароли'),
                reply_markup=make_invite_keyboard()
            )      

    await state.clear()


# password string is not valid and empty.
@router.message(LoginState.users_password)
async def handling_empty_password(message: Message, state: FSMContext) -> None:
        await message.answer(
        text=_("Заповнення поля пароль є обов'язковим.")
    )
