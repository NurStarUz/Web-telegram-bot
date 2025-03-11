import logging
import json
import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from fastapi import FastAPI
import uvicorn

API_TOKEN = os.getenv("677810027:AAHqD6IwmCUmRfdeskvTOx-0LwLiK-f8RM4")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

app = FastAPI()

# 🔹 Testlarni yuklash
try:
    with open("tests.json", "r", encoding="utf-8") as f:
        tests = json.load(f)
except FileNotFoundError:
    tests = []

user_tests = {}

@app.get("/")
def home():
    return {"message": "Web bot ishlayapti!"}

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("👋 Web botga xush kelibsiz!\n\n📝 Testni boshlash uchun /test buyrug‘ini yuboring.")

@dp.message_handler(commands=['test'])
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

@dp.poll_answer_handler()
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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
# 🔹 Web interfeys uchun testlarni API orqali yuborish
@app.get("/get_questions")
def get_questions():
    return {"questions": tests}
