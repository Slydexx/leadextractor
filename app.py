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

# === STILE PERSONALIZZATO ===
st.markdown("""
    <style>
        .big-title {
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0.5em;
        }
        .subtitle {
            font-size: 1.2em;
            text-align: center;
            margin-bottom: 2em;
            color: #555;
        }
        .benefits {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 1.5em;
            font-size: 1.05em;
        }
        .cta-button {
            display: block;
            text-align: center;
            margin-top: 2em;
        }
        .form-container {
            padding-top: 30px;
        }
        .error {
            color: red;
            font-size: 1.1em;
        }
        .btn-login {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            font-size: 1.2em;
            border: none;
            cursor: pointer;
        }
        .btn-login:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)

# === SESSION INIT ===
if "user_logged_in" not in st.session_state:
    st.session_state["user_logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""
if "ricerche_effettuate" not in st.session_state:
    st.session_state["ricerche_effettuate"] = 0
if "is_premium" not in st.session_state:
    st.session_state["is_premium"] = False
if "just_upgraded" not in st.session_state:
    st.session_state["just_upgraded"] = False

# === LOGIN / REGISTRAZIONE ===
st.markdown("<div class='big-title'>📍 Lead Extractor</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Benvenuto! Accedi per iniziare a estrarre contatti da Google Maps.</div>", unsafe_allow_html=True)

if not st.session_state["user_logged_in"]:
    with st.form(key="login_form", clear_on_submit=True):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        azione = st.radio("Accedi o Registrati", ["Login", "Registrati"], horizontal=True)

        submit_button = st.form_submit_button("Continua")
        
        if submit_button:
            if email and password:
                try:
                    if azione == "Registrati":
                        res = supabase.auth.sign_up({"email": email, "password": password})
                        if res.user:
                            st.success("✅ Registrazione avvenuta! Controlla la tua email per confermare.")
                            st.stop()
                    else:
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        if res.session:
                            st.session_state["user_logged_in"] = True
                            st.session_state["user_email"] = email
                            st.rerun()
                        else:
                            st.error("❌ Login fallito. Verifica le credenziali o conferma la mail.")
                except Exception as e:
                    st.error(f"Errore: {e}")
            else:
                st.warning("Compila tutti i campi.")
    st.stop()

# === MESSAGGIO DI CONFERMA PREMIUM ===
if st.session_state["just_upgraded"]:
    st.success("🎉 Accesso Premium attivato! Puoi iniziare a usare tutte le funzionalità.")
    st.session_state["just_upgraded"] = False

# === RECUPERO STATO UTENTE ===
user_email = st.session_state["user_email"]
res = supabase.table("user").select("*").eq("email", user_email).single().execute()

if res.data:
    user_data = res.data
    st.session_state["ricerche_effettuate"] = user_data.get("ricerche_effettuate", 0)
    st.session_state["is_premium"] = user_data.get("premium", False)
else:
    supabase.table("user").insert({
        "email": user_email,
        "premium": False,
        "ricerche_effettuate": 0
    }).execute()

# === UI PREMIUM BADGE + LIMITI ===
is_premium = st.session_state["is_premium"]
MAX_RICERCHE = 30 if is_premium else 3
MAX_CONTATTI = 60 if is_premium else 4

col1, col2 = st.columns([0.7, 0.3])
with col1:
    st.markdown(f"👋 Ciao **{user_email}**")
with col2:
    st.markdown(
        f"<div style='text-align:right;'>{'👑 <b>Premium</b>' if is_premium else '🧪 <b>Demo</b>'}</div>",
        unsafe_allow_html=True
    )

st.markdown(f"🔁 Ricerche disponibili: **{MAX_RICERCHE - st.session_state['ricerche_effettuate']}**")

if not is_premium:
    with st.expander("🔓 Vuoi sbloccare più potenza?"):
        st.markdown(""" 
        ### ✨ Vantaggi Premium:
        - 🔁 30 ricerche al mese
        - 📇 60 contatti per ricerca
        - 🧠 Dati completi: telefono, email, sito
        - 💾 Download CSV completo

        👉 [**Attiva Premium ora**](https://ticalcolo.gumroad.com/l/uqpgo)
        """)

if st.session_state["ricerche_effettuate"] >= MAX_RICERCHE:
    st.error("🚫 Hai esaurito le ricerche disponibili.")
    st.markdown("[👉 Passa a Premium](https://ticalcolo.gumroad.com/l/uqpgo)")
    st.stop()

# === FORM DI RICERCA ===
gmaps = googlemaps.Client(key="AIzaSyCAaPuraZRkHip3QAT39F-Mi2rHsZjFmQg")
query = st.text_input("🔍 Tipo di attività", placeholder="Es: Estetista, Ristorante")
location = st.text_input("📍 Località", placeholder="Es: Roma, Milano")

if st.button("Estrai contatti"):
    if query and location:
        st.session_state["ricerche_effettuate"] += 1
        supabase.table("user").update({
            "ricerche_effettuate": st.session_state["ricerche_effettuate"]
        }).eq("email", user_email).execute()

        with st.spinner("📡 Estrazione in corso..."):
            try:
                results = gmaps.places(query=f"{query} a {location}")
                business_data = []

                for place in results.get("results", [])[:MAX_CONTATTI]:
                    name = place.get("name")
                    place_id = place.get("place_id")
                    details = gmaps.place(place_id)["result"]

                    address = details.get("formatted_address", "Non disponibile")
                    phone_number = details.get("international_phone_number") or \
                                   details.get("formatted_phone_number", "Non disponibile")

                    telefono_finale = phone_number if phone_number.startswith("+39 3") else "Non disponibile"
                    website = details.get("website", "Non disponibile")
                    email_estratto = "Non disponibile"

                    try:
                        if website != "Non disponibile":
                            html = requests.get(website, timeout=5).text
                            soup = BeautifulSoup(html, "html.parser")
                            for a in soup.find_all("a", href=True):
                                if "mailto:" in a["href"]:
                                    email_estratto = a["href"].split("mailto:")[1].split("?")[0]
                                    break
                    except:
                        pass

                    business_data.append({
                        "Nome": name,
                        "Indirizzo": address,
                        "Telefono": telefono_finale,
                        "Sito Web": website,
                        "Email": email_estratto
                    })

                if business_data:
                    df = pd.DataFrame(business_data)
                    st.dataframe(df)
                    csv = df.to_csv(index=False).encode("utf-8-sig")
                    st.download_button("📥 Scarica CSV", data=csv, file_name="contatti.csv", mime="text/csv")
                else:
                    st.warning("😕 Nessun risultato trovato.")
            except Exception as e:
                st.error(f"❌ Errore durante l’estrazione: {e}")
    else:
        st.warning("⚠️ Inserisci categoria e località.")
