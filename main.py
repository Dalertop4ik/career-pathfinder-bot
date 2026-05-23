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

# Состояния для нашего нового умного опроса
class Quiz(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    answering_questions = State()

# Список разнообразных вопросов под 5 актуальных направлений
QUESTIONS = [
    {
        "text": "1️⃣ Какой школьный предмет или сфера деятельности тебе ближе всего?",
        "answers": [
            ("Информатика, алгоритмы и логика", "python_dev"),
            ("Рисование, дизайн или черчение", "ui_designer"),
            ("Биология, анатомия и химия", "doctor"),
            ("Физика, сборка механизмов, конструкторы", "engineer"),
            ("Обществознание, экономика, общение с людьми", "marketer")
        ]
    },
    {
        "text": "2️⃣ В какой атмосфере тебе хотелось бы работать в будущем?",
        "answers": [
            ("В тишине за кодом, решая сложные технические задачи", "python_dev"),
            ("В творческой среде, создавая красивый визуал приложений", "ui_designer"),
            ("В современной клинике или лаборатории, помогая людям", "doctor"),
            ("В конструкторском бюро или цеху среди роботов и техники", "engineer"),
            ("Удаленно или в стильном офисе, развивая бренды и бизнес", "marketer")
        ]
    },
    {
        "text": "3️⃣ Что для тебя является лучшим результатом проделанной работы?",
        "answers": [
            ("Стабильно работающая программа или сложный скрипт", "python_dev"),
            ("Удобный и эстетичный интерфейс, которым приятно пользоваться", "ui_designer"),
            ("Вылеченный, здоровый и благодарный пациент", "doctor"),
            ("Успешно запущенный и запрограммированный механизм", "engineer"),
            ("Резкий рост продаж и взлет популярности компании", "marketer")
        ]
    },
    {
        "text": "4️⃣ Какое хобби ты бы с удовольствием выбрал на выходные?",
        "answers": [
            ("Написать своего бота или разобраться в новой библиотеке", "python_dev"),
            ("Порисовать в Figma или обработать крутые кадры", "ui_designer"),
            ("Почитать медицинский научпоп или посмотреть док. фильм", "doctor"),
            ("Починить сломанный гаджет или собрать схему на Arduino", "engineer"),
            ("Посмотреть разборы бизнес-стратегий известных брендов", "marketer")
        ]
    }
]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardBuilder()
    kb.button(text="🚀 Начать проф-тестирование")
    await message.answer(
        "Привет! Я продвинутый карьерный бот. Пройди тест, и я детально подберу тебе профессию.", 
        reply_markup=kb.as_markup(resize_keyboard=True)
    )

@dp.message(F.text == "🚀 Начать проф-тестирование")
async def start_quiz(message: types.Message, state: FSMContext):
    await state.clear()  # Очищаем старые данные перед началом нового теста
    await message.answer("Для начала познакомимся. Как тебя зовут?")
    await state.set_state(Quiz.waiting_for_name)

@dp.message(Quiz.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    
    # ВАЛИДАЦИЯ ИМЕНИ: Проверяем на наличие цифр
    if any(char.isdigit() for char in name):
        return await message.answer("❌ Так не бывает! Имя не должно содержать цифры. Введи свое настоящее имя:")
        
    # Проверяем длину имени
    if len(name) < 2:
        return await message.answer("❌ Слишком короткое имя. Введи корректное имя:")

    await state.update_data(name=name)
    await message.answer(f"Приятно познакомиться, {name}! Сколько тебе лет?")
    await state.set_state(Quiz.waiting_for_age)

@dp.message(Quiz.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    # ВАЛИДАЦИЯ ВОЗРАСТА: Проверяем, что введены именно цифры
    if not message.text.isdigit():
        return await message.answer("❌ Пожалуйста, введи возраст целым числом (например: 19):")
    
    age = int(message.text)
    
    # ОГРАНИЧЕНИЕ ПО ВОЗРАСТУ (СТРОГО 18+)
    if age < 18:
        await message.answer(
            "⛔️ Извини, но этот глубокий тест предназначен только для совершеннолетних пользователей (18+).\n"
            "Доступ заблокирован. Удачи! 👋"
        )
        await state.clear()  # Сбрасываем состояние, чтобы бот не ждал ответа
        return
    
    # Сохраняем проверенный возраст и подготавливаем счетчики под новые профессии
    await state.update_data(
        age=age, 
        scores={"python_dev": 0, "ui_designer": 0, "doctor": 0, "engineer": 0, "marketer": 0}, 
        q_index=0
    )
    
    # Достаем первый вопрос
    q = QUESTIONS[0]
    kb = InlineKeyboardBuilder()
    for text, prof in q["answers"]:
        kb.button(text=text, callback_data=f"ans_{prof}")
    kb.adjust(1)
    
    await message.answer(q["text"], reply_markup=kb.as_markup())
    await state.set_state(Quiz.answering_questions)

# Универсальный хендлер для обработки ответов
@dp.callback_query(Quiz.answering_questions, F.data.startswith("ans_"))
async def process_question(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    scores = data.get('scores', {})
    question_index = data.get('q_index', 0)
    
    # Безопасно вырезаем айди профессии, даже если там есть подчеркивания (типа python_dev)
    chosen_prof = callback.data.replace("ans_", "")
    
    # Добавляем 1 балл выбранной профессии
    scores[chosen_prof] = scores.get(chosen_prof, 0) + 1
    
    # Переходим к следующему вопросу
    question_index += 1
    
    if question_index < len(QUESTIONS):
        # Если вопросы еще остались, обновляем индекс и выводим следующий
        await state.update_data(scores=scores, q_index=question_index)
        q = QUESTIONS[question_index]
        
        kb = InlineKeyboardBuilder()
        for text, prof in q["answers"]:
            kb.button(text=text, callback_data=f"ans_{prof}")
        kb.adjust(1)
        
        await callback.message.edit_text(q["text"], reply_markup=kb.as_markup())
    else:
        # Вопросы закончились! 
        if not scores:
            await callback.message.edit_text("Не удалось определить результаты. Попробуйте пройти тест снова!")
            await state.clear()
            return

        # 1. Находим максимальный набранный балл
        max_score = max(scores.values())
        
        # 2. Собираем список ВСЕХ профессий, у которых балл равен максимальному
        winner_profs = [prof for prof, score in scores.items() if score == max_score]
        
        if len(winner_profs) == 1:
            # Обычный сценарий: есть один явный победитель
            winner_prof = winner_profs[0]
            prof_data = db.get_profession(winner_prof)
            
            if prof_data:
                title, desc, skills = prof_data
                text = (
                    f"🎯 <b>{data.get('name', 'Пользователь')}, твой тест успешно завершен!</b>\n\n"
                    f"💻 <b>Твоя идеальная сфера:</b> {title}\n\n"
                    f"📋 <b>Описание направления:</b>\n{desc}\n\n"
                    f"🛠 <b>Ключевые навыки для старта:</b>\n<i>{skills}</i>"
                )
                db.add_user(callback.from_user.id, data.get('name', 'Неизвестно'), data.get('age', 0), winner_prof)
            else:
                text = "❌ Ошибка: Направление не найдено в базе данных."
                
        else:
            # Сценарий ничьей: пользователь выбрал несколько направлений поровну
            text = (
                f"🎯 <b>{data.get('name', 'Пользователь')}, твой тест успешно завершен!</b>\n\n"
                f"У тебя очень разносторонние интересы! Тебе одинаково хорошо подходят сразу несколько направлений:\n\n"
            )
            
            # Собираем описания для каждой победившей профессии
            for prof in winner_profs:
                prof_data = db.get_profession(prof)
                if prof_data:
                    title, desc, _ = prof_data # Навыки тут можно опустить, чтобы не перегружать текст
                    text += f"🔹 <b>{title}</b>\n<i>{desc}</i>\n\n"
            
            text += "💡 <b>Совет:</b> Обрати внимание на профессии на стыке этих сфер (например, IT-медицина или продуктовый дизайн)!"
            
            # Сохраняем в БД победителей через запятую (например, "python_dev,marketer")
            combined_profs = ",".join(winner_profs)
            db.add_user(callback.from_user.id, data.get('name', 'Неизвестно'), data.get('age', 0), combined_profs)

        await callback.message.edit_text(text, parse_mode="HTML")
        await state.clear()

async def main():
    print("Бот запущен и готов к тестам!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
        
        
        
