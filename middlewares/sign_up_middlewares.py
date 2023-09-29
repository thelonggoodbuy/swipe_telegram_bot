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
        print('---------ESF---------')
        entry_sing_up_flag = get_flag(data, "entry_sing_up_flag")
        print(entry_sing_up_flag)
        print(type(entry_sing_up_flag))
        print('---------------------')
        # pprint.pprint(data)
        # print('--------')

        if data['raw_state'] and len(data['raw_state']) != 0: 
            if data['raw_state'] == 'SignUpState:users_email':
                return await handler(event, data)
            if data['raw_state'] == 'SignUpState:users_password':
                return await handler(event, data)

        if entry_sing_up_flag:
            return await handler(event, data)
        