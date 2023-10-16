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
        # get first key
        obj_title = next(iter(obj))
        builder.add(types.KeyboardButton(
            text=obj_title
        ))
    builder.add(types.KeyboardButton(
            text=f'Зробити оголошення з існуючою квартирою'
        ))
    builder.adjust(2, 3)
    return builder.as_markup(resize_keyboard=True)





# def choose_version_of_calculation() -> ReplyKeyboardMarkup:
#     builder = ReplyKeyboardBuilder()
#     builder.add(types.KeyboardButton(
#         text='кредит'
#     ))
#     builder.add(types.KeyboardButton(
#         text='тільки готівка'
#     ))
#     builder.add(types.KeyboardButton(
#         text='іпотека'
#     ))
#     return builder.as_markup(resize_keyboard=True)


# def save_or_change_ads_kayboard() -> ReplyKeyboardMarkup:
#     builder = ReplyKeyboardBuilder()
#     builder.add(types.KeyboardButton(
#         text='змінити вартість'
#     ))
#     builder.add(types.KeyboardButton(
#         text='зміники коміссію агента'
#     ))
#     builder.add(types.KeyboardButton(
#         text='змінити тип оплати'
#     ))
#     builder.add(types.KeyboardButton(
#         text='змінити опис'
#     ))
#     builder.add(types.KeyboardButton(
#         text='зберігти оголошення'
#     ))
#     builder.add(types.KeyboardButton(
#         text='відміна'
#     ))
#     builder.adjust(2, 2, 1, )
#     return builder.as_markup(resize_keyboard=True)