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

# === Sblocco PREMIUM via URL ===
query_params = st.query_params
if "email" in query_params and "access" in query_params:
    if query_params["access"] == "premium":
        email_from_link = query_params["email"]
        supabase.table("user").upsert({
            "email": email_from_link,
            "premium": True,
            "ricerche_effettuate": 0
        }).execute()
        st.session_state["just_upgraded"] = True
        st.session_state["user_email"] = email_from_link
        st.session_state["user_logged_in"] = True

# === LOGIN / REGISTRAZIONE ===
st.markdown("<h2 style='text-align: center;'>📍 Lead Extractor</h2>", unsafe_allow_html=True)

if not st.session_state["user_logged_in"]:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    azione = st.radio("Accedi o Registrati", ["Login", "Registrati"], horizontal=True)

    if st.button("Continua"):
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

# === MESSAGGIO DI CONFERMA PREMIUM (solo se attivato via link) ===
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

if st.session_state["ricerche_effettuate"] >= MAX_RICERCHE:
    st.error("🚫 Hai esaurito le ricerche disponibili.")
    st.markdown("[👉 Passa a Premium](https://buy.stripe.com/test_fZe00lahzdbM2WYcMN)")
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

                    address = details.get("formatted_address") or details.get("vicinity") or "Non disponibile"
                    phone_number = details.get("international_phone_number") or \
                                   details.get("formatted_phone_number") or "Non disponibile"

                    telefono_finale = "Non disponibile"
                    if phone_number.startswith("+39 3"):
                        telefono_finale = phone_number
                    elif phone_number != "Non disponibile":
                        telefono_finale = phone_number

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
