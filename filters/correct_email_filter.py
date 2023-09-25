from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

from email_validator import validate_email, EmailNotValidError



class ChatTypeFilter(BaseFilter):  # [1]
    # def __init__(self, email: str): # [2]
    #     self.email = email

    async def __call__(self, message: Message) -> bool:  # [3]
        print('------FILTER---CALLL-------')
        print(message.text)
        email = message.text
        print('---------------------------')
        # if isinstance(self.chat_type, str):
        #     return message.chat.type == self.chat_type
        # else:
        #     return message.chat.type in self.chat_type
        try:
            validate_email_status = validate_email(email)
            email = validate_email_status.normalized
            print('return TRUE')
            return True
        except EmailNotValidError:
            print('return False')
            return False