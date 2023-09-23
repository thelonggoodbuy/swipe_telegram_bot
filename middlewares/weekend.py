from datetime import datetime
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery



def _is_weekend() -> bool:
    # 5 - суббота, 6 - воскресенье
    return datetime.utcnow().weekday() in (5, 6)


class WeekendMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        print('--middleware-1---')
        print(_is_weekend())
        print('-------')
        if not _is_weekend():
            return await handler(event, data)
        


class WeekendCallbackMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        print('---middleware-2---')
        print(_is_weekend())
        print('-------')

        if not _is_weekend():
            return await handler(event, data)
        await event.answer(
            "Bot doesn`t work when day off",
            show_alert=True
        )
        return 