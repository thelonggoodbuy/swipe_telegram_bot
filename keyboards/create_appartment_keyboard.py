from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram import types



def choose_house_keyboard(obj_list) -> ReplyKeyboardMarkup:
    
    builder = ReplyKeyboardBuilder()
    for obj in obj_list:
        builder.add(types.KeyboardButton(
            text=f'ЖК {obj[1]} за адресою {obj[2]}'
        ))
    builder.add(types.KeyboardButton(
            text=f'Зробити оголошення з існуючою квартирою'
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
            text=f'Зробити оголошення з існуючою квартирою'
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
            text=f'Зробити оголошення з існуючою квартирою'
        ))
    builder.adjust(2, 3)
    return builder.as_markup(resize_keyboard=True)


def save_or_change_accomodation_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text='змінити будинок і номер квартири'
    ))
    builder.add(types.KeyboardButton(
        text='змінити тип нерухомості'
    ))
    builder.add(types.KeyboardButton(
        text='змінити тип планування'
    ))
    builder.add(types.KeyboardButton(
        text='змінити життєві умови'
    ))
    builder.add(types.KeyboardButton(
        text='змінити тип опалення'
    ))
    builder.add(types.KeyboardButton(
        text='змінити схему квартири'
    ))
    builder.add(types.KeyboardButton(
        text='змінити фотографії'
    ))
    builder.add(types.KeyboardButton(
        text='зберігти квартиру'
    ))
    builder.add(types.KeyboardButton(
        text='відміна'
    ))
    builder.adjust(3, 3)
    return builder.as_markup(resize_keyboard=True)