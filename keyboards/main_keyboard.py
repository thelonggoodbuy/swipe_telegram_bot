from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from aiogram.utils.i18n import gettext as _

def make_main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.adjust(2, 2)
    builder.add(types.KeyboardButton(
        text=_('Оголошення')
    ))
    builder.add(types.KeyboardButton(
        text=_('Створити оголошення')
    ))
    builder.add(types.KeyboardButton(
        text=_('Мій профіль')
    ))
    builder.add(types.KeyboardButton(
        text=_('Змінити мову')
    ))
    return builder.as_markup(resize_keyboard=True)


def make_main_keyboard_uk() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.adjust(2, 2)
    builder.add(types.KeyboardButton(
        text='Оголошення'
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


def make_main_keyboard_en() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.adjust(2, 2)
    builder.add(types.KeyboardButton(
        text='Ads'
    ))
    builder.add(types.KeyboardButton(
        text='Create ad'
    ))
    builder.add(types.KeyboardButton(
        text='My profile'
    ))
    builder.add(types.KeyboardButton(
        text='Change Language'
    ))
    return builder.as_markup(resize_keyboard=True)