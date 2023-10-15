from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from aiogram.utils.i18n import gettext as _

def make_main_profile_keyboards() -> ReplyKeyboardMarkup:
    
    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(
        text=_('Мої оголошення')
    ))
    builder.add(types.KeyboardButton(
        text=_('Мої дані')
    ))
    builder.add(types.KeyboardButton(
        text=_('Попереднє меню')
    ))
    return builder.as_markup(resize_keyboard=True)