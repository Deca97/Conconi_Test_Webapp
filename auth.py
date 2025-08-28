# auth.py
import sqlite3
import bcrypt
import json
from datetime import datetime

DB_PATH = "users.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# ---- Creazione tabelle ----
def create_users_table():
    conn = get_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            heart_rate REAL NOT NULL,
            speed REAL NOT NULL,
            pace TEXT NOT NULL,
            hr_array TEXT,
            sp_array TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ---- Registrazione / Login ----
def register_user(username, password):
    conn = get_conn()
    try:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username=?", (username,))
    data = cur.fetchone()
    conn.close()
    if data and bcrypt.checkpw(password.encode(), data[0]):
        return True
    return False

# ---- Salvataggio test ----
def save_result(username, hr, speed, pace, hr_list=None, sp_list=None, custom_date=None):
    conn = get_conn()
    cursor = conn.cursor()
    timestamp = custom_date.strftime("%Y-%m-%d %H:%M:%S") if custom_date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO results (username, timestamp, heart_rate, speed, pace, hr_array, sp_array)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, timestamp, hr, speed, pace,
          json.dumps(hr_list or []), json.dumps(sp_list or [])))
    conn.commit()
    conn.close()

# ---- Caricamento storico test ----
def load_test_with_data(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM results WHERE username=? ORDER BY timestamp
    """, (username,))
    data = cur.fetchall()
    conn.close()
    return data

# ---- Eliminazione test ----
def delete_test(username, timestamp):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM results WHERE username=? AND timestamp=?
    """, (username, timestamp))
    conn.commit()
    conn.close()

# ---- Aggiornamento data test ----
def update_test_date(username, old_timestamp, new_timestamp):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE results SET timestamp=? WHERE username=? AND timestamp=?
    """, (new_timestamp, username, old_timestamp))
    conn.commit()
    conn.close()
