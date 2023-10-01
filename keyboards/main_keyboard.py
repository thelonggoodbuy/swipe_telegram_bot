from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def make_main_keyboard() -> ReplyKeyboardMarkup:
    # row = [KeyboardButton(text=item) for item in items]
    
    builder = ReplyKeyboardBuilder()
    builder.adjust(2, 2)
    builder.add(types.KeyboardButton(
        text='Список оголошень'
    ))
    builder.add(types.KeyboardButton(
        text='Створити оголошення'
    ))
    builder.add(types.KeyboardButton(
        text='Мій профіль'
    ))
    builder.add(types.KeyboardButton(
        text='Змінити мову'
    ))
    return builder.as_markup(resize_keyboard=True)