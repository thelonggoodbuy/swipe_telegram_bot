from typing import List

from aiogram import Router, F
from aiogram.types import Message

from filters.find_username import HasUsernameFilter

router = Router()

@router.message(
    F.text,
    HasUsernameFilter()
)
async def message_with_username(
    message: Message,
    usernames: List[str]
):
    await message.reply(
        f'Thanks! I will describe on'
        f'{", ".join(usernames)}'
    )