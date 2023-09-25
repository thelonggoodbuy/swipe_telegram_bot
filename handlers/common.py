from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, KeyboardBuilder



from keyboards.simple_row import make_row_keyboard



router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):


    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='Увійти в бот',
        callback_data="sign_in"
    ))
    builder.add(types.InlineKeyboardButton(
        text='Зареєструватись',
        callback_data="sign_up"
    ))
    builder.add(types.InlineKeyboardButton(
        text='Список оголошень',
        callback_data="list_of_ads"
    ))

    await message.answer(
        text="Привіт! Залогінся або зареєструйся =)",
        reply_markup=builder.as_markup()
    )




from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from filters.correct_email_filter import ChatTypeFilter






# --------------work area-----------------------

class LoginState(StatesGroup):
    users_email = State()
    users_password = State()


# request and wait email state
@router.callback_query(F.data == "sign_in")
async def callback_cmd_sign_in(callback: types.CallbackQuery,\
                                state: FSMContext):
    await callback.message.answer(
        text="Введіть емейл користувача",        
    )
    await state.set_state(LoginState.users_email)



# save emails state if email is valid
@router.message(LoginState.users_email, ChatTypeFilter())
async def save_email(message: Message, state: FSMContext) -> None:
    await state.update_data(users_email=message.text)
    await message.answer(
        text="Введіть пароль"
    )
    await state.set_state(LoginState.users_password)


# email is not valid. We are not saving it.
@router.message(LoginState.users_email)
async def handling_uncorrect_email(message: Message, state: FSMContext) -> None:
        await message.answer(
        text="Помилка в емейлі. Такой адресси електронної пошти не може існувати. Введіть існуючу."
    )
 

# save passwor state if password string is valid
@router.message(LoginState.users_password, F.text)
async def process_password(message: Message, state: FSMContext) -> None:
    await state.update_data(users_password=message.text)
    auth_data = await state.get_data()
    await message.answer(
        text=f"Вітаю! Email {auth_data['users_email']} та пароль {auth_data['users_password']}"
    )
    await state.clear()


# password string is not valid and empty.
@router.message(LoginState.users_password)
async def handling_empty_password(message: Message, state: FSMContext) -> None:
        await message.answer(
        text="Заповнення поля пароль є обов'язковим."
    )

# ---------------END----WORK------AREA------------------