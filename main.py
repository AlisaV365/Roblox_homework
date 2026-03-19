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

@app.post("/complete/{task_id}")
def complete_task(task_id: int):
    conn = db()
    cur = conn.cursor()

    cur.execute("UPDATE tasks SET status='waiting' WHERE id=?", (task_id,))
    conn.commit()

    return {"status": "waiting"}

# --- DB ---
def db():
    return sqlite3.connect("db.sqlite")


def init_db():
    cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    role TEXT,
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
    status TEXT DEFAULT 'pending',
    photo TEXT
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


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

WEBAPP_URL = "https://robloxhomework-production.up.railway.app/webapp/index.html"


def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎮 Начать игру",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(text="➕ Добавить задание", callback_data="add_task")
        ]
    ])


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "🎮 Готов поиграть?",
        reply_markup=menu()
    )

@dp.callback_query(lambda c: c.data == "add_task")
async def add_task_callback(callback: types.CallbackQuery):
    await callback.message.answer("✏️ Напиши задание так:\n/add Убрать комнату")


    
@dp.message(Command("add"))
async def add_task(message: types.Message):
    text = message.text.replace("/add ", "")

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tasks (title, reward, assigned_to) VALUES (?, ?, ?)",
        (text, 50, message.from_user.id)
    )

    conn.commit()

    await message.answer(f"✅ Задание добавлено: {text}")

# --- RUN BOT ---
@app.on_event("startup")
async def startup():
    print("🚀 Бот запускается...")

    asyncio.create_task(run_bot())


async def run_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

@dp.message(Command("parent"))
async def set_parent(message: types.Message):
    conn = db()
    cur = conn.cursor()

    cur.execute("INSERT OR REPLACE INTO users (user_id, role) VALUES (?, ?)",
                (message.from_user.id, "parent"))
    conn.commit()

    await message.answer("👨 Вы родитель")

@dp.message(Command("child"))
async def set_child(message: types.Message):
    conn = db()
    cur = conn.cursor()

    cur.execute("INSERT OR REPLACE INTO users (user_id, role) VALUES (?, ?)",
                (message.from_user.id, "child"))
    conn.commit()

    await message.answer("👶 Вы ребёнок")

@dp.message(Command("add"))
async def add_task(message: types.Message):
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT role FROM users WHERE user_id=?", (message.from_user.id,))
    role = cur.fetchone()

    if not role or role[0] != "parent":
        await message.answer("❌ Только родитель может добавлять задания")
        return

    text = message.text.replace("/add ", "")

    cur.execute(
        "INSERT INTO tasks (title, reward, assigned_to) VALUES (?, ?, ?)",
        (text, 50, message.from_user.id)
    )

    conn.commit()

    await message.answer(f"✅ Задание создано: {text}")


@app.post("/approve/{task_id}")
def approve_task(task_id: int):
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT reward, assigned_to FROM tasks WHERE id=?", (task_id,))
    task = cur.fetchone()

    if task:
        reward, user_id = task

        cur.execute("UPDATE users SET coins = coins + ?, xp = xp + ? WHERE user_id=?",
                    (reward, reward, user_id))

        cur.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
        conn.commit()

    return {"status": "done"}
