from typing import Union

from aiogram.filters import BaseFilter
from aiogram.filters.state import StateFilter
from aiogram.types import Message

from email_validator import validate_email, EmailNotValidError

# --------------------------------------------


from inspect import isclass
from typing import Any, Dict, Optional, Sequence, Type, Union, cast

from aiogram.filters.base import Filter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import TelegramObject

StateType = Union[str, None, State, StatesGroup, Type[StatesGroup]]
# --------------------------------------------



class IsNotDefaultStateFilter(Filter):
    """
    State filter
    """

    __slots__ = ("states",)

    def __init__(self, *states: StateType) -> None:
        if not states:
            raise ValueError("At least one state is required")

        self.states = states

    def __str__(self) -> str:
        return self._signature_to_string(
            *self.states,
        )

    async def __call__(
        self, obj: TelegramObject, raw_state: Optional[str] = None
    ) -> Union[bool, Dict[str, Any]]:
        print('----filter----run----')
        allowed_states = cast(Sequence[StateType], self.states)
        print('----allowed----states----')
        print(allowed_states)
        # print(allowed_states[0].__all_states__)
        # state = await allowed_states[0].get_data()
        # state = await allowed_states.get_data()
        # print(state)

        for allowed_state in allowed_states:
            print('-----option_1-----')
            if isinstance(allowed_state, str) or allowed_state is None:
                print('-----option_1_1-----')
                if allowed_state == "*" or raw_state == allowed_state:
                    print('-----option_1_1_1-----')
                    return True
                
            elif isinstance(allowed_state, (State, StatesGroup)):
                print('-----option_1_2-----')
                if allowed_state(event=obj, raw_state=raw_state):
                    print('-----option_1_2_1-----')
                    return True
            elif isclass(allowed_state) and issubclass(allowed_state, StatesGroup):
                print('-----option_1_3-----')
                if allowed_state()(event=obj, raw_state=raw_state):
                    print('-----option_1_3_1-----')
                    return True
                    
        print('-----option_2-----')
        return False