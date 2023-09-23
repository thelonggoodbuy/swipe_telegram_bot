from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Router, F

from keyboards.simple_row import make_row_keyboard

available_food_names = ["Суши", "Спагетти", "Хачапури"]
available_food_sizes = ["Маленькую", "Среднюю", "Большую"]


router = Router()



class OrderFood(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State() 




@router.message(Command("food"))
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите блюдо:",
        reply_markup=make_row_keyboard(available_food_names)
    )

    await state.set_state(OrderFood.choosing_food_name)




@router.message(
    OrderFood.choosing_food_name, # пользователь находиться в одном из состояний
    F.text.in_(available_food_names) # текст сообщения совпадает с одним из предложеных
)
async def food_choosen(message: Message, state: FSMContext):
    await state.update_data(choosen_food=message.text.lower()) # сохраняем выбранные действия в хранилизе FSM
    await message.answer(
        text="Спасибо, выберите размер порции:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )
    await state.set_state(OrderFood.choosing_food_size) # переводим пользователя в следующее состояние


@router.message(OrderFood.choosing_food_name)
async def food_choosen_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого блюда. \n\n"
            "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=make_row_keyboard(available_food_names)
    )


@router.message(OrderFood.choosing_food_size, F.text.in_(available_food_sizes))
async def food_size_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data() # возвращает обьект хранилища 
                                        # для конкретного пользователя в конекртеном чате

    print('--------user_data-----')
    print(user_data)
    print('-----------------------')
    await message.answer(
        text=f"Вы выбрали {message.text.lower()} порцию {user_data['choosen_food']}.\n"
            f"Попробуйте теперь заказать напитки: /drinks",
            reply_markup=ReplyKeyboardRemove()
    )
    await state.clear() # возвращает пользователя в пустое состояние
                        # и удаляет все сохраненные даныне FSM


@router.message(OrderFood.choosing_food_size)
async def food_size_choosen_incorrectly(message: Message):
    await message.answer(
        text = "Я не знаю такого размера порции.\n\n"
                "Пожалуйста выберете один из вариантов из списка ниже:",
        reply_markup=make_row_keyboard(available_food_sizes)
    )

