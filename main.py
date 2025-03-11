import logging
import json
import os
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from fastapi import FastAPI
import uvicorn

PORT = int(os.getenv("PORT", 8080))
API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    raise ValueError("❌ ERROR: API_TOKEN o‘rnatilmagan yoki noto‘g‘ri!")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "🚀 FastAPI server ishlayapti!"}

try:
    with open("tests.json", "r", encoding="utf-8") as f:
        tests = json.load(f)
except FileNotFoundError:
    tests = []

user_tests = {}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    web_button = KeyboardButton(
        text="🌐 Web Botni Ochish",
        web_app=WebAppInfo(url="https://web-telegram-bot-qsag.onrender.com")
    )
    keyboard.add(web_button)
    await message.answer("👋 Web botga xush kelibsiz!", reply_markup=keyboard)

@dp.message(Command("test"))
async def start_test(message: types.Message):
    user_id = message.from_user.id
    if not tests:
        await message.answer("❌ Testlar topilmadi!")
        return

    user_tests[user_id] = {
        "questions": random.sample(tests, 10),
        "current_index": 0,
        "correct_answers": 0
    }
    await send_question(message, user_id)

async def send_question(message, user_id):
    test_index = user_tests[user_id]["current_index"]
    if test_index >= len(user_tests[user_id]["questions"]):
        correct = user_tests[user_id]["correct_answers"]
        await bot.send_message(user_id, f"✅ Test tugadi!\n\n🎯 To‘g‘ri javoblar: {correct} / 10")
        return

    test = user_tests[user_id]["questions"][test_index]
    await bot.send_poll(
        chat_id=user_id,
        question=test["savol"],
        options=test["variantlar"],
        type="quiz",
        correct_option_id=test["togri"],
        is_anonymous=False
    )

@dp.poll_answer()
async def handle_poll_answer(poll_answer: types.PollAnswer):
    user_id = poll_answer.user.id
    if user_id in user_tests:
        test_index = user_tests[user_id]["current_index"]
        test = user_tests[user_id]["questions"][test_index]

        if poll_answer.option_ids[0] == test["togri"]:
            user_tests[user_id]["correct_answers"] += 1

        user_tests[user_id]["current_index"] += 1
        message = types.Message(chat=types.Chat(id=poll_answer.user.id, type="private"))
        await send_question(message, user_id)

@app.get("/get_questions")
def get_questions():
    return {"questions": tests}

async def main():
    logging.basicConfig(level=logging.INFO)
    bot_task = asyncio.create_task(dp.start_polling(bot))
    server_task = asyncio.create_task(uvicorn.run(app, host="0.0.0.0", port=PORT))
    await asyncio.gather(bot_task, server_task)

if __name__ == "__main__":
    asyncio.run(main())  # 🔥 Asosiy ishga tushirish
