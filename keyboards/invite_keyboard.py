from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def make_invite_keyboard() -> ReplyKeyboardMarkup:
    # row = [KeyboardButton(text=item) for item in items]
    
    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(
        text='Увійти в бот'
    ))
    builder.add(types.KeyboardButton(
        text='Зареєструватись'
    ))
    builder.add(types.KeyboardButton(
        text='Список оголошень'
    ))
    return builder.as_markup(resize_keyboard=True)