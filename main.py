from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import random
import os

def init_db():
    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()

    # таблица пользователей
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        coins INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        xp INTEGER DEFAULT 0,
        avatar TEXT
    )
    """)

    # таблица заданий
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
    
app = FastAPI()
init_db()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- ПРОВЕРКА ПАПКИ ---
WEBAPP_DIR = os.path.join(BASE_DIR, "webapp")

if not os.path.exists(WEBAPP_DIR):
    print("❌ Папка webapp НЕ найдена!")
else:
    print("✅ Папка webapp найдена:", WEBAPP_DIR)


# --- БАЗА ---
def db():
    return sqlite3.connect("db.sqlite")


# --- ЗАДАНИЯ ---
@app.get("/tasks/{user_id}")
def get_tasks(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, reward, status FROM tasks WHERE assigned_to=?", (user_id,))
    return cur.fetchall()


# --- ПРОФИЛЬ ---
@app.get("/profile/{user_id}")
def profile(user_id: int):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT coins, level, xp, avatar FROM users WHERE user_id=?", (user_id,))
    u = cur.fetchone()

    return {
        "coins": u[0],
        "level": u[1],
        "xp": u[2],
        "avatar": u[3] or "🧍"
    }


# --- СУНДУК ---
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


# --- ROOT ---
@app.get("/")
def root():
    return FileResponse(os.path.join(WEBAPP_DIR, "index.html"))
