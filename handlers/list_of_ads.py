from aiogram import F, Router, types

from middlewares import auth_middlewares

import pprint

from typing import Dict, Any


router = Router()
router.message.middleware(auth_middlewares.IsAuthenticatedMiddleware())
router.message.middleware(auth_middlewares.GetJWTAuthenticationMiddleware())




# List of ads
@router.message(F.text == "Список оголошень")
async def list_of_ads_handler(message: types.Message, middleware_access_data: Dict[str, Any] | None):
    print('-------------MESSAGE-----DICT---------------')
    # pprint.pprint(data)
    print(middleware_access_data)
    print('--------------------------------------------')
    await message.reply("Ви намагаєтеся отримати список оголошень. Функція пока не розроблена.")
