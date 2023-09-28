from aiogram import F, Router, types

from middlewares import auth_middlewares



router = Router()
router.message.middleware(auth_middlewares.IsAuthenticatedMiddleware())


# List of ads
@router.message(F.text == "Список оголошень")
async def list_of_ads_handler(message: types.Message):
    await message.reply("Ви намагаєтеся отримати список оголошень. Функція пока не розроблена.")
