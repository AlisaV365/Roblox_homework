from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import random
import os
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# --- TOKEN ---
TOKEN = os.getenv("TG_BOT_API_KEY")

if not TOKEN:
    raise ValueError("❌ TG_BOT_API_KEY не найден")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- APP ---
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBAPP_DIR = os.path.join(BASE_DIR, "webapp")

# --- DB ---
def db():
    return sqlite3.connect("db.sqlite")


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        coins INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        xp INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        reward INTEGER,
        assigned_to INTEGER,
        status TEXT DEFAULT 'pending'
    )
    """)

    conn.commit()
    conn.close()


init_db()

# --- API ---
@app.get("/tasks/{user_id}")
def get_tasks(user_id: int):
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT id, title, reward, status FROM tasks WHERE assigned_to=?", (user_id,))
    return cur.fetchall()


@app.get("/add_test/{user_id}")
def add_test(user_id: int):
    conn = db()
    cur = conn.cursor()

    cur.execute("INSERT INTO tasks (title, reward, assigned_to) VALUES (?, ?, ?)",
                ("Убрать комнату", 50, user_id))

    cur.execute("INSERT INTO tasks (title, reward, assigned_to) VALUES (?, ?, ?)",
                ("Покормить кота", 30, user_id))

    conn.commit()
    return {"ok": True}


# --- WEBAPP ---
app.mount("/webapp", StaticFiles(directory=WEBAPP_DIR, html=True), name="webapp")


@app.get("/")
def root():
    return FileResponse(os.path.join(WEBAPP_DIR, "index.html"))


# --- TELEGRAM ---
WEBAPP_URL = "https://robloxhomework-production.up.railway.app/webapp/index.html"


def menu():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎮 Открыть игру",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]
    ])


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Привет!\n🎮 Открой игру ниже:",
        reply_markup=menu()
    )


# --- RUN BOT ---
@app.on_event("startup")
async def startup():
    print("🚀 Бот запускается...")

    asyncio.create_task(run_bot())


async def run_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
