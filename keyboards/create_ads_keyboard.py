from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram import types



def create_ads_keyboard(accomodation_list_of_dict) -> ReplyKeyboardMarkup:
    
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text='Попереднє меню'
    ))
    builder.add(types.KeyboardButton(
        text='Додати квартиру'
    ))
    for accomodation in accomodation_list_of_dict:
        builder.add(types.KeyboardButton(
            text='№{number}, {address}'.format(number=accomodation['number'], address=accomodation['house_address'])
        ))
    builder.adjust(2, 3)
    return builder.as_markup(resize_keyboard=True)



def choose_version_of_calculation() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text='кредит'
    ))
    builder.add(types.KeyboardButton(
        text='тільки готівка'
    ))
    builder.add(types.KeyboardButton(
        text='іпотека'
    ))
    return builder.as_markup(resize_keyboard=True)


def save_or_change_ads_kayboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text='змінити вартість'
    ))
    builder.add(types.KeyboardButton(
        text='зміники коміссію агента'
    ))
    builder.add(types.KeyboardButton(
        text='змінити тип оплати'
    ))
    builder.add(types.KeyboardButton(
        text='змінити опис'
    ))
    builder.add(types.KeyboardButton(
        text='зберігти оголошення'
    ))
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)