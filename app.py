import streamlit as st
from auth import (
    create_users_table, register_user, login_user,
    save_result, get_user_results, load_test_with_data, delete_test, update_test_date
)
from utils import analyze_fit_file  
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json

create_users_table()

# Login / Registration UI
st.title("🏃‍♂️ Conconi Test App")

auth_mode = st.sidebar.radio("Accedi / Registrati", ("Login", "Registrati"))

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if auth_mode == "Registrati":
        if st.sidebar.button("Crea account"):
            if register_user(username, password):
                st.success("Account creato. Ora puoi accedere.")
            else:
                st.error("Username già esistente.")
    else:
        if st.sidebar.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Benvenuto {username}!")
            else:
                st.error("Credenziali errate.")
else:
    st.sidebar.success(f"Accesso come {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Upload e analisi
    uploaded_file = st.file_uploader("📁 Carica file FIT", type=["fit"])
    if uploaded_file:
        result = analyze_fit_file(uploaded_file)
        if "error" in result:
            st.error(result["error"])
        else:
            hr = result["heart_rate"]
            speed = result["speed_threshold"]
            pace = result["pace"]
            st.success(f"Soglia: {hr} bpm - {speed:.2f} m/s - {pace}")

            # Salvataggio dati
            save_result(st.session_state.username, hr, speed, pace, result["heartRate"], result["speed"])

            # Visualizzazione dati
            data = get_user_results(st.session_state.username)
            df = pd.DataFrame(data, columns=["Data", "HR", "Speed", "Pace"])
            df["Data"] = pd.to_datetime(df["Data"])
            st.dataframe(df)

            fig = px.line(df, x="Data", y="HR", title="Andamento soglia FC")
            st.plotly_chart(fig)

            fig2 = px.line(df, x="Data", y="Speed", title="Andamento velocità soglia")
            st.plotly_chart(fig2)

    st.markdown("---")
    st.subheader("📊 Visualizza test precedenti")

    tests = load_test_with_data(st.session_state.username)

    if tests:
        options = [f"{t[1]} – {t[2]} bpm / {t[3]:.2f} m/s" for t in tests]
        selection = st.selectbox("Seleziona un test da visualizzare", options)

        selected_test = tests[options.index(selection)]
        _, timestamp, hr, sp, pace, hr_json, sp_json = selected_test


        # Campo per modificare la data del test selezionato
        st.markdown("### ✏️ Modifica data test selezionato")
        new_date = st.date_input("Nuova data", pd.to_datetime(timestamp).date())

        if st.button("💾 Salva nuova data"):
            new_timestamp = new_date.strftime("%Y-%m-%d") + timestamp[10:]  # conserva ora originale
            update_test_date(st.session_state.username, timestamp, new_timestamp)
            st.success("Data modificata con successo.")
            st.rerun()

        hr_list = json.loads(hr_json)
        sp_list = json.loads(sp_json)

        if hr_list and sp_list:
            fig = go.Figure()

            # Dati HR vs Speed
            fig.add_trace(go.Scatter(
                x=sp_list,
                y=hr_list,
                mode='lines+markers',
                name='HR vs Speed',
                line=dict(color='darkblue')
            ))

            # Linea orizzontale a soglia HR
            fig.add_shape(
                type="line",
                x0=min(sp_list),
                x1=max(sp_list),
                y0=hr,
                y1=hr,
                line=dict(color="red", width=2, dash="dash"),
                name="Soglia FC"
            )

            # Linea verticale a soglia Speed
            fig.add_shape(
                type="line",
                x0=sp,
                x1=sp,
                y0=min(hr_list),
                y1=max(hr_list),
                line=dict(color="green", width=2, dash="dash"),
                name="Soglia Speed"
            )

            # Annotazioni (opzionale)
            fig.add_annotation(
                x=max(sp_list),
                y=hr,
                text="Soglia FC",
                showarrow=False,
                font=dict(color="red", size=12),
                bgcolor="rgba(255,0,0,0.1)",
                xanchor="left",
                yanchor="bottom"
            )
            fig.add_annotation(
                x=sp,
                y=max(hr_list),
                text="Soglia Speed",
                showarrow=False,
                font=dict(color="green", size=12),
                bgcolor="rgba(0,255,0,0.1)",
                xanchor="right",
                yanchor="top"
            )

            fig.update_layout(
                title=f"Test del {timestamp} – Soglia: {hr} bpm @ {sp:.2f} m/s",
                xaxis_title="Velocità (m/s)",
                yaxis_title="Frequenza cardiaca (bpm)",
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nessun dato disponibile per questo test.")

