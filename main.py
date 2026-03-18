from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import sqlite3
import random
from datetime import datetime

app = FastAPI()

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


# --- WEBAPP (ОЧЕНЬ ВАЖНО) ---
app.mount("/webapp", StaticFiles(directory="webapp", html=True), name="webapp")
