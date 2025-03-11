import logging
import json
import os
import random
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from fastapi import FastAPI
import uvicorn

# 🔹 1️⃣ Render uchun PORT'ni olish
PORT = int(os.getenv("PORT", 8080))

# 🔹 2️⃣ Telegram API Token'ni olish
API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    raise ValueError("❌ ERROR: API_TOKEN o‘rnatilmagan yoki noto‘g‘ri!")

# 🔹 3️⃣ Aiogram botini yaratish
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# 🔹 4️⃣ FastAPI web serverini yaratish
app = FastAPI()

# 🔹 5️⃣ FastAPI asosiy sahifasi (`GET /` endpoint)
@app.get("/")
def read_root():
    return {"message": "🚀 FastAPI server ishlayapti!"}

# 🔹 6️⃣ Testlarni yuklash
try:
    with open("tests.json", "r", encoding="utf-8") as f:
        tests = json.load(f)
except FileNotFoundError:
    tests = []

# 🔹 7️⃣ Foydalanuvchi test natijalarini saqlash
user_tests = {}

# 🔹 8️⃣ Web sahifani ochish tugmasi
@router.message(Command("start"))
async def start_cmd(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    web_button = KeyboardButton(
        text="🌐 Web Botni Ochish",
        web_app=WebAppInfo(url="https://your-web-url.com")  # Web sahifa URL'sini qo‘ying
    )
    keyboard.add(web_button)
    await message.answer("👋 Web botga xush kelibsiz!", reply_markup=keyboard)

# 🔹 9️⃣ Testni boshlash
@router.message(Command("test"))
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

# 🔹 🔟 Foydalanuvchiga test yuborish
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

# 🔹 1️⃣1️⃣ Foydalanuvchi javobini qayta ishlash
@router.poll_answer()
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

# 🔹 1️⃣2️⃣ Web API (`/get_questions` endpoint)
@app.get("/get_questions")
def get_questions():
    return {"questions": tests}

# 🔹 1️⃣3️⃣ FastAPI serveri va botni ishga tushirish
async def start_bot():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.info(f"🚀 Server ishga tushdi! Port: {PORT}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_bot())  # 🔥 Aiogram botni ishga tushirish
    uvicorn.run(app, host="0.0.0.0", port=PORT)  # 🔥 FastAPI serverni ishga tushirish
