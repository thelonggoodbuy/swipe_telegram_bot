from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards.checkin import get_checkin_kb
from middlewares.weekend import WeekendMessageMiddleware



router = Router()
router.message.filter(F.chat.type == 'private')
router.message.middleware(WeekendMessageMiddleware())




@router.callback_query(F.data == "test_call_back")
async def checkin_confirm(callback: CallbackQuery):
    print('---6---')
    await callback.answer(
        "Test call back function work",
        show_alert=True
    )



@router.message(Command('checkin'))
async def cmd_checkin(message: Message):
    print('---4---')
    await message.answer(
        "Please, enter button!",
        reply_markup=get_checkin_kb()
    )


@router.callback_query(F.data == "confirm")
async def checkin_confirm(callback: CallbackQuery):
    print('---5---')
    await callback.answer(
        "Thanks, I will aproove",
        show_alert=True
    )


@router.message(
    Command(commands=["test_message"]),
)
async def test_message_function(message:Message):
    await message.answer("Test handler, <b>checkin</b>!", parse_mode="HTML")


