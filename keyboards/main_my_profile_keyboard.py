from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from aiogram.utils.i18n import gettext as _

def make_main_profile_keyboards() -> ReplyKeyboardMarkup:
    # row = [KeyboardButton(text=item) for item in items]
    
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