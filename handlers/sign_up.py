from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup, default_state

from keyboards.invite_keyboard import make_invite_keyboard
from keyboards.sign_up_update_keyboard import edit_registration_data_keyboard
from keyboards.cancel_keyboard import cancel_keyboard
from middlewares.sign_up_middlewares import OnlySignUpMiddleware

from aiogram.filters.state import StateFilter
from filters.correct_email_filter import EmailValidationFilter
from services.get_secret_values import return_secret_value


from services.request_to_swipeapi import OrdinaryRequestSwipeAPI, RegistrationRequestSwipeAPI


import httpx
import json
from pymongo import MongoClient

from aiogram import flags


mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')


router = Router()
router.message.middleware(OnlySignUpMiddleware())

management_commands_set = ['Відміна', 'Змінити email',\
                        'Змінити пароль', 'Підтвердити',\
                        'Назад']


class SignUpState(StatesGroup):
    users_email = State()
    users_password = State()
    is_all_fields_filled = State()
    previouse_states = State()


# entry point for FSM
@router.message(F.text == "Зареєструватись", flags={'entry_sing_up_flag': 'True'})
async def sign_up_handler(message: types.Message, state: FSMContext):

    await message.reply("Введіть свій email.", 
                        reply_markup=cancel_keyboard())
    await state.set_state(SignUpState.users_email)


# SAVE EMAIL state if email is valid or CHANGE EMAIL
@router.message(SignUpState.users_email, EmailValidationFilter(), ~F.text.in_(management_commands_set))
async def save_email(message: types.Message, state: FSMContext) -> None:

    registration_data = await state.get_data()
    # first saving of email state 
    if 'is_all_fields_filled' not in registration_data:
        await state.update_data(users_email=message.text, previouse_states=['users_email', ])
        await message.answer(
        text="Введіть пароль",
        reply_markup=cancel_keyboard()
    )
        await state.set_state(SignUpState.users_password)
    # updating email state
    elif 'is_all_fields_filled' in registration_data:
        await state.update_data(users_email=message.text, previouse_states=['users_email', ])
        await message.answer(text="email змінено")
        await message.answer(
            text=f"Ви бажаєте зареєструватись як {registration_data['users_email']} з паролем {registration_data['users_password']} ",
            reply_markup=edit_registration_data_keyboard()
            )



@router.message(SignUpState.users_email, ~F.text.in_(management_commands_set))
async def handling_uncorrect_email(message: types.Message, state: FSMContext) -> None:
        await message.answer(
        text="Помилка в емейлі. Такой адресси електронної пошти не може існувати. Введіть існуючу.",
        reply_markup=cancel_keyboard()
    )


@router.message(SignUpState.users_password, ~F.text.in_(management_commands_set))
async def process_password(message: types.Message, state: FSMContext) -> None:
    registration_data = await state.get_data()    
    previouse_states=registration_data['previouse_states']
    new_previouse_states = previouse_states.append('users_password')
    await state.update_data(users_password=message.text, previouse_states=new_previouse_states)
    # UPDATING password logic
    if 'is_all_fields_filled' in registration_data:
        await message.answer(text="Ви змінили пароль")
    else:
        await state.update_data(is_all_fields_filled='true', previouse_states=previouse_states)
    registration_data = await state.get_data()
    await message.answer(
        text=f"Ви бажаєте зареєструватись як {registration_data['users_email']} з паролем {registration_data['users_password']} ",
        reply_markup=edit_registration_data_keyboard()
    )


# return to privious stage
@router.message(F.text == "Назад")
async def return_to_previous_step(message: types.Message, state: FSMContext):

    state_data = await state.get_data()
    previous_state = state_data['previouse_states'].pop()

    if previous_state == 'users_email':
        await message.answer("Введіть свій email.")
        await state.set_state(SignUpState.users_email)

    if previous_state == 'users_password':
        await message.answer("Введіть пароль.")
        await state.set_state(SignUpState.users_password)
   
# Update data commands
@router.message(F.text == "Змінити email")
async def change_email(message: types.Message, state: FSMContext):
    await message.answer("Введіть новий email")
    await state.set_state(SignUpState.users_email)   

@router.message(F.text == "Змінити пароль")
async def change_password(message: types.Message, state: FSMContext):
    await message.answer("Введіть новий пароль")
    await state.set_state(SignUpState.users_password)   

@router.message(F.text == "Відміна")
async def sign_up_cancel(message: types.Message, state: FSMContext):

    await state.clear()
    await message.answer(
        text="Реєстрацію відмінено. Залогінся або зареєструйся =)",
        reply_markup=make_invite_keyboard()
    )


client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection


@router.message(F.text == 'Підтвердити')
async def sign_up_confirmation(message: types.Message, state: FSMContext):
    auth_data = await state.get_data()

    # ----------------NEW----CODE--------------------------------------------
    # with httpx.Client() as client:
    #     url = "http://127.0.0.1:8000/users/auth/register_builder_user/"
    #     data = {"email": auth_data['users_email'], "password": auth_data['users_password']}
    #     response = client.post(url, data=data, timeout=10.0)
    #     response_dict = json.loads(response.text)

    registration_request = RegistrationRequestSwipeAPI()
    method = 'post'
    url = f"{base_url_secret}/users/auth/register_builder_user/"
    chat_id = message.chat.id
    data = {"email": auth_data['users_email'], "password": auth_data['users_password']}
    request_dict = {'data': data}
    response = registration_request(method, url, chat_id, **request_dict)
    response_dict = json.loads(response.text)

    match response.status_code:
        case 200:
            response_text = f"Ви зареєстровані в системі як {response_dict['email']}"
        case 400:
            response_text = response_dict['non_field_errors'][0]

    await message.answer(
        text = response_text
    )

    # -----------------END----NEW------CODE----------------------------------

    await state.clear()
    await message.answer(
        text="Ви успішно зареєструвалися",
        reply_markup=make_invite_keyboard()
    )