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

from filters.correct_email_filter import ChatTypeFilter
from keyboards.simple_row import make_row_keyboard


from filters.state_still_in_validation_filter import IsNotDefaultStateFilter
from aiogram.filters.state import StateFilter

router = Router()





client = MongoClient("mongodb://localhost:27017/")
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection



# --------------work area-----------------------

class LoginState(StatesGroup):
    users_email = State()
    users_password = State()
    is_not_default_state = State()


# request and wait email state
@router.message(F.text == "Увійти в бот")
async def sign_in(message: types.Message, state: FSMContext):

    await message.reply("Введіть емейл користувача", reply_markup=types.ReplyKeyboardRemove())
    await state.update_data(is_not_default_state='true')
    await state.set_state(LoginState.users_email)


# save emails state if email is valid
@router.message(LoginState.users_email, ChatTypeFilter())
async def save_email(message: Message, state: FSMContext) -> None:
    await state.update_data(users_email=message.text)
    await message.answer(
        text="Введіть пароль"
    )
    await state.set_state(LoginState.users_password)




@router.message(LoginState.users_email, ~StateFilter(default_state))
async def handling_uncorrect_email(message: Message, state: FSMContext) -> None:
        
        await message.answer(
        text="Помилка в емейлі. Такой адресси електронної пошти не може існувати. Введіть існуючу."
    )
 

# save passwor state if password string is valid
@router.message(LoginState.users_password, F.text)
async def process_password(message: Message, state: FSMContext) -> None:
    await state.update_data(users_password=message.text)
    auth_data = await state.get_data()

    with httpx.Client() as client:
        url = "http://127.0.0.1:8000/users/auth/login_simple_user/"

        data = {"email": auth_data['users_email'], "password": auth_data['users_password']}

        response = client.post(url, data=data, timeout=10.0)

        response_dict = json.loads(response.text)

        match response.status_code:
            case 200:
                print('Your status 200')
                auth_object = {"chat_id": message.chat.id,
                               "email": response_dict["email"],
                               "access_token": response_dict["tokens"]["access"],
                               "refresh_token": response_dict["tokens"]["refresh"]}
                
                bot_aut_collection.update_one({"chat_id": message.chat.id},\
                                               {"$set": auth_object}, upsert=True)
                
                response_text = f"Ви увійшли в бот як {response_dict['email']}"
            case 400:
                response_text = response_dict['non_field_errors'][0]

        await message.answer(
        text = response_text
    )

    await state.clear()


# password string is not valid and empty.
@router.message(LoginState.users_password)
async def handling_empty_password(message: Message, state: FSMContext) -> None:
        await message.answer(
        text="Заповнення поля пароль є обов'язковим."
    )

# ---------------END----WORK------AREA------------------

