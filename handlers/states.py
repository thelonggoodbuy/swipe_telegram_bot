from aiogram.fsm.state import State, StatesGroup, default_state

class SignUpState(StatesGroup):
    users_email = State()
    users_password = State()
    is_not_default_state = State()