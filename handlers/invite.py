from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards.simple_row import make_row_keyboard




router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):


    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(
        text='Увійти в бот'
    ))
    builder.add(types.KeyboardButton(
        text='Зареєструватись'
    ))
    builder.add(types.KeyboardButton(
        text='Список оголошень'
    ))

    await message.answer(
        text="Привіт! Залогінся або зареєструйся =)",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )