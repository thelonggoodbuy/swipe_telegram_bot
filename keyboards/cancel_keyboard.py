from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text='Назад'
    ))
    builder.add(types.KeyboardButton(
        text='Відміна'
    ))
    return builder.as_markup(resize_keyboard=True)