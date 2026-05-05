from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from tool import Valute_Manager, AI_Assistant
from database import DataBase
import app.keyboard as kb 

router = Router()
ai = AI_Assistant()

class Form(StatesGroup):
    waiting_for_valtype = State()
    waiting_for_calc_val = State()   
    waiting_for_sum = State()
    waiting_for_ai_val = State()
     

# 1. КОМАНДА СТАРТ
@router.message(CommandStart())
async def cmd_start(message: Message, db: DataBase):

    user_id = message.from_user.id
    user = await db.search_user(user_id)

    if user:
        await message.answer(
                    "<b>С возвращением в строй!</b> 👋\n\n"
                    "Рад снова тебя видеть. Твои данные в порядке, и я готов к выполнению новых задач.\n\n"
                    "Чем займемся сегодня?",
                    parse_mode="HTML",
                    reply_markup=kb.main
        )  
    else:
        await db.save_user(user_id, message.from_user.username)
        await message.answer(
            "<b>Добро пожаловать в ManageTool!</b> 🛠\n\n"
            "Я тебя не нашел в своей базе данных, поэтому <b>успешно зарегистрировал</b> твой профиль.\n\n"
            "Теперь тебе доступны все функции управления. Начнем работу?",
            parse_mode="HTML",
            reply_markup=kb.main
        )

    await message.answer_sticker(sticker='CAACAgIAAxkBAAIEYGnzRnbCef3ZAuCz6TvNzSx70DIyAAL8swAC-nFYSySVJZD6Fu-dOwQ')
    

# 2. ТЕКСТОВЫЕ КНОПКИ ГЛАВНОГО МЕНЮ
FAQ_TEXT = """
📋 <b>Часто задаваемые вопросы</b>

<b>💰 Курсы валют</b>
▸ Откуда курсы? — ЦБ РФ + 2% комиссия
▸ Почему курс отличается? — Банки добавляют свою маржу
▸ Обновляются? — Да, каждый рабочий день ЦБ

<b>🧮 Калькулятор</b>
▸ Точный ли расчёт? — Ориентировочный, курс может измениться
▸ Какие валюты? — USD, EUR, CNY, KZT
▸ Комиссия включена? — Да, 2% от курса ЦБ

<b>🔮 Прогноз от ИИ</b>
▸ Это финансовый совет? — Нет, только аналитика
▸ Почему медленно? — ИИ требует времени на генерацию
▸ Можно доверять? — ИИ показывает тренд, не гарантию

<b>🔐 Безопасность</b>
▸ Бот крадёт данные? — Нет, бот не хранит личные данные
▸ Это официальный проект? — Нет, частный проект s1lenZ

<b>📞 Поддержка</b>
▸ Ошибка? — Напиши: amiyume@gmail.com
"""

@router.message(F.text == 'FAQ') 
async def get_help(message: Message):
    await message.answer(FAQ_TEXT, parse_mode="HTML")

@router.message(F.text == 'Кто автор бота?')
async def who_is_avtor(message: Message):
    await message.answer('Создатель бота: s1lenZ (Amir)')
    await message.answer_sticker(sticker='CAACAgIAAxkBAAIEXmnzRj45oJ4eIBosIaLOOilZG-QjAAIonQAC8ctZS5p2W3ga6h-EOwQ')

@router.message(F.text == '🔙Cancel')
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer_sticker(sticker='CAACAgIAAxkBAAIEYmnzRp7JeE4Ss3cEQlFD4s437qCkAAKeogACWfNgS2u6jcz-zgQ_OwQ')
    await message.answer("Возврат в главное меню", reply_markup=kb.main)

# 3. ЛОГИКА КАЛЬКУЛЯТОРА
@router.message(F.text == 'Калькулятор')
async def start_calculator(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_for_calc_val) 
    await message.answer('🧮 Режим калькулятора: Выберите валюту', reply_markup=kb.main1)

@router.message(Form.waiting_for_calc_val)
async def calc_val_choice(message: Message, state: FSMContext):
    val_name = message.text.upper()[-3:]
    if val_name in ['USD', 'CNY', 'KZT', 'EUR']:
        await state.update_data(chosen_val=val_name)
        await message.answer(f'Выбрано: {val_name}. Теперь введите сумму цифрами:')
        await state.set_state(Form.waiting_for_sum) 
    else:
        await message.answer('Пожалуйста, выберите валюту из списка на кнопках!')

