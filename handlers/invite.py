from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards.invite_keyboard import make_invite_keyboard




router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):

    await message.answer(
        text="Привіт! Залогінся або зареєструйся =)",
        reply_markup=make_invite_keyboard()
    )