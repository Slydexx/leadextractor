import streamlit as st
import googlemaps
import requests
from bs4 import BeautifulSoup
import pandas as pd
from supabase import create_client

# === CONFIG SUPABASE ===
SUPABASE_URL = "https://gsbfqagtbgafbsdzenxa.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdzYmZxYWd0YmdhZmJzZHplbnhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQzODA4NjYs"
    "ImV4cCI6MjA1OTk1Njg2Nn0."
    "aabjFnBgMagRIWVTBm_MU7hrDq8rJHmSoIc7EVy8-EA"
)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === STREAMLIT CONFIG ===
st.set_page_config(page_title="Lead Extractor", layout="centered")

# === CUSTOM STYLE ===
st.markdown("""
    <style>
        .big-title { font-size: 3em; font-weight: bold; text-align: center; margin-bottom: 0.5em; color:#ff4b4b; }
        .subtitle { font-size: 1.3em; text-align: center; margin-bottom: 1em; color:#333; }
        .benefits { background-color: #f0f8ff; border-radius: 10px; padding: 1em; }
        .cta-button { background-color: #ff4b4b; color: white; padding: 0.8em; border-radius: 8px; font-weight:bold; }
    </style>
""", unsafe_allow_html=True)

# === SESSION INIT ===
for key in ["user_logged_in", "user_email", "ricerche_effettuate", "is_premium"]:
    if key not in st.session_state:
        st.session_state[key] = False if "logged_in" in key else 0 if "ricerche" in key else ""

# === LOGIN / REGISTRATION ===
st.markdown("<div class='big-title'>📍 Lead Extractor</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Trova contatti commerciali da Google Maps in pochi secondi!</div>", unsafe_allow_html=True)

if not st.session_state["user_logged_in"]:
    with st.form("login_form"):
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        azione = st.radio("", ["Login", "Registrati"], horizontal=True)
        if st.form_submit_button("🚀 Entra ora"):
            if email and password:
                try:
                    if azione == "Registrati":
                        res = supabase.auth.sign_up({"email": email, "password": password})
                        st.success("🎉 Registrato! Conferma la tua email prima di accedere.")
                        st.stop()
                    else:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state["user_logged_in"] = True
                        st.session_state["user_email"] = email
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Errore: {e}")
            else:
                st.warning("⚠️ Inserisci tutti i dati")
    st.markdown("""
        <div class="benefits">
            <b>🧪 Versione Demo gratuita:</b><br>
            • 3 ricerche totali<br>
            • Fino a 4 contatti per ricerca<br><br>
            <b>👑 Versione Premium:</b><br>
            • 30 ricerche al mese<br>
            • Fino a 60 contatti per ricerca<br>
            • Esporta CSV completo<br>
            <a href="https://ticalcolo.gumroad.com/l/uqpgo" class="cta-button">🚀 Passa a Premium</a>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# === RECUPERO UTENTE DA DB ===
user_email = st.session_state["user_email"]
try:
    res = supabase.table("user").select("*").eq("email", user_email).single().execute()
    if res.data:
        st.session_state["ricerche_effettuate"] = res.data.get("ricerche_effettuate", 0)
        st.session_state["is_premium"] = res.data.get("premium", False)
    else:
        supabase.table("user").insert({"email": user_email, "premium": False, "ricerche_effettuate": 0}).execute()
except:
    supabase.table("user").insert({"email": user_email, "premium": False, "ricerche_effettuate": 0}).execute()

# === UI LIMITI ===
is_premium = st.session_state["is_premium"]
MAX_RICERCHE = 30 if is_premium else 3
MAX_CONTATTI = 60 if is_premium else 4

st.success(f"👋 Ciao {user_email}! Sei {'Premium 👑' if is_premium else 'Demo 🧪'}")
st.info(f"🔁 Ricerche rimaste: {MAX_RICERCHE - st.session_state['ricerche_effettuate']}")

# === FORM RICERCA ===
gmaps = googlemaps.Client(key="AIzaSyCAaPuraZRkHip3QAT39F-Mi2rHsZjFmQg")
query = st.text_input("🔍 Attività")
location = st.text_input("📍 Località")

if st.button("🔎 Cerca contatti"):
    if query and location:
        st.session_state["ricerche_effettuate"] += 1
        supabase.table("user").update({"ricerche_effettuate": st.session_state["ricerche_effettuate"]}).eq("email", user_email).execute()

        results = gmaps.places(query=f"{query} a {location}").get("results", [])[:MAX_CONTATTI]
        data = []
        for place in results:
            details = gmaps.place(place["place_id"])["result"]
            data.append({
                "Nome": details.get("name"),
                "Indirizzo": details.get("formatted_address", "N/A"),
                "Telefono": details.get("international_phone_number", "N/A"),
                "Sito Web": details.get("website", "N/A"),
            })
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.download_button("📥 Scarica CSV", df.to_csv(index=False).encode("utf-8-sig"), "contatti.csv", "text/csv")
    else:
        st.warning("⚠️ Compila tutti i campi.")
