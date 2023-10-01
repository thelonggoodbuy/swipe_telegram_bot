from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards.main_keyboard import make_main_keyboard




router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):

    await message.answer(
        reply_markup=make_main_keyboard()
    )