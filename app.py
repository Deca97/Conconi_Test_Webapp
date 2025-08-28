# app.py
import streamlit as st
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json
import sqlite3
import os

from auth import (
    create_users_table,
    register_user,
    login_user,
    save_result,
    load_test_with_data,
    delete_test,
    update_test_date,
)
from utils import analyze_fit_file

# ---- Config app ----
st.set_page_config(page_title="Conconi Test App", layout="wide")
create_users_table()

st.title("🏃‍♂️ Conconi Test Analyzer")

# ---- Auth ----
auth_mode = st.sidebar.radio("Accedi / Registrati", ("Login", "Registrati"))

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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

    # ---- Upload file FIT ----
    st.header("📁 Carica e Analizza un Nuovo Test Conconi")
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None

    uploaded_file = st.file_uploader(
        "Carica file FIT", type=["fit"], key="fit_uploader"
    )

    test_date = st.date_input("📅 Data del test", date.today())

    if uploaded_file and uploaded_file != st.session_state.uploaded_file:
        # Analizza solo se è un nuovo file
        st.session_state.uploaded_file = uploaded_file
        result = analyze_fit_file(uploaded_file)

        if "error" in result:
            st.error(result["error"])
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

    # ---- Storico test ----
    st.markdown("---")
    st.header("📊 Storico Test Conconi")

    tests = load_test_with_data(st.session_state.username)

    if tests:
        # Creazione DataFrame
        df = pd.DataFrame(
            [
                (t[2], t[3], t[4], t[5])
                for t in tests
            ],
            columns=["Data", "HR", "Speed", "Pace"]
        )
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df = df.sort_values("Data")
        st.dataframe(df, use_container_width=True)

        # Grafici trend
        st.plotly_chart(
            px.line(df, x="Data", y="HR", title="Andamento Soglia FC (bpm)", markers=True),
            use_container_width=True
        )
        st.plotly_chart(
            px.line(df, x="Data", y="Speed", title="Andamento Velocità Soglia (m/s)", markers=True),
            use_container_width=True
        )

        # Selezione test per dettagli
        st.subheader("🔍 Visualizza un test")
        options = [
            f"{t[2]} – {t[3]} bpm / {t[4]:.2f} m/s"
            for t in tests
        ]
        selection_index = st.selectbox("Seleziona un test", range(len(options)), format_func=lambda x: options[x])

        selected_test = tests[selection_index]
        _, _, timestamp, hr, sp, pace, hr_json, sp_json = selected_test

        # Colonne per pulsanti
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("🗑️ Elimina test"):
                delete_test(st.session_state.username, timestamp)
                st.success("Test eliminato")
                st.session_state.uploaded_file = None
                st.rerun()

        with col2:
            new_date = st.date_input("✏️ Modifica data test", pd.to_datetime(timestamp).date(), key="edit_date")
            if st.button("💾 Salva nuova data"):
                suffix = timestamp[10:] if len(timestamp) > 10 else " 00:00:00"
                new_timestamp = new_date.strftime("%Y-%m-%d") + suffix
                update_test_date(st.session_state.username, timestamp, new_timestamp)
                st.success("Data modificata")
                st.rerun()

        # Grafico HR vs Speed
        hr_list = json.loads(hr_json) if hr_json else []
        sp_list = json.loads(sp_json) if sp_json else []

        if hr_list and sp_list and len(hr_list) == len(sp_list):
            figd = go.Figure()
            figd.add_trace(
                go.Scatter(
                    x=sp_list, y=hr_list, mode="lines+markers", name="HR vs Speed"
                )
            )
            figd.add_shape(
                type="line", x0=sp, x1=sp, y0=min(hr_list), y1=max(hr_list),
                line=dict(color="green", width=2, dash="dash")
            )
            figd.add_shape(
                type="line", x0=min(sp_list), x1=max(sp_list), y0=hr, y1=hr,
                line=dict(color="red", width=2, dash="dash")
            )
            figd.update_layout(
                title=f"Dettagli Test – {timestamp} | Soglia: {hr} bpm @ {sp:.2f} m/s ({pace})",
                xaxis_title="Velocità (m/s)",
                yaxis_title="Frequenza cardiaca (bpm)",
                height=520
            )
            st.plotly_chart(figd, use_container_width=True)
        else:
            st.warning("Nessun dato dettagliato disponibile per questo test.")
    else:
        st.info("Nessun test disponibile. Carica un file FIT per iniziare.")
