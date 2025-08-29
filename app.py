import streamlit as st
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json
from utils import analyze_fit_file
from auth import (
    register_user,
    login_user,
    save_result,
    load_test_with_data,
    delete_test,
    update_test_date,
)

# ---- Config Streamlit ----
st.set_page_config(page_title="Conconi Test App", layout="wide")
st.title("🏃‍♂️ Conconi Test Analyzer")

# ---- Auth ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

auth_mode = st.sidebar.radio("Accedi / Registrati", ("Login", "Registrati"))

if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if auth_mode == "Registrati":
        if st.sidebar.button("Crea account", use_container_width=True):
            if not username or not password:
                st.error("Inserisci username e password.")
            elif register_user(username, password):
                st.success("✅ Account creato. Ora puoi effettuare il login.")
            else:
                st.error("⚠️ Username già esistente.")
    else:
        if st.sidebar.button("Login", use_container_width=True):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Credenziali errate.")
else:
    st.sidebar.success(f"Accesso come {st.session_state.username}")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # ---- Upload & Analisi FIT ----
    st.header("📁 Carica e Analizza un Nuovo Test Conconi")
    uploaded_file = st.file_uploader("Carica file FIT", type=["fit"])
    test_date = st.date_input("📅 Data del test", date.today())

    if uploaded_file and "file_uploaded" not in st.session_state:
        st.session_state.file_uploaded = True  # evita caricamenti multipli
        result = analyze_fit_file(uploaded_file)
        if "error" in result:
            st.error(result["error"])
            st.session_state.file_uploaded = False
        else:
            hr = result["heart_rate"]
            speed = result["speed_threshold"]
            pace = result["pace"]

            st.success(f"🎯 Soglia: **{hr} bpm** – **{speed:.2f} m/s** – **{pace}**")

            save_result(
                st.session_state.username,
                hr,
                speed,
                pace,
                result["heartRate"],
                result["speed"],
                custom_date=test_date,
            )
            st.info("✅ Test salvato con successo!")

    # ---- Storico Test ----
    st.markdown("---")
    st.header("📊 Storico Test Conconi")

    tests = load_test_with_data(st.session_state.username)
    if tests:
        # Ordina per timestamp
        tests = sorted(tests, key=lambda x: x["timestamp"])
        df = pd.DataFrame(
            [(t["timestamp"], t["heart_rate"], t["speed"], t["pace"]) for t in tests],
            columns=["Data", "HR", "Speed", "Pace"],
        )
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        st.dataframe(df, use_container_width=True)

        # Grafici trend
        fig = px.line(df, x="Data", y="HR", title="Andamento Soglia FC (bpm)", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        fig2 = px.line(df, x="Data", y="Speed", title="Andamento Velocità Soglia (m/s)", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

        # Selezione test
        st.subheader("🔍 Visualizza un test")
        options = [f"{t['timestamp']} – {t['heart_rate']} bpm / {t['speed']:.2f} m/s" for t in tests]
        selection = st.selectbox("Seleziona un test", options)
        selected_test = tests[options.index(selection)]

        timestamp = selected_test["timestamp"]
        hr_val = selected_test["heart_rate"]
        sp_val = selected_test["speed"]
        pace_val = selected_test["pace"]
        hr_json = selected_test.get("hr_array", "[]")
        sp_json = selected_test.get("sp_array", "[]")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🗑️ Elimina test", use_container_width=True):
                delete_test(st.session_state.username, timestamp)
                st.success("Test eliminato.")
                st.rerun()
        with col2:
            new_date = st.date_input("✏️ Modifica data", pd.to_datetime(timestamp).date(), key="edit_date")
            if st.button("💾 Salva nuova data", use_container_width=True):
                suffix = timestamp[10:] if len(timestamp) > 10 else " 00:00:00"
                new_timestamp = new_date.strftime("%Y-%m-%d") + suffix
                update_test_date(st.session_state.username, timestamp, new_timestamp)
                st.success("Data modificata.")
                st.rerun()

        # Grafico dettagliato HR vs Speed
        hr_list = json.loads(hr_json)
        sp_list = json.loads(sp_json)
        if hr_list and sp_list and len(hr_list) == len(sp_list):
            figd = go.Figure()
            figd.add_trace(
                go.Scatter(
                    x=sp_list,
                    y=hr_list,
                    mode="lines+markers",
                    name="HR vs Speed",
                    line=dict(width=2),
                )
            )
            figd.add_shape(type="line", x0=sp_val, x1=sp_val, y0=min(hr_list), y1=max(hr_list),
                           line=dict(color="green", width=2, dash="dash"))
            figd.add_shape(type="line", x0=min(sp_list), x1=max(sp_list), y0=hr_val, y1=hr_val,
                           line=dict(color="red", width=2, dash="dash"))
            figd.update_layout(
                title=f"Dettagli Test – {timestamp} | Soglia: {hr_val} bpm @ {sp_val:.2f} m/s ({pace_val})",
                xaxis_title="Velocità (m/s)",
                yaxis_title="Frequenza cardiaca (bpm)",
                height=520,
            )
            st.plotly_chart(figd, use_container_width=True)
        else:
            st.warning("Nessun dato dettagliato disponibile.")
    else:
        st.info("Nessun test disponibile. Carica un file FIT per iniziare.")
