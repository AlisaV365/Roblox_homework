import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv

# --- ЗАГРУЗКА .env ---
load_dotenv()

TOKEN = os.getenv("TG_BOT_API_KEY")

if not TOKEN:
    raise ValueError("❌ TG_BOT_API_KEY не найден! Добавь в Railway Variables")

# --- ИНИЦИАЛИЗАЦИЯ ---
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ⚠️ ВАЖНО: сюда вставь свой URL из Railway
WEBAPP_URL = "https://robloxhomework-production.up.railway.app"


# --- МЕНЮ ---
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎮 Открыть игру",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]
    ])


# --- СТАРТ ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "🎮 Это игра домашних дел!\n"
        "Выполняй задания и зарабатывай награды 💎",
        reply_markup=main_menu()
    )


# --- ПОМОЩЬ ---
@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "ℹ️ Команды:\n"
        "/start — открыть игру\n"
        "/help — помощь"
    )


# --- ЛОГ ВСЕХ СООБЩЕНИЙ (для отладки) ---
@dp.message()
async def echo(message: types.Message):
    await message.answer("🤖 Я работаю! Нажми /start")


# --- ЗАПУСК ---
async def main():
    print("🚀 Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
