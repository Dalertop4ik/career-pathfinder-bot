import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config import TOKEN
from database import Database

bot = Bot(token=TOKEN)
dp = Dispatcher()
db = Database()

# Состояния опроса
class Quiz(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_interest = State()

# --- Хендлеры ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardBuilder()
    kb.button(text="🚀 Пройти тест")
    await message.answer(
        "Привет! Я помогу тебе выбрать профессию. Начнем опрос?", 
        reply_markup=kb.as_markup(resize_keyboard=True)
    )

@dp.message(F.text == "🚀 Пройти тест")
async def start_quiz(message: types.Message, state: FSMContext):
    await message.answer("Как тебя зовут?")
    await state.set_state(Quiz.waiting_for_name)

@dp.message(Quiz.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Приятно познакомиться, {message.text}! Сколько тебе лет?")
    await state.set_state(Quiz.waiting_for_age)

@dp.message(Quiz.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Пожалуйста, введи число.")
    
    await state.update_data(age=int(message.text))
    
    kb = InlineKeyboardBuilder()
    kb.button(text="IT", callback_data="interest_it")
    kb.button(text="Дизайн", callback_data="interest_design")
    
    await message.answer("Какая сфера тебе интересна?", reply_markup=kb.as_markup())
    await state.set_state(Quiz.waiting_for_interest)

@dp.callback_query(Quiz.waiting_for_interest)
async def process_interest(callback: types.CallbackQuery, state: FSMContext):
    interest = callback.data.split("_")[1]
    user_data = await state.get_data()
    
    # Сохраняем в БД
    db.add_user(callback.from_user.id, user_data['name'], user_data['age'], interest)
    
    # Получаем рекомендации
    jobs = db.get_recommendations(interest)
    
    # Подготавливаем текст ответа
    response = f"🎯 {user_data['name']}, вот рекомендации для тебя:\n\n"
    
    if jobs:
        for title, desc in jobs:
            response += f"✅ **{title}**\n_{desc}_\n\n"
    else:
        response += "Пока в базе нет профессий для этой сферы, но мы скоро их добавим!"
        
    await callback.message.answer(response, parse_mode="Markdown")
    await state.clear()
    await callback.answer()

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")