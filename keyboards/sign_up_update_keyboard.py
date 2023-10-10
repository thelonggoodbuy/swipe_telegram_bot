from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

from aiogram.utils.i18n import gettext as _

def edit_registration_data_keyboard() -> ReplyKeyboardMarkup:
        
    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(
        text=_('Відміна')
    ))
    builder.add(types.KeyboardButton(
        text=_('Змінити email')
    ))
    builder.add(types.KeyboardButton(
        text=_('Змінити пароль')
    ))
    builder.add(types.KeyboardButton(
        text=_('Підтвердити')
    ))
    return builder.as_markup(resize_keyboard=True)