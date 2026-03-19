from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import os
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = os.getenv("TG_BOT_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBAPP_DIR = os.path.join(BASE_DIR, "webapp")


def db():
    return sqlite3.connect("db.sqlite")


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        role TEXT,
        coins INTEGER DEFAULT 0
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


@app.get("/tasks/{user_id}")
def get_tasks(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, reward, status FROM tasks WHERE assigned_to=?", (user_id,))
    return cur.fetchall()


@app.post("/complete/{task_id}")
def complete_task(task_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
    conn.commit()
    return {"ok": True}


app.mount("/webapp", StaticFiles(directory=WEBAPP_DIR, html=True), name="webapp")


@app.get("/")
def root():
    return FileResponse(os.path.join(WEBAPP_DIR, "index.html"))


WEBAPP_URL = "https://robloxhomework-production.up.railway.app/webapp/index.html"


def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Начать игру", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Привет! Нажми кнопку ниже 👇", reply_markup=menu())


@dp.message(Command("add"))
async def add_task(message: types.Message):
    text = message.text.replace("/add ", "")

    conn = db()
    cur = conn.cursor()

    cur.execute("INSERT INTO tasks (title, reward, assigned_to) VALUES (?, ?, ?)",
                (text, 50, message.from_user.id))

    conn.commit()

    await message.answer("✅ Задание добавлено")


@app.on_event("startup")
async def startup():
    asyncio.create_task(run_bot())


async def run_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
