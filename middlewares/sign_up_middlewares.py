import pymongo

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

import pprint

from aiogram.dispatcher.flags import get_flag

class OnlySignUpMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        entry_sing_up_flag = get_flag(data, "entry_sing_up_flag")

        if data['raw_state'] and len(data['raw_state']) != 0: 
            match data['raw_state']:
                case 'SignUpState:users_email':
                    return await handler(event, data)
                case 'SignUpState:users_password':
                    return await handler(event, data)

        if entry_sing_up_flag:
            return await handler(event, data)
        