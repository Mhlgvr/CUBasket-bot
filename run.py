import sqlite3
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# from aiogram.utils import executor
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
# dp.middleware.setup(LoggingMiddleware())

# Подключение к базе данных
conn = sqlite3.connect("teams.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    full_name TEXT,
                    stream TEXT
                )''')
conn.commit()

# Клавиатура для выбора участия
participation_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
participation_keyboard.add(KeyboardButton("Да"), KeyboardButton("Нет"))

# Клавиатура для выбора потока
streams = ["Восток", "Запад", "Север", "Юг", "Магистратура", "Преподаватели"]
stream_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
for stream in streams:
    stream_keyboard.add(KeyboardButton(stream))

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Добро пожаловать в бота баскетбольного турнира! 🏀")
    await message.answer("Этот турнир собирает лучшие команды по регионам и уровням подготовки. Хотите принять участие?", reply_markup=participation_keyboard)

@dp.message_handler(lambda message: message.text.lower() == "да")
async def ask_full_name(message: types.Message):
    await message.answer("Отлично! Введите ваше ФИО:")

@dp.message_handler(lambda message: message.text.lower() == "нет")
async def decline_participation(message: types.Message):
    await message.answer("Хорошо! Если передумаете, просто напишите /start.")

@dp.message_handler(lambda message: len(message.text.split()) >= 2)
async def ask_stream(message: types.Message):
    user_id = message.from_user.id
    full_name = message.text
    await message.answer("Теперь выберите ваш поток:", reply_markup=stream_keyboard)
    dp.register_message_handler(lambda msg: save_participant(msg, user_id, full_name), content_types=types.ContentTypes.TEXT)

async def save_participant(message: types.Message, user_id, full_name):
    if message.text not in streams:
        await message.answer("Выберите поток из списка!")
        return
    
    stream = message.text
    cursor.execute("INSERT INTO participants (user_id, full_name, stream) VALUES (?, ?, ?)", (user_id, full_name, stream))
    conn.commit()
    await message.answer(f"Вы успешно зарегистрированы в команде {stream}! 🏀")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.start_polling(dp, skip_updates=True)