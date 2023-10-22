from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram import types

from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _


def create_ads_keyboard(accomodation_list_of_dict) -> ReplyKeyboardMarkup:
    
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text=_('Попереднє меню')
    ))
    builder.add(types.KeyboardButton(
        text=_('Додати квартиру')
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
        text=_('кредит')
    ))
    builder.add(types.KeyboardButton(
        text=_('тільки готівка')
    ))
    builder.add(types.KeyboardButton(
        text=_('іпотека')
    ))
    return builder.as_markup(resize_keyboard=True)


def save_or_change_ads_kayboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text=_('змінити вартість')
    ))
    builder.add(types.KeyboardButton(
        text=_('зміники коміссію агента')
    ))
    builder.add(types.KeyboardButton(
        text=_('змінити тип оплати')
    ))
    builder.add(types.KeyboardButton(
        text=_('змінити опис')
    ))
    builder.add(types.KeyboardButton(
        text=_('зберігти оголошення')
    ))
    builder.add(types.KeyboardButton(
        text=_('відміна')
    ))
    builder.adjust(2, 2, 1, )
    return builder.as_markup(resize_keyboard=True)