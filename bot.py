import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TG_BOT_API_KEY")

bot = Bot(TOKEN)
dp = Dispatcher()

WEBAPP_URL = "http://localhost:8000/webapp/index.html"

@dp.message(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎮 Открыть приложение",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    await message.answer("🚀 Открой приложение:", reply_markup=kb)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
