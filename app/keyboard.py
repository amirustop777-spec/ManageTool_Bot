from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text= 'Курсы валют'), KeyboardButton(text= 'Калькулятор' ),KeyboardButton(text= 'Прогноз от ИИ' ), KeyboardButton(text= 'FAQ' )]
], resize_keyboard= True) #функции бота

main1 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text= '🇺🇸 USD'), KeyboardButton(text= '🇪🇺 EUR' ), KeyboardButton(text= '🇨🇳 CNY' ), KeyboardButton(text= '🇰🇿 KZT' )],
    [KeyboardButton(text= '🔙Cancel')]
], resize_keyboard= True, #минимальный размер кнопок
                           input_field_placeholder= 'Выбор валюты') #выбор валюты
