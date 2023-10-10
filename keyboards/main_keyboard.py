from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from aiogram.utils.i18n import gettext as _

def make_main_keyboard() -> ReplyKeyboardMarkup:
    # row = [KeyboardButton(text=item) for item in items]
    
    builder = ReplyKeyboardBuilder()
    builder.adjust(2, 2)
    builder.add(types.KeyboardButton(
        text=_('Оголошення')
    ))
    builder.add(types.KeyboardButton(
        text=_('Створити оголошення')
    ))
    builder.add(types.KeyboardButton(
        text=_('Мій профіль')
    ))
    builder.add(types.KeyboardButton(
        text=_('Змінити мову')
    ))
    return builder.as_markup(resize_keyboard=True)