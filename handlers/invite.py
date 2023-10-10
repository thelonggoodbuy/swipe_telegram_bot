from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards.invite_keyboard import make_invite_keyboard

from aiogram.utils.i18n import gettext as _
import pymongo

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):

    await message.answer(
        text=_("Привіт! Залогінся або зареєструйся =)"),
        reply_markup=make_invite_keyboard()
    )

