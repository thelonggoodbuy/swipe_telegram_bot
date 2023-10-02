from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards.main_keyboard import make_main_keyboard




router = Router()


@router.message(F.text == "Ласкаво просимо!")
async def cmd_start(message: types.Message):

    print('-------NEW----ELEMENT----------')

    await message.answer(
        text="Головне меню",
        reply_markup=make_main_keyboard()
    )