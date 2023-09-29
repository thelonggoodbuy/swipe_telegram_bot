from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup, default_state

from keyboards.invite_keyboard import make_invite_keyboard
from middlewares.sign_up_middlewares import OnlySignUpMiddleware

from aiogram.filters.state import StateFilter

from aiogram import flags

router = Router()
router.message.middleware(OnlySignUpMiddleware())



class SignUpState(StatesGroup):
    users_email = State()
    users_password = State()
    is_not_default_state = State()


# Entry point for user sign up
# @flags.entry_sing_up_flag
@router.message(F.text == "Зареєструватись", flags={'entry_sing_up_flag': 'True'})
async def sign_up_handler(message: types.Message, state: FSMContext):

    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(
        text='Відміна'
    ))

    await message.reply("Введіть свій email.", 
                        reply_markup=builder.as_markup(resize_keyboard=True))
    await state.update_data(is_not_default_state='true')
    await state.set_state(SignUpState.users_email)


# --------------------------WORK----AREA-------------------------------------------------


@router.message(F.text == "Відміна")
async def sign_up_cancel(message: types.Message, state: FSMContext):
    # print('--------1------------------')
    # print(state)
    # print('--------2------------------')
    await state.clear()
    # print('--------3------------------')

    # print(state)

    await message.answer(
        text="Реєстрацію відмінено. Залогінся або зареєструйся =)",
        reply_markup=make_invite_keyboard()
    )


# --------------------------END----AREA---------------------------------------------------