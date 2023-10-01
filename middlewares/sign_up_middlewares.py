import pymongo

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

import pprint

from aiogram.dispatcher.flags import get_flag

# from handlers.states import SignUpState

class OnlySignUpMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        entry_sing_up_flag = get_flag(data, "entry_sing_up_flag")

        # print('--------handler-----------------------------')
        # pprint.pprint(handler.__dict__)
        # print('--------HANDLER---OTHERS--------------------')
        # # pprint.pprint(handler.state)
        # print('--------event-------------------------------')
        # print(SignUpState.users_email._state)
        # print('********************************************')
        # print(SignUpState.__all_states__)
        # print(SignUpState.users_email.get_data())
        # print(SignUpState.users_email.get_state())
        # print(type(event))
        # pprint.pprint(event.__dict__)
        # print('--------data--------------------------------')
        # state_context = data['state']
        # pprint.pprint(data['raw_state'])
        # pprint.pprint(type(data['raw_state']))
        # pprint(state_context)
        # pprint(state_context.get_data())
        # pprint.pprint(type(data['state']))
        print('--------end---------------------------------')

        if data['raw_state'] and len(data['raw_state']) != 0: 
            match data['raw_state']:
                case 'SignUpState:users_email':
                    return await handler(event, data)
                case 'SignUpState:users_password':
                    return await handler(event, data)

        if entry_sing_up_flag:
            return await handler(event, data)
        