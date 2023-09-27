from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

from email_validator import validate_email, EmailNotValidError



class ChatTypeFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        email = message.text
        try:
            validate_email_status = validate_email(email)
            email = validate_email_status.normalized
            return True
        except EmailNotValidError:
            return False