
from aiogram import F, Router, types

from keyboards.invite_keyboard import make_invite_keyboard_uk, make_invite_keyboard_en
from keyboards.choose_language_keyboard import choose_language_keyboard
import pymongo

from keyboards.main_keyboard import make_main_keyboard_uk, make_main_keyboard_en

from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _


router = Router()


@router.message(F.text == __('Змінити мову'))
async def change_language(message: types.Message):

    await message.answer(
        text = _("Оберіть мову"),
        reply_markup=choose_language_keyboard()
    )


@router.message(F.text == 'Українська')
async def change_to_ukrainian(message: types.Message):
    auth_pymongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    auth_db = auth_pymongo_client.rptutorial
    auth_collection = auth_db.bot_aut_collection
    chat_data = auth_collection.find_one({"chat_id": message.chat.id})
    auth_collection.update_one({"chat_id": message.chat.id},\
                                    {"$set": {"chat_language_code": 'uk'}}, upsert=False)
    print(message.from_user)
    await message.answer(text="Ви користуєтеся українською",
                                     reply_markup=make_main_keyboard_uk())


@router.message(F.text == 'English')
async def change_to_ukrainian(message: types.Message):
    auth_pymongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    auth_db = auth_pymongo_client.rptutorial
    auth_collection = auth_db.bot_aut_collection
    chat_data = auth_collection.find_one({"chat_id": message.chat.id})
    auth_collection.update_one({"chat_id": message.chat.id},\
                                    {"$set": {"chat_language_code": 'en'}}, upsert=False)
    print(message.from_user)
    await message.answer(text="Now you are using English",
                                     reply_markup=make_main_keyboard_en())
