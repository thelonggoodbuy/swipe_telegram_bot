from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.simple_row import make_row_keyboard


router = Router()





# @router.message(Command(commands=["start"]))
# async def cmd_start(message: Message, state: FSMContext):
#     await state.clear()
#     await message.answer(
#         text="Выберите блюдо, что хотите заказа: "
#         "блюдо (/food) или напитки (/drinks).",
#         reply_markup=ReplyKeyboardRemove()
#     )


# @router.message(F.data == "start")
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


# --------------work area-----------------------

class LoginState(StatesGroup):
    users_email = State()
    users_password = State()



@router.callback_query(F.data == "sign_in")
async def callback_cmd_sign_in(callback: types.CallbackQuery, state: FSMContext):

    await callback.message.answer(
        text="Введіть емейл користувача",
        # reply_markup=make_row_keyboard(available_food_names)
    )
    await state.set_state(LoginState.users_email)
    print('------states-------')
    print(LoginState.users_email.state)
    print(LoginState.users_password.state)
    print('------states-------')





    # your_variable = callback.message.text

    # if your_variable:
    #   print("Cool!")
        # await callback.message.answer(
        #     text="Спасибі, але функція авторизації ще не розроблена"
        # )
        # await callback.message.answer(
        #     text=f"Спасибі, {your_variable}!"
        # )


# --------END---work area-----------------------






@router.callback_query(F.data == "sign_up")
async def callback_cmd_sign_up(callback: types.CallbackQuery):
    await callback.message.answer(
        text="Спасибі, але функція реєстрації ще не розроблена"
    )



@router.callback_query(F.data == "list_of_ads")
async def callback_cmd_sign_up(callback: types.CallbackQuery):
    await callback.message.answer(
        text="Спасибі, але функція списку оголошень ще не розроблена"
    )



# @router.message(Command(commands=["cancel"]))
# @router.message(F.text.lower() == "отмена")
# async def cmd_cancel(message: Message, state: FSMContext):
#     await state.clear()
#     await message.answer(
#         text="действие отменено",
#         reply_markup=ReplyKeyboardRemove()
#     )