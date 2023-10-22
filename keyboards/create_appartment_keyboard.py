from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram import types

from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

def choose_house_keyboard(obj_list) -> ReplyKeyboardMarkup:
    
    builder = ReplyKeyboardBuilder()
    for obj in obj_list:
        builder.add(types.KeyboardButton(
            text=_('ЖК {obj_1} за адресою {obj_2}'.format(obj_1=obj[1], obj_2=obj[2]))
        ))
    builder.add(types.KeyboardButton(
            text=_(f'Зробити оголошення з існуючою квартирою')
        ))
    builder.adjust(2, 3)
    return builder.as_markup(resize_keyboard=True)


def choose_house_subordinate_obj_kb(obj_list) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for obj in obj_list:
        obj_title = next(iter(obj))
        builder.add(types.KeyboardButton(
            text=obj_title
        ))
    builder.add(types.KeyboardButton(
            text=_(f'Зробити оголошення з існуючою квартирою')
        ))
    builder.adjust(2, 3)
    return builder.as_markup(resize_keyboard=True)


def choose_from_accomodation_model_dict_kb(obj_dict):
    builder = ReplyKeyboardBuilder()
    for obj in obj_dict.keys():
        builder.add(types.KeyboardButton(
        text=obj
        ))
    builder.add(types.KeyboardButton(
            text=_(f'Зробити оголошення з існуючою квартирою')
        ))
    builder.adjust(2, 3)
    return builder.as_markup(resize_keyboard=True)


def save_or_change_accomodation_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text=_('змінити будинок і номер квартири')
    ))
    builder.add(types.KeyboardButton(
        text=_('змінити тип нерухомості')
    ))
    builder.add(types.KeyboardButton(
        text=_('змінити тип планування')
    ))
    builder.add(types.KeyboardButton(
        text=_('змінити життєві умови')
    ))
    builder.add(types.KeyboardButton(
        text=_('змінити тип опалення')
    ))
    builder.add(types.KeyboardButton(
        text=_('змінити схему квартири')
    ))
    builder.add(types.KeyboardButton(
        text=_('змінити фотографії')
    ))
    builder.add(types.KeyboardButton(
        text=_('зберігти квартиру')
    ))
    builder.add(types.KeyboardButton(
        text=_('відміна')
    ))
    builder.adjust(3, 3)
    return builder.as_markup(resize_keyboard=True)