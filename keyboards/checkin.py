from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


def get_checkin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Aprove', callback_data="confirm")
    kb.button(text='TestCallBackFunction', callback_data="test_call_back")


    print('----inline--keyboard----')
    # print()
    # print('----inline--keyboard----')
    return kb.as_markup()