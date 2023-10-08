from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def make_main_profile_keyboards() -> ReplyKeyboardMarkup:
    # row = [KeyboardButton(text=item) for item in items]
    
    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(
        text='Мої оголошення'
    ))
    builder.add(types.KeyboardButton(
        text='Мої дані'
    ))
    # builder.add(types.KeyboardButton(
    #     text='Список оголошень'
    # ))
    return builder.as_markup(resize_keyboard=True)