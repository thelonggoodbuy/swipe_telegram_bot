from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

def choose_language_keyboard() -> ReplyKeyboardMarkup:
    # row = [KeyboardButton(text=item) for item in items]
    
    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(
        text='Українська'
    ))
    builder.add(types.KeyboardButton(
        text='English'
    ))
    return builder.as_markup(resize_keyboard=True)