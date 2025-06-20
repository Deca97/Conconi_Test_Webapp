import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

import os
DB_PATH = "users.db"

def get_conn():
    return sqlite3.connect("users.db", check_same_thread=False)

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

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                     (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                (username, hash_password(password)))
    data = cur.fetchone()
    conn.close()
    return data is not None

import json

def save_result(username, hr, speed, pace, hr_list=None, sp_list=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO results (username, timestamp, heart_rate, speed, pace, hr_array, sp_array)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, timestamp, hr, speed, pace,
          json.dumps(hr_list or []), json.dumps(sp_list or [])))
    conn.commit()
    conn.close()

def get_user_results(username):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT timestamp, heart_rate, speed, pace FROM results WHERE username=? ORDER BY timestamp ASC", (username,))
    data = cur.fetchall()
    conn.close()
    return data

def load_test_with_data(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, heart_rate, speed, pace, hr_array, sp_array
        FROM results
        WHERE username = ?
        ORDER BY timestamp DESC
    """, (username,))
    results = cursor.fetchall()
    conn.close()
    return results

def delete_test(username, timestamp):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM results
        WHERE username = ? AND timestamp = ?
    """, (username, timestamp))
    conn.commit()
    conn.close()

def update_test_date(username, old_timestamp, new_timestamp):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE results
        SET timestamp = ?
        WHERE username = ? AND timestamp = ?
    """, (new_timestamp, username, old_timestamp))
    conn.commit()
    conn.close()
