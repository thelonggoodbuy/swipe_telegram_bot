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

from aiogram import flags



router = Router()
router.message.middleware(OnlySignUpMiddleware())

# management_commands = ['Відміна', 'Email відрадагований', 'Пароль відрадагований']

class SignUpState(StatesGroup):
    users_email = State()
    users_password = State()
    is_not_default_state = State()


@router.message(F.text == "Зареєструватись", flags={'entry_sing_up_flag': 'True'})
async def sign_up_handler(message: types.Message, state: FSMContext):

    await message.reply("Введіть свій email.", 
                        reply_markup=cancel_keyboard())
    await state.update_data(is_not_default_state='true')
    await state.set_state(SignUpState.users_email)



# create data for sign up
# save emails state if email is valid

@router.message(SignUpState.users_email, EmailValidationFilter(), F.text != 'Відміна')
async def save_email(message: types.Message, state: FSMContext) -> None:
    await state.update_data(users_email=message.text)
    await message.answer(
        text="Введіть пароль",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(SignUpState.users_password)


@router.message(SignUpState.users_email, F.text != 'Відміна')
async def handling_uncorrect_email(message: types.Message, state: FSMContext) -> None:
        await message.answer(
        text="Помилка в емейлі. Такой адресси електронної пошти не може існувати. Введіть існуючу.",
        reply_markup=cancel_keyboard()
    )


@router.message(SignUpState.users_password, F.text != 'Відміна')
async def process_password(message: types.Message, state: FSMContext) -> None:
    await state.update_data(users_password=message.text)
    registration_data = await state.get_data()
    await message.answer(
         text=f"Ви бажаєте зареєструватись як \
         {registration_data['users_email']} \
                            з паролем \
                            {registration_data['users_password']} ",
        reply_markup=edit_registration_data_keyboard()
    )




# # --------------------------WORK----AREA-------------------------------------------------
# update data for sigm


# --------------------------END----AREA---------------------------------------------------

@router.message(F.text == "Відміна")
async def sign_up_cancel(message: types.Message, state: FSMContext):

    await state.clear()
    await message.answer(
        text="Реєстрацію відмінено. Залогінся або зареєструйся =)",
        reply_markup=make_invite_keyboard()
    )


