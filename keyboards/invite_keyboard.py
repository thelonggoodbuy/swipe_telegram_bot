from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

def make_invite_keyboard() -> ReplyKeyboardMarkup:    
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text=_('Увійти в бот')
    ))
    builder.add(types.KeyboardButton(
        text=_('Зареєструватись')
    ))
    return builder.as_markup(resize_keyboard=True)


def make_invite_keyboard_uk() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text='Увійти в бот'
    ))
    builder.add(types.KeyboardButton(
        text='Зареєструватись'
    ))
    return builder.as_markup(resize_keyboard=True)

def make_invite_keyboard_en() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(
        text='Sign In'
    ))
    builder.add(types.KeyboardButton(
        text='Sign Up'
    ))

    return builder.as_markup(resize_keyboard=True)