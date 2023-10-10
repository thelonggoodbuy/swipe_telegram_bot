from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

from aiogram.utils.i18n import gettext as _

def cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text=_('Назад')
    ))
    builder.add(types.KeyboardButton(
        text=_('Відміна')
    ))
    return builder.as_markup(resize_keyboard=True)