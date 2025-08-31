import streamlit as st
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json
import numpy as np
from pathlib import Path
import os

from utils import analyze_fit_file, speed_to_pace
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

# ---- Sidebar ----


# Inizializza la variabile di sessione
if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

# Bottone fisso (label sempre uguale)
if st.sidebar.button("Guida"):
    st.session_state.show_guide = not st.session_state.show_guide

# Mostra guida se attivo
if st.session_state.show_guide:
    readme_path = "README.md"
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            guide_content = f.read()
        st.sidebar.markdown(guide_content, unsafe_allow_html=True)
    else:
        st.sidebar.warning("Guida non trovata (README.md mancante).")




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
    uploaded_file = st.file_uploader("Carica file FIT", type=["fit"], key="uploader")
    test_date = st.date_input("📅 Data del test", date.today())

    # Evita duplicati: processa ogni file una sola volta per nome+size
    if uploaded_file is not None:
        file_signature = f"{uploaded_file.name}-{getattr(uploaded_file, 'size', 0)}"
    else:
        file_signature = None

    if uploaded_file and st.session_state.get("last_processed_signature") != file_signature:
        result = analyze_fit_file(uploaded_file)
        if "error" in result:
            st.error(result["error"])
        else:
            hr = result["heart_rate"]
            sp_val = result["speed_threshold"]
            pace = result["pace"]
            ci_low = result["ci_low"]
            ci_high = result["ci_high"]

            st.success(f"🎯 Soglia: **{hr:.1f} bpm** – **{sp_val:.2f} m/s** – **{pace}**")
            if ci_low and ci_high:
                st.info(f"🔹 Intervallo di confidenza: [{ci_low:.2f}, {ci_high:.2f}] m/s")

            # Salva come nuovo record
            save_result(
                st.session_state.username,
                hr,
                sp_val,
                pace,
                result["heartRate"],
                result["speed"],
                custom_date=test_date,
                ci_low=ci_low,
                ci_high=ci_high
            )
            st.session_state["last_processed_signature"] = file_signature
            st.info("✅ Test salvato con successo!")

    # ---- Storico Test ----
    st.markdown("---")
    st.header("📊 Storico Test Conconi")

    tests = load_test_with_data(st.session_state.username)
    if tests:
        # Ordina per data (solo YYYY-MM-DD)
        tests = sorted(tests, key=lambda x: x["timestamp"])
        df = pd.DataFrame(
            [(t["timestamp"][:10], t["heart_rate"], t["speed"], t["pace"]) for t in tests],
            columns=["Data", "HR", "Speed", "Pace"]
        )

        st.dataframe(df, use_container_width=True)

                # ---- Grafici di Trend ----

        # Grafico HR (solo date nel formato gg-mm-aaaa)
        fig = px.line(df, x="Data", y="HR", title="Andamento Soglia FC (bpm)", markers=True)
        fig.update_layout(
            xaxis=dict(
                title="Data",
                tickformat="%d-%m-%Y"  # Formato data senza HH:MM:SS
            ),
            yaxis=dict(title="Frequenza cardiaca (bpm)")
        )
        st.plotly_chart(fig, use_container_width=True)

        # Grafico Pace (mostra mm:ss/km e velocità alta a destra)
        df['Pace_sec'] = df['Pace'].apply(lambda x: int(x.split(":")[0])*60 + int(x.split(":")[1]))
        fig2 = px.line(df, x="Data", y="Pace_sec", title="Andamento Ritmo Soglia", markers=True)

        # Genera tick personalizzati per mm:ss
        max_pace = df["Pace_sec"].max()
        min_pace = df["Pace_sec"].min()
        step = 10 if (max_pace - min_pace) <= 120 else 15 if (max_pace - min_pace) <= 240 else 30
        tickvals = list(range(int(min_pace), int(max_pace) + 1, step))
        ticktext = [f"{v//60:02d}:{v%60:02d}" for v in tickvals]

        fig2.update_layout(
            xaxis=dict(
                title="Data",
                tickformat="%d-%m-%Y"  # Data senza orario
            ),
            yaxis=dict(
                title="Ritmo soglia (mm:ss/km)",
                tickvals=tickvals,
                ticktext=ticktext,
                autorange="reversed"  # Velocità più alta a destra
            )
        )
        st.plotly_chart(fig2, use_container_width=True)


        # Visualizzazione singolo test
        st.subheader("🔍 Visualizza un test")
        options = [f"{t['timestamp'][:10]} – {t['heart_rate']} bpm / {t['speed']:.2f} m/s" for t in tests]
        selection = st.selectbox("Seleziona un test", options, key="select_test")
        selected_test = tests[options.index(selection)]

        timestamp = selected_test["timestamp"]
        hr_val_saved = selected_test["heart_rate"]
        sp_val_saved = selected_test["speed"]
        pace_val_saved = selected_test["pace"]
        hr_json = selected_test.get("hr_array", "[]")
        sp_json = selected_test.get("sp_array", "[]")
        ci_low = selected_test.get("ci_low")
        ci_high = selected_test.get("ci_high")

        # ---- Utility robusta per convertire json/lista ----
        def _to_list(x):
            if isinstance(x, list):
                return x
            if isinstance(x, str):
                try:
                    return json.loads(x)
                except Exception:
                    return []
            return []

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🗑️ Elimina test", use_container_width=True):
                delete_test(st.session_state.username, timestamp)
                st.success("Test eliminato.")
                st.rerun()
        with col2:
            new_date = st.date_input("✏️ Modifica data", pd.to_datetime(timestamp[:10]).date(), key="edit_date")
            if st.button("💾 Salva nuova data", use_container_width=True):
                new_timestamp = new_date.strftime("%Y-%m-%d")
                update_test_date(st.session_state.username, timestamp, new_timestamp)
                st.success("Data modificata.")
                st.rerun()

        # ---- Grafico dettagliato HR vs Pace con soglia + CI ----
        hr_list = _to_list(hr_json)
        sp_list = _to_list(sp_json)

        if hr_list and sp_list and len(hr_list) == len(sp_list):
            # Converti speed -> pace in secondi
            def pace_to_sec(p):
                m, s = p.split(":")
                return int(m) * 60 + int(s)

            pace_sec = [pace_to_sec(speed_to_pace(s)) for s in sp_list]

            # Ordina da lenta (più secondi) a veloce (meno secondi) così la velocità alta resta a destra
            sorted_pairs = sorted(zip(pace_sec, hr_list), key=lambda x: x[0], reverse=True)
            pace_sec_sorted, hr_sorted = map(list, zip(*sorted_pairs))

            # Calcola HR al punto soglia usando il campione più vicino a sp_val_saved
            # (così le linee si incrociano su un punto esistente del grafico)
            try:
                sp_arr = np.array(sp_list, dtype=float)
                hr_arr = np.array(hr_list, dtype=float)
                idx_near = int(np.argmin(np.abs(sp_arr - float(sp_val_saved))))
                hr_cross = float(hr_arr[idx_near])
                threshold_sec = pace_to_sec(speed_to_pace(float(sp_val_saved)))
            except Exception:
                hr_cross = float(hr_val_saved)
                threshold_sec = pace_to_sec(speed_to_pace(float(sp_val_saved)))

            # Figura
            figd = go.Figure()
            figd.add_trace(
                go.Scatter(
                    x=pace_sec_sorted,
                    y=hr_sorted,
                    mode="lines+markers",
                    name="HR vs Pace",
                    line=dict(width=2),
                )
            )

            # Linea orizzontale soglia (passa per il punto campione più vicino)
            figd.add_shape(
                type="line",
                x0=min(pace_sec_sorted), x1=max(pace_sec_sorted),
                y0=hr_cross, y1=hr_cross,
                line=dict(color="red", width=2, dash="dash")
            )

            # Linea verticale soglia (stesso x dell'incrocio)
            figd.add_shape(
                type="line",
                x0=threshold_sec, x1=threshold_sec,
                y0=min(hr_sorted), y1=max(hr_sorted),
                line=dict(color="green", width=2, dash="dash")
            )

            # Marker sul punto di incrocio per evidenziare visivamente
            figd.add_trace(
                go.Scatter(
                    x=[threshold_sec],
                    y=[hr_cross],
                    mode="markers",
                    name="Soglia",
                    marker=dict(size=10, symbol="x")
                )
            )

            # Rettangolo CI (assicuriamoci di usare [min,max] in secondi)
            if ci_low and ci_high:
                try:
                    ci_low_sec = pace_to_sec(speed_to_pace(float(ci_low)))
                    ci_high_sec = pace_to_sec(speed_to_pace(float(ci_high)))
                    x0_ci = min(ci_low_sec, ci_high_sec)
                    x1_ci = max(ci_low_sec, ci_high_sec)
                    figd.add_vrect(
                        x0=x0_ci, x1=x1_ci,
                        fillcolor="red", opacity=0.1, line_width=0,
                        annotation_text="CI 95%", annotation_position="top left"
                    )
                except Exception:
                    pass

            # Tick X meglio distribuiti (10/15/20/30 s a seconda dello span)
            x_min, x_max = min(pace_sec_sorted), max(pace_sec_sorted)
            span = x_max - x_min
            if span > 240:
                step = 30
            elif span > 150:
                step = 20
            elif span > 90:
                step = 15
            else:
                step = 10

            start_tick = int(np.floor(x_min / step) * step)
            end_tick = int(np.ceil(x_max / step) * step)
            tickvals = list(range(start_tick, end_tick + 1, step))
            ticktext = [f"{v//60:02d}:{v%60:02d}" for v in tickvals]

            # Layout (pace crescente a destra -> axis reversed)
            figd.update_layout(
                title=f"Dettagli Test – {timestamp[:10]} | Soglia: {hr_val_saved:.1f} bpm @ {float(sp_val_saved):.2f} m/s ({pace_val_saved})",
                xaxis=dict(
                    title="Pace (mm:ss / km)",
                    tickmode="array",
                    tickvals=tickvals,
                    ticktext=ticktext,
                    autorange="reversed",
                ),
                yaxis_title="Frequenza cardiaca (bpm)",
                height=520
            )
            st.plotly_chart(figd, use_container_width=True)
        else:
            st.warning("Nessun dato dettagliato disponibile.")
    else:
        st.info("Nessun test disponibile. Carica un file FIT per iniziare.")
