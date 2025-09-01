from supabase import create_client
import bcrypt
import json
import re
from datetime import datetime
from secrets import token_urlsafe
import smtplib


# Configurazione Supabase
SUPABASE_URL = "https://gzvjntyijmvtrvntfxqv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6dmpudHlpam12dHJ2bnRmeHF2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY0MjM0MDUsImV4cCI6MjA3MTk5OTQwNX0.kDXNnBoDdJAh4Zlikp5oxi8JTv_kOTtaKbQs09_W6fw"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===============================
#   UTILS
# ===============================
def check_password_strength(password: str):
    """
    Controlla che la password sia robusta:
    - Minimo 8 caratteri
    - Almeno 1 numero
    - Almeno 1 lettera maiuscola
    """
    if len(password) < 8:
        return False, "La password deve avere almeno 8 caratteri"
    if not re.search(r"[0-9]", password):
        return False, "La password deve contenere almeno un numero"
    if not re.search(r"[A-Z]", password):
        return False, "La password deve contenere almeno una lettera maiuscola"
    return True, None

# ===============================
#   AUTENTICAZIONE
# ===============================
def register_user(username, password):
    """Registra un nuovo utente usando l'username"""
    # Verifica robustezza password
    valid, error = check_password_strength(password)
    if not valid:
        return False, error

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    existing = supabase.table("users").select("*").eq("username", username).execute()
    if existing.data and len(existing.data) > 0:
        return False, "username già registrata"
    
    supabase.table("users").insert({"username": username, "password": hashed}).execute()
    return True, "Registrazione completata"

def login_user(username, password):
    """Login con username e password"""
    resp = supabase.table("users").select("*").eq("username", username).execute()
    if resp.data and len(resp.data) > 0:
        hashed = resp.data[0]["password"].encode()
        if bcrypt.checkpw(password.encode(), hashed):
            return True
        return False
    return False

# # ===============================
# #   RESET PASSWORD
# # ===============================
# def generate_reset_token(username):
#     """
#     Genera un token univoco per il reset password, lo salva nel DB
#     e invia un'username all'utente con il link per resettare la password.
#     """
#     # Verifica che l'utente esista
#     resp = supabase.table("users").select("*").eq("username", username).execute()
#     if not resp.data or len(resp.data) == 0:
#         return False, "Utente non trovato"
    
#     # Genera token casuale
#     token = token_urlsafe(32)

#     # Salva il token nel DB
#     supabase.table("users").update({"reset_token": token}).eq("username", username).execute()

#     # --- INVIO username ---
#     try:
#         msg = usernameMessage()
#         msg['Subject'] = "Reset Password – Conconi Test App"
#         msg['From'] = "tua.username@gmail.com"  # Da modificare con la tua username
#         msg['To'] = username
#         reset_link = f"https://tua-app/reset-password?token={token}"
#         msg.set_content(f"Ciao!\n\nPer resettare la tua password clicca il link qui sotto:\n{reset_link}\n\nSe non hai richiesto il reset, ignora questa username.")

#         # Connessione SMTP
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
#             smtp.login("tua.username@gmail.com", "LA_TUA_PASSWORD_APP")
#             smtp.send_message(msg)

#         return True, "username inviata con successo!"
#     except Exception as e:
#         return False, f"Errore nell'invio dell'username: {str(e)}"

# def reset_password(token, new_password):
#     """Reimposta la password usando un token valido"""
#     valid, error = check_password_strength(new_password)
#     if not valid:
#         return False, error

#     resp = supabase.table("users").select("*").eq("reset_token", token).execute()
#     if not resp.data or len(resp.data) == 0:
#         return False, "Token non valido o scaduto"

#     username = resp.data[0]["username"]
#     hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
#     supabase.table("users").update({"password": hashed, "reset_token": None}).eq("username", username).execute()
#     return True, "Password aggiornata con successo"

# ===============================
#   CANCELLAZIONE ACCOUNT
# ===============================
def delete_account(username):
    """Elimina definitivamente un account e tutti i suoi dati"""
    try:
        # Elimina utente
        resp_user = supabase.table("users").delete().eq("username", username).execute()
        print("Resp user:", resp_user)
        if not resp_user.data:
            print("Nessun utente trovato da eliminare")
            return False

        # Elimina risultati
        resp_results = supabase.table("results").delete().eq("username", username).execute()
        print("Resp results:", resp_results)
        # Qui anche se non ci sono risultati va bene, non deve fallire

        return True
    except Exception as e:
        print("Errore delete_account:", e)
        return False



# ===============================
#   GESTIONE RISULTATI
# ===============================
def save_result(username, hr, speed, pace, hr_list=None, sp_list=None,
                custom_date=None, ci_low=None, ci_high=None):
    """Salva un test Conconi per l'utente"""
    timestamp = custom_date.strftime("%Y-%m-%d") if custom_date else datetime.now().strftime("%Y-%m-%d")
    supabase.table("results").insert({
        "username": username,
        "timestamp": timestamp,
        "heart_rate": hr,
        "speed": speed,
        "pace": pace,
        "hr_array": json.dumps(hr_list or []),
        "sp_array": json.dumps(sp_list or []),
        "ci_low": ci_low,
        "ci_high": ci_high
    }).execute()

def load_test_with_data(username):
    """Recupera tutti i test dell'utente"""
    resp = supabase.table("results").select("*").eq("username", username).order("timestamp").execute()
    return resp.data or []

def delete_test(username, timestamp):
    """Elimina un test specifico"""
    supabase.table("results").delete().eq("username", username).eq("timestamp", timestamp).execute()

def update_test_date(username, old_ts, new_ts):
    """Aggiorna la data di un test"""
    supabase.table("results").update({"timestamp": new_ts}).eq("username", username).eq("timestamp", old_ts).execute()
