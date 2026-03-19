  File "/app/.venv/lib/python3.13/site-packages/click/core.py", line 824, in invoke
    return callback(*args, **kwargs)
    run(
    ~~~^
        app,
        ^^^^
    ...<47 lines>...
        h11_max_incomplete_event_size=h11_max_incomplete_event_size,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
  File "/app/.venv/lib/python3.13/site-packages/uvicorn/config.py", line 441, in load
  File "/app/.venv/lib/python3.13/site-packages/uvicorn/main.py", line 606, in run
    server.run()
    ~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/uvicorn/server.py", line 75, in run
    return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
  File "/mise/installs/python/3.13.12/lib/python3.13/asyncio/runners.py", line 195, in run
    return runner.run(main)
  File "/mise/installs/python/3.13.12/lib/python3.13/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/mise/installs/python/3.13.12/lib/python3.13/asyncio/base_events.py", line 725, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/uvicorn/server.py", line 79, in serve
  File "/app/.venv/lib/python3.13/site-packages/uvicorn/server.py", line 86, in _serve
    config.load()
    ~~~~~~~~~~~^^
  File "/app/main.py", line 146
    await dp.start_polling(bot)0
                               ^
SyntaxError: invalid syntax
    module = importlib.import_module(module_str)
  File "/mise/installs/python/3.13.12/lib/python3.13/importlib/__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1019, in exec_module
  File "<frozen importlib._bootstrap_external>", line 1087, in source_to_code
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
    ~~~^
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
        ^^^^
    ...<47 lines>...
    return ctx.invoke(self.callback, **ctx.params)
           ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.13/site-packages/click/core.py", line 824, in invoke
    return callback(*args, **kwargs)
  File "/app/.venv/lib/python3.13/site-packages/uvicorn/main.py", line 433, in main
Traceback (most recent call last):
  File "/app/.venv/lib/python3.13/site-packages/click/core.py", line 1485, in __call__
    return self.main(*args, **kwargs)
           ~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.13/site-packages/uvicorn/main.py", line 606, in run
    server.run()
  File "/app/.venv/lib/python3.13/site-packages/uvicorn/server.py", line 75, in run
    return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
  File "/mise/installs/python/3.13.12/lib/python3.13/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
    return future.result()
           ~~~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/uvicorn/server.py", line 79, in serve
    await self._serve(sockets)
  File "/app/.venv/lib/python3.13/site-packages/uvicorn/server.py", line 86, in _serve
    ~~~~~~~~~~~^^
  File "/app/.venv/lib/python3.13/site-packages/uvicorn/config.py", line 441, in load
    self.loaded_app = import_from_string(self.app)
  File "/app/main.py", line 146
SyntaxError: invalid syntax
  File "<frozen importlib._bootstrap_external>", line 1157, in get_code
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked



main.py^: from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import random
import os
import asyncio

# --- TELEGRAM ---
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("TG_BOT_API_KEY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- FASTAPI ---
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBAPP_DIR = os.path.join(BASE_DIR, "webapp")


# --- БАЗА ---
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
        xp INTEGER DEFAULT 0,
        avatar TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        reward INTEGER,
        status TEXT DEFAULT 'pending',
        assigned_to INTEGER
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


@app.get("/profile/{user_id}")
def profile(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT coins, level, xp, avatar FROM users WHERE user_id=?", (user_id,))
    u = cur.fetchone()

    if not u:
        cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return {"coins": 0, "level": 1, "xp": 0, "avatar": "🧍"}

    return {
        "coins": u[0],
        "level": u[1],
        "xp": u[2],
        "avatar": u[3] or "🧍"
    }


@app.post("/chest/{user_id}")
def open_chest(user_id: int):
    reward = random.randint(10, 50)

    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (reward, user_id))
    conn.commit()

    return {"reward": reward}


# --- WEBAPP ---
app.mount("/webapp", StaticFiles(directory=WEBAPP_DIR, html=True), name="webapp")


@app.get("/")
def root():
    return FileResponse(os.path.join(WEBAPP_DIR, "index.html"))


# --- TELEGRAM BOT ---
WEBAPP_URL = "https://robloxhomework-production.up.railway.app/webapp/index.html"


def main_menu():
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
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "🎮 Это игра домашних дел!\n"
        "Выполняй задания и зарабатывай награды 💎",
        reply_markup=main_menu()
    )


# --- ЗАПУСК БОТА ВМЕСТЕ С API ---
@app.on_event("startup")
async def start_bot():
    print("🚀 Бот запускается...")

    asyncio.create_task(run_bot())

Ну 
async def run_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)0


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        coins INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        xp INTEGER DEFAULT 0,
        avatar TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        reward INTEGER,
        status TEXT DEFAULT 'pending',
        assigned_to INTEGER
    )
    """)

    conn.commit()
    conn.close()
