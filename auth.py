from supabase import create_client
import bcrypt
import json
from datetime import datetime

SUPABASE_URL = "https://gzvjntyijmvtrvntfxqv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6dmpudHlpam12dHJ2bnRmeHF2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY0MjM0MDUsImV4cCI6MjA3MTk5OTQwNX0.kDXNnBoDdJAh4Zlikp5oxi8JTv_kOTtaKbQs09_W6fw"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def register_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    existing = supabase.table("users").select("*").eq("username", username).execute()
    if existing.data:
        return False
    supabase.table("users").insert({"username": username, "password": hashed}).execute()
    return True

def login_user(username, password):
    resp = supabase.table("users").select("*").eq("username", username).execute()
    if resp.data:
        hashed = resp.data[0]["password"].encode()
        return bcrypt.checkpw(password.encode(), hashed)
    return False

def save_result(username, hr, speed, pace, hr_list=None, sp_list=None, custom_date=None):
    timestamp = (custom_date.strftime("%Y-%m-%d %H:%M:%S")
                 if custom_date else datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    supabase.table("results").insert({
        "username": username,
        "timestamp": timestamp,
        "heart_rate": hr,
        "speed": speed,
        "pace": pace,
        "hr_array": json.dumps(hr_list or []),
        "sp_array": json.dumps(sp_list or [])
    }).execute()

def load_test_with_data(username):
    resp = supabase.table("results").select("*").eq("username", username).execute()
    return resp.data or []

def delete_test(username, timestamp):
    supabase.table("results").delete().eq("username", username).eq("timestamp", timestamp).execute()

def update_test_date(username, old_ts, new_ts):
    supabase.table("results").update({"timestamp": new_ts}).eq("username", username).eq("timestamp", old_ts).execute()
