from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards.main_keyboard import make_main_keyboard

from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _


router = Router()


@router.message(F.text == __("Ласкаво просимо!"))
async def cmd_start(message: types.Message):

    await message.answer(
        text=_("Головне меню"),
        reply_markup=make_main_keyboard()
    )