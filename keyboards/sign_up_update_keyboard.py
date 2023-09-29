from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def edit_registration_data_keyboard() -> ReplyKeyboardMarkup:
        
    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(
        text='Відміна'
    ))
    builder.add(types.KeyboardButton(
        text='Відрегувати email'
    ))
    builder.add(types.KeyboardButton(
        text='Відрегувати пароль'
    ))
    builder.add(types.KeyboardButton(
        text='Підтвердити'
    ))
    return builder.as_markup(resize_keyboard=True)