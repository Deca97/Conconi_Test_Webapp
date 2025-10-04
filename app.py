import streamlit as st
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json
import numpy as np
from pathlib import Path
import os
from transformers import pipeline


from utils import analyze_fit_file, speed_to_pace
from auth import (
    register_user,
    login_user,
    save_result,
    load_test_with_data,
    delete_test,
    update_test_date,
    delete_account               
)



# ===============================
#   CONFIGURAZIONE STREAMLIT
# ===============================
st.set_page_config(
    page_title="Conconi Test App",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===============================
#   LAYOUT INIZIALE MIGLIORATO
# ===============================
st.markdown(
    """
    <div style="text-align:center; margin-bottom:30px;">
        <h1 style="color:#2E86C1; font-size:3em;">🏃‍♂️ Conconi Test Analyzer</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# ===============================
#   INIZIALIZZAZIONE SESSION_STATE
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

# ===============================
#   SIDEBAR: AUTH O ACCOUNT
# ===============================
if st.session_state.logged_in:
    st.sidebar.success(f"Accesso come {st.session_state.username}")

    # Logout
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.delete_step = 0
        st.rerun()

    # Inizializza variabile di sessione per il flusso di eliminazione
    if "delete_step" not in st.session_state:
        st.session_state.delete_step = 0  # 0 = nulla, 1 = conferma visibile

    # Step 0: mostra solo bottone ELIMINA
    if st.session_state.delete_step == 0:
        if st.sidebar.button("🗑️ Elimina account", use_container_width=True):
            st.session_state.delete_step = 1
            st.rerun()

    # Step 1: mostra bottoni CONFERMA o ANNULLA
    elif st.session_state.delete_step == 1:
        st.warning("⚠️ Sei sicuro di voler eliminare l'account? Questa azione è irreversibile!")
        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button("✅ Conferma", use_container_width=True):
                st.write("Eliminando account:", st.session_state.username)
                if delete_account(st.session_state.username):
                    st.success("✅ Account eliminato con successo!")
                    # Reset sessione e ritorno alla home
                    st.session_state.logged_in = False
                    st.session_state.username = ""
                    st.session_state.delete_step = 0
                    st.rerun()
                else:
                    st.error("⚠️ Errore durante la cancellazione dell'account.")

        with col2:
            if st.button("❌ Annulla", use_container_width=True):
                st.session_state.delete_step = 0
                st.rerun()


else:
    # Mostra Auth solo se NON loggato
    # auth_mode = st.sidebar.radio("Accedi / Registrati", ("Login", "Registrati", "Recupera password"))
    auth_mode = st.sidebar.radio("Accedi / Registrati", ("Login", "Registrati"))


    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    # --- REGISTRAZIONE ---
    if auth_mode == "Registrati":
        if st.sidebar.button("Crea account", use_container_width=True):
            if not username or not password:
                st.error("Inserisci username e password.")
            else:
                result, msg = register_user(username, password)
                if result:
                    st.success("✅ Account creato! Ora puoi effettuare il login.")
                else:
                    st.error(msg)

    # --- LOGIN ---
    elif auth_mode == "Login":
        if st.sidebar.button("Login", use_container_width=True):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Credenziali errate.")

    # # --- RECUPERO E RESET PASSWORD ---
    # elif auth_mode == "Recupera password":
    #     st.sidebar.markdown("### Genera token di reset")
    #     if st.sidebar.button("Invia username di reset", use_container_width=True):
    #         if not username:
    #             st.error("Inserisci la tua username.")
    #         else:
    #             ok, msg = generate_reset_token(username)
    #             if ok:
    #                 st.success("📧 Email di reset inviata! Controlla la tua casella di posta.")
    #             else:
    #                 st.error("⚠️ " + msg)

    #     st.sidebar.markdown("---")
    #     st.sidebar.markdown("### Reimposta password")
    #     token = st.sidebar.text_input("Token ricevuto via username")
    #     new_password = st.sidebar.text_input("Nuova password", type="password")
    #     if st.sidebar.button("Reimposta password", use_container_width=True):
    #         if not token or not new_password:
    #             st.error("Inserisci token e nuova password.")
    #         else:
    #             ok, msg = reset_password(token, new_password)
    #             if ok:
    #                 st.success("✅ Password aggiornata con successo! Ora puoi effettuare il login.")
    #             else:
    #                 st.error("⚠️ " + msg)

# ===============================
#   GUIDA A COMPARSA (EXPANDER)
# ===============================
if st.button("Apri/Chiudi Guida 📖"):
    st.session_state.show_guide = not st.session_state.show_guide

if st.session_state.show_guide:
    with st.expander("📖 Guida", expanded=True):
        readme_path = "README.md"
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                guide_content = f.read()
            st.markdown(
                f"<div style='max-height:500px; overflow-y:auto; border:1px solid #ddd; padding:10px'>{guide_content}</div>",
                unsafe_allow_html=True
            )
        else:
            st.warning("Guida non trovata (README.md mancante).")


# ===============================
# UPLOAD & ANALISI FIT
# ===============================
if st.session_state.logged_in:

    st.header("📁 Carica e Analizza un Nuovo Test Conconi")
    uploaded_file = st.file_uploader("Carica file FIT", type=["fit"], key="uploader")
    test_date = st.date_input("📅 Data del test", date.today())

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
            warning = result.get("warning")

            st.success(f"🎯 Soglia: **{hr:.1f} bpm** – **{sp_val:.2f} m/s** – **{pace}**")
            if ci_low and ci_high:
                st.info(f"🔹 Intervallo di confidenza: [{ci_low:.2f}, {ci_high:.2f}] m/s")
            if warning:
                st.warning(f"⚠️ Attenzione: {warning}")

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
        tests = sorted(tests, key=lambda x: x["timestamp"])
        df = pd.DataFrame(
            [(t["timestamp"][:10], t["heart_rate"], t["speed"], t["pace"]) for t in tests],
            columns=["Data", "HR", "Speed", "Pace"]
        )

        st.dataframe(df, use_container_width=True)

        # ---- Grafici di Trend ----
        fig = px.line(df, x="Data", y="HR", title="Andamento Soglia FC (bpm)", markers=True)
        fig.update_layout(
            xaxis=dict(
                title="Data",
                tickformat="%d-%m-%Y"
            ),
            yaxis=dict(title="Frequenza cardiaca (bpm)")
        )
        st.plotly_chart(fig, use_container_width=True)

        df['Pace_sec'] = df['Pace'].apply(lambda x: int(x.split(":")[0])*60 + int(x.split(":")[1]))
        fig2 = px.line(df, x="Data", y="Pace_sec", title="Andamento Ritmo Soglia", markers=True)

        max_pace = df["Pace_sec"].max()
        min_pace = df["Pace_sec"].min()
        step = 10 if (max_pace - min_pace) <= 120 else 15 if (max_pace - min_pace) <= 240 else 30
        tickvals = list(range(int(min_pace), int(max_pace) + 1, step))
        ticktext = [f"{v//60:02d}:{v%60:02d}" for v in tickvals]

        fig2.update_layout(
            xaxis=dict(
                title="Data",
                tickformat="%d-%m-%Y"
            ),
            yaxis=dict(
                title="Ritmo soglia (mm:ss/km)",
                tickvals=tickvals,
                ticktext=ticktext,
                autorange="reversed"
            )
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Visualizzazione singolo test
        st.subheader("🔍 Visualizza un test")
        if tests:
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

            # Funzione per convertire json/lista
            def _to_list(x):
                if isinstance(x, list):
                    return x
                if isinstance(x, str):
                    try:
                        return json.loads(x)
                    except Exception:
                        return []
                return []

            hr_list = _to_list(hr_json)
            sp_list = _to_list(sp_json)

            # Colonne per eliminazione test e modifica data
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

            # Grafico dettagliato HR vs Pace
            if hr_list and sp_list and len(hr_list) == len(sp_list):
                def pace_to_sec(p):
                    m, s = p.split(":")
                    return int(m) * 60 + int(s)
                
                pace_sec = [pace_to_sec(speed_to_pace(s)) for s in sp_list]
                sorted_pairs = sorted(zip(pace_sec, hr_list), key=lambda x: x[0], reverse=True)
                pace_sec_sorted, hr_sorted = map(list, zip(*sorted_pairs))

                # Calcola HR al punto soglia
                try:
                    sp_arr = np.array(sp_list, dtype=float)
                    hr_arr = np.array(hr_list, dtype=float)
                    idx_near = int(np.argmin(np.abs(sp_arr - float(sp_val_saved))))
                    hr_cross = float(hr_arr[idx_near])
                    threshold_sec = pace_to_sec(speed_to_pace(float(sp_val_saved)))
                except Exception:
                    hr_cross = float(hr_val_saved)
                    threshold_sec = pace_to_sec(speed_to_pace(float(sp_val_saved)))

                figd = go.Figure()
                figd.add_trace(go.Scatter(x=pace_sec_sorted, y=hr_sorted, mode="lines+markers", name="HR vs Pace", line=dict(width=2)))
                figd.add_shape(type="line", x0=min(pace_sec_sorted), x1=max(pace_sec_sorted), y0=hr_cross, y1=hr_cross, line=dict(color="red", width=2, dash="dash"))
                figd.add_shape(type="line", x0=threshold_sec, x1=threshold_sec, y0=min(hr_sorted), y1=max(hr_sorted), line=dict(color="green", width=2, dash="dash"))
                figd.add_trace(go.Scatter(x=[threshold_sec], y=[hr_cross], mode="markers", name="Soglia", marker=dict(size=10, symbol="x")))

                # Rettangolo CI
                if ci_low and ci_high:
                    try:
                        ci_low_sec = pace_to_sec(speed_to_pace(float(ci_low)))
                        ci_high_sec = pace_to_sec(speed_to_pace(float(ci_high)))
                        x0_ci, x1_ci = min(ci_low_sec, ci_high_sec), max(ci_low_sec, ci_high_sec)
                        figd.add_vrect(x0=x0_ci, x1=x1_ci, fillcolor="red", opacity=0.1, line_width=0, annotation_text="CI 95%", annotation_position="top left")
                    except Exception:
                        pass

                # Tick X
                x_min, x_max = min(pace_sec_sorted), max(pace_sec_sorted)
                span = x_max - x_min
                step = 30 if span > 240 else 20 if span > 150 else 10
                tickvals = list(range(int(np.floor(x_min / step) * step), int(np.ceil(x_max / step) * step) + 1, step))
                ticktext = [f"{v//60:02d}:{v%60:02d}" for v in tickvals]

                figd.update_layout(
                    title=f"Dettagli Test – {timestamp[:10]} | Soglia: {hr_val_saved:.1f} bpm @ {float(sp_val_saved):.2f} m/s ({pace_val_saved})",
                    xaxis=dict(title="Pace (mm:ss / km)", tickmode="array", tickvals=tickvals, ticktext=ticktext, autorange="reversed"),
                    yaxis_title="Frequenza cardiaca (bpm)",
                    height=520
                )
                st.plotly_chart(figd, use_container_width=True)
            else:
                st.warning("Nessun dato dettagliato disponibile.")
        else:
            st.info("Nessun test disponibile. Carica un file FIT per iniziare.")


        # ===============================
  
        # ===============================
        #   SIDEBAR: CHAT OPEN-SOURCE LEGGERO (POP-UP)
        # ===============================    

        from transformers import pipeline

        # Inizializza il modello solo una volta
        if "chatbot" not in st.session_state:
            st.session_state.chatbot = pipeline(
                "text-generation",
                model="mrm8488/bloom-560m-finetuned-unnatural-instructions",
                device=-1,
                max_new_tokens=150,
                temperature=0.6,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2
            )


        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "cached_answers" not in st.session_state:
            st.session_state.cached_answers = {}

        # ===============================
        # Chat in Pop-up separato
        # ===============================
        with st.expander("💬 Chat con Coach AI (apri/chiudi)", expanded=False):
            
            # Mostra chat salvata
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Input utente
            if prompt := st.chat_input("Fai una domanda sui tuoi test o allenamenti..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Cache per evitare rigenerazioni
                cache_key = f"{timestamp[:10]}_{prompt}"
                if cache_key in st.session_state.cached_answers:
                    answer = st.session_state.cached_answers[cache_key]
                else:
                    # Prompt ottimizzato per modelli leggeri
                    full_prompt = (
                        "You are an expert running coach. Provide concise, actionable advice based on test data. "
                        "Do NOT repeat the test numbers, just interpret them.\n\n"
                        f"Latest Conconi test data:\n"
                        f"- Threshold HR: {hr_val_saved:.1f} bpm\n"
                        f"- Threshold speed: {sp_val_saved:.2f} m/s\n"
                        f"- Threshold pace: {pace_val_saved}\n\n"
                        f"User question: {prompt}\n"
                        "Answer in one or two short sentences, clear and practical."
                    )

                    try:
                        output = st.session_state.chatbot(full_prompt)
                        answer = output[0]["generated_text"].replace(full_prompt, "").strip()
                        st.session_state.cached_answers[cache_key] = answer
                    except Exception as e:
                        answer = f"⚠️ Model generation error: {str(e)}"

                st.session_state.messages.append({"role": "assistant", "content": answer})
                with st.chat_message("assistant"):
                    st.markdown(answer)

