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

from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

from services.request_to_swipeapi import OrdinaryRequestSwipeAPI, RegistrationRequestSwipeAPI


import httpx
import json
from pymongo import MongoClient

from aiogram import flags


mongo_url_secret = return_secret_value('MONGO_URL')
base_url_secret = return_secret_value('BASE_URL')


router = Router()
router.message.middleware(OnlySignUpMiddleware())

management_commands_set = [__('Відміна'), __('Змінити email'),\
                        __('Змінити пароль'), __('Підтвердити'),\
                        __('Назад')]


class SignUpState(StatesGroup):
    users_email = State()
    users_password = State()
    is_all_fields_filled = State()
    previouse_states = State()


# entry point for FSM
@router.message(F.text == __("Зареєструватись"), flags={'entry_sing_up_flag': 'True'})
async def sign_up_handler(message: types.Message, state: FSMContext):

    await message.reply(_("Введіть свій email."), 
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
        text=_("Введіть пароль"),
        reply_markup=cancel_keyboard()
    )
        await state.set_state(SignUpState.users_password)
    # updating email state
    elif 'is_all_fields_filled' in registration_data:
        await state.update_data(users_email=message.text, previouse_states=['users_email', ])
        await message.answer(text=_("email змінено"))
        await message.answer(
            text="Ви бажаєте зареєструватись як {users_email} з паролем {users_password} ".format(users_email=registration_data['users_email'], users_password=registration_data['users_password']),
            reply_markup=edit_registration_data_keyboard()
            )



@router.message(SignUpState.users_email, ~F.text.in_(management_commands_set))
async def handling_uncorrect_email(message: types.Message, state: FSMContext) -> None:
        await message.answer(
        text=_("Помилка в емейлі. Такой адресси електронної пошти не може існувати. Введіть існуючу."),
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
        await message.answer(text=_("Ви змінили пароль"))
    else:
        await state.update_data(is_all_fields_filled='true', previouse_states=previouse_states)
    registration_data = await state.get_data()
    await message.answer(
        text="Ви бажаєте зареєструватись як {users_email} з паролем {users_password} ".format(users_email=registration_data['users_email'], users_password=registration_data['users_password']),
        reply_markup=edit_registration_data_keyboard()
    )


# return to privious stage
@router.message(F.text == __("Назад"))
async def return_to_previous_step(message: types.Message, state: FSMContext):

    state_data = await state.get_data()
    previous_state = state_data['previouse_states'].pop()

    if previous_state == 'users_email':
        await message.answer(_("Введіть свій email."))
        await state.set_state(SignUpState.users_email)

    if previous_state == 'users_password':
        await message.answer(_("Введіть пароль."))
        await state.set_state(SignUpState.users_password)
   
# Update data commands
@router.message(F.text == __("Змінити email"))
async def change_email(message: types.Message, state: FSMContext):
    await message.answer(_("Введіть новий email"))
    await state.set_state(SignUpState.users_email)   

@router.message(F.text == __("Змінити пароль"))
async def change_password(message: types.Message, state: FSMContext):
    await message.answer(__("Введіть новий пароль"))
    await state.set_state(SignUpState.users_password)   

@router.message(F.text == __("Відміна"))
async def sign_up_cancel(message: types.Message, state: FSMContext):

    await state.clear()
    await message.answer(
        text=_("Реєстрацію відмінено. Залогінся або зареєструйся =)"),
        reply_markup=make_invite_keyboard()
    )


client = MongoClient(mongo_url_secret)
db = client.rptutorial
bot_aut_collection = db.bot_aut_collection


@router.message(F.text == __('Підтвердити'))
async def sign_up_confirmation(message: types.Message, state: FSMContext):
    auth_data = await state.get_data()
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
            response_text = "Ви зареєстровані в системі як {email}".format(email=response_dict['email'])
        case 400:
            response_text = response_dict['non_field_errors'][0]

    await message.answer(
        text = response_text
    )

    # -----------------END----NEW------CODE----------------------------------

    await state.clear()
    await message.answer(
        text=_("Ви успішно зареєструвалися"),
        reply_markup=make_invite_keyboard()
    )