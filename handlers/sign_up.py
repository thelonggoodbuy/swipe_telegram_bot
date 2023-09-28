from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.context import FSMContext


router = Router()

# Registration
@router.message(F.text == "Зареєструватись")
async def sign_up_handler(message: types.Message, state: FSMContext):
    await message.reply("Ви намагаєтеся зареєструватися. Функція пока не розроблена.")