@router.message(Form.waiting_for_sum)
async def process_calc(message: Message, state: FSMContext):
    check_text = message.text.replace('.', '', 1).replace(',', '', 1)
    if check_text.isdigit():
        amount = float(message.text.replace(',', '.'))
        user_data = await state.get_data()
        val_name = user_data.get('chosen_val')

        data = Valute_Manager(val_name)
        today, _ = await data.get_need_info()
        res = round(amount * float(today * 1.02), 2)
        
        await message.answer(
            f"🧮 **Результат расчета:**\n{amount} {val_name} = {res} ₽\n(курс: {today})", 
            parse_mode="Markdown"
        )
        await state.clear() 
        await message.answer("Готово!", reply_markup=kb.main)
    else:
        await message.answer("Введите сумму числом!")

# 4. ЛОГИКА КУРСОВ ВАЛЮТ
@router.message(F.text == 'Курсы валют')
async def start_val_check(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_for_valtype)
    await message.answer('Выберите валюту для проверки курса', reply_markup=kb.main1)

@router.message(Form.waiting_for_valtype)
async def val_type_handler(message: Message, state: FSMContext):
    val_name = message.text.upper()[-3:]
    if val_name in ['USD', 'CNY', 'KZT', 'EUR']:
        data = Valute_Manager(val_name) 
        today, yesterday = await data.get_need_info()
        await message.answer(f"🧮 1 {val_name} = {today}₽\n(Вчера было: {yesterday}₽)")
        await state.clear()
        await message.answer('Что-нибудь еще?', reply_markup=kb.main)
    else:
        await message.answer('Валюта не найдена!')

# 5. ИИ ПРОГНОЗ
@router.message(F.text == 'Прогноз от ИИ')
async def start_ai_forecast(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_for_ai_val) 
    await message.answer('📈 Аналитика AI: Выберите валюту', reply_markup=kb.main1)

@router.message(Form.waiting_for_ai_val)
async def process_ai_forecast(message: Message, state: FSMContext):
    val_name = message.text.upper()[-3:]
    
    if val_name in ['USD', 'CNY', 'KZT', 'EUR']:
        await message.answer(f'🔍 Генерирую отчет по {val_name}... Это займет пару секунд.')
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        
        prompt = f"""
        Ты — ведущий финансовый аналитик системы ManageTool. 
        Проведи анализ валюты {val_name} по следующему шаблону:
        📊 АНАЛИТИЧЕСКИЙ ОТЧЕТ: {val_name}/RUB
        ---
        📈 Технические индикаторы: Волатильность, Тренд.
        📉 Фундаментальные факторы: Описание события.
        ⚖️ Риск-профиль (12 месяцев): Вероятность укрепления/ослабления в %.
        🔍 Заключение: Вывод из 2 предложений.
        📊Итог: Закупать или нет
        ---
        Отказ от ответственности: Данные носят информационный характер.
        """
        
        try:
            result = await ai.get_answer(prompt)
            
            try:
                await message.answer(result, parse_mode="HTML")
            except Exception:
                await message.answer(result)
                
        except Exception as e:
            print(f"Ошибка при вызове ИИ: {e}")
            await message.answer("🤖 Извини, мой аналитический модуль временно недоступен. Попробуй позже.")
        
        await state.clear()
        await message.answer("Анализ завершен", reply_markup=kb.main)
    else:
        await message.answer("⚠️ Пожалуйста, выбери валюту из предложенных кнопок.")

# 6. ВСПОМОГАТЕЛЬНЫЕ ХЕНДЛЕРЫ
@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f"ID фото: `{message.photo[-1].file_id}`", parse_mode="MarkdownV2")

@router.message(F.sticker)
async def get_sticker_id(message: Message):
    await message.answer(f"ID стикера: `{message.sticker.file_id}`", parse_mode="MarkdownV2")

# 7. ОБЫЧНЫЙ ЧАТ С ИИ
@router.message(F.text)
async def simple_chat(message: Message, state: FSMContext):
    if await state.get_state() is not None:
        return 
    
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        response = await ai.get_answer(message.text)
        try:
            await message.answer(response, parse_mode="HTML")
        except Exception:
            await message.answer(response) 
    except Exception as e:
        print(f"Ошибка в чате: {e}")
        await message.answer('🤖 Я призадумался... Попробуй позже.')
