from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENTS = ["maksheyhey@gmail.com", "btatp3@gmail.com"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

user_data = {}

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECIPIENTS)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENTS, msg.as_string())

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_data[message.chat.id] = {}
    await bot.send_message(message.chat.id, "Привет! Давай коротко разберёмся:\n\n1. Как тебя зовут?")

@dp.message_handler(lambda msg: "name" not in user_data.get(msg.chat.id, {}))
async def ask_issue(message: types.Message):
    user_data[message.chat.id]["name"] = message.text

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    options = ["тревога", "зависимость", "паника", "апатия", "злость", "другое"]
    keyboard.add(*options)

    await bot.send_message(message.chat.id, "2. Что тебя беспокоит?", reply_markup=keyboard)

@dp.message_handler(lambda msg: "issue" not in user_data.get(msg.chat.id, {}))
async def ask_goal(message: types.Message):
    user_data[message.chat.id]["issue"] = message.text

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    options = ["свобода", "спокойствие", "энергия", "уверенность", "принятие", "другое"]
    keyboard.add(*options)

    await bot.send_message(message.chat.id, "3. А что ты хочешь вместо этого?", reply_markup=keyboard)

@dp.message_handler(lambda msg: "goal" not in user_data.get(msg.chat.id, {}))
async def ask_attempts(message: types.Message):
    user_data[message.chat.id]["goal"] = message.text
    await bot.send_message(message.chat.id, "4. Что ты уже пробовал?")

@dp.message_handler(lambda msg: "attempts" not in user_data.get(msg.chat.id, {}))
async def ask_ready(message: types.Message):
    user_data[message.chat.id]["attempts"] = message.text

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    options = ["Да, готов(а)", "Нет", "Не уверен(а)"]
    keyboard.add(*options)

    await bot.send_message(message.chat.id, "5. Ты сейчас готов(а)?", reply_markup=keyboard)

@dp.message_handler(lambda msg: "ready" not in user_data.get(msg.chat.id, {}))
async def ask_contact(message: types.Message):
    user_data[message.chat.id]["ready"] = message.text
    await bot.send_message(message.chat.id, "6. Оставь контакт, чтобы мы могли связаться.")

@dp.message_handler(lambda msg: "contact" not in user_data.get(msg.chat.id, {}))
async def finish(message: types.Message):
    user_data[message.chat.id]["contact"] = message.text
    data = user_data[message.chat.id]

    text = f"""
Новая заявка из анкеты ZonovHypnoBot:
1. Имя: {data['name']}
2. Что беспокоит: {data['issue']}
3. Что хочет: {data['goal']}
4. Что уже пробовал: {data['attempts']}
5. Готов к работе: {data['ready']}
6. Контакт: {data['contact']}
"""

    try:
        send_email("Новая анкета", text)
        await bot.send_message(message.chat.id, "✅ Спасибо! Всё получено.\nInstagram: https://instagram.com/m_a_k_s_zonov\nTelegram: https://t.me/maks_zonov")
    except Exception as e:
        await bot.send_message(message.chat.id, f"Ошибка при отправке анкеты. {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
