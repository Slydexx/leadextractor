import streamlit as st
import googlemaps
import requests
from bs4 import BeautifulSoup
import pandas as pd
from supabase import create_client

# === CONFIGURAZIONE SUPABASE ===
SUPABASE_URL = "https://gsbfqagtbgafbsdzenxa.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdzYmZxYWd0YmdhZmJzZHplbnhhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQzODA4NjYs"
    "ImV4cCI6MjA1OTk1Njg2Nn0."
    "aabjFnBgMagRIWVTBm_MU7hrDq8rJHmSoIc7EVy8-EA"
)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === CONFIG STREAMLIT ===
st.set_page_config(page_title="Lead Extractor", layout="centered")

# === INIT SESSION STATE ===
if "user_logged_in" not in st.session_state:
    st.session_state["user_logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""
if "user_token" not in st.session_state:
    st.session_state["user_token"] = None
if "ricerche_effettuate" not in st.session_state:
    st.session_state["ricerche_effettuate"] = 0

# === NAVIGAZIONE ===
menu = st.sidebar.selectbox("📂 Navigazione", ["🏠 Home", "🔐 Login / Registrazione", "🚀 App"])

# === HOME ===
if menu == "🏠 Home":
    st.title("📍 Google Maps Lead Extractor")
    st.markdown("""
    #### ✨ Trova clienti e aziende nella tua zona in pochi clic

    Con questa app puoi:
    - Cercare attività su Google Maps
    - Estrarre **telefono, sito, email e indirizzo**
    - Esportare i dati in CSV

    #### 🎯 Ideale per:
    - Agenzie marketing
    - Rappresentanti commerciali
    - Liberi professionisti

    #### 🔓 Versione gratuita:
    - 3 ricerche totali
    - Max 4 contatti per ricerca

    #### 👑 Versione Premium:
    - 30 ricerche/mese
    - 60 contatti per ricerca

    👉 Usa la barra laterale per registrarti o accedere.
    """)

# === LOGIN / REGISTRAZIONE ===
elif menu == "🔐 Login / Registrazione":
    st.title("🔐 Login / Registrazione")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    azione = st.radio("Seleziona un'opzione", ["Login", "Registrati"])

    if st.button("Continua"):
        if email and password:
            try:
                if azione == "Registrati":
                    res = supabase.auth.sign_up({"email": email, "password": password})
                    if res.user:
                        st.success("✅ Registrazione avvenuta con successo. Ora puoi effettuare il login.")
                else:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    if res.session:
                        st.session_state["user_logged_in"] = True
                        st.session_state["user_email"] = email
                        st.session_state["user_token"] = res.session.access_token
                        st.success("✅ Login effettuato con successo.")
                        st.rerun()
                    else:
                        st.error("❌ Login fallito. Controlla email e password.")
            except Exception as e:
                st.error(f"Errore: {e}")
        else:
            st.warning("Inserisci email e password.")

# === APP ===
elif menu == "🚀 App":
    if not st.session_state["user_logged_in"]:
        st.warning("🔒 Devi effettuare il login per accedere all'app.")
        st.stop()

    # === LIMITI DEMO ===
    MAX_RICERCHE = 3
    MAX_CONTATTI = 4

    st.title("📊 Estrai contatti da Google Maps")
    st.info(f"DEMO GRATUITA: massimo {MAX_RICERCHE} ricerche con {MAX_CONTATTI} contatti ciascuna.")

    if st.session_state["ricerche_effettuate"] >= MAX_RICERCHE:
        st.error("🚫 Hai raggiunto il limite della versione gratuita.")
        st.markdown("[👉 Passa a Premium](https://buy.stripe.com/test_fZe00lahzdbM2WYcMN)")
        st.stop()

    gmaps = googlemaps.Client(key="AIzaSyCAaPuraZRkHip3QAT39F-Mi2rHsZjFmQg")

    query = st.text_input("🔍 Tipo di attività", placeholder="Es: Ristorante, Estetista")
    location = st.text_input("📍 Località", placeholder="Es: Roma, Milano")

    if st.button("Estrai contatti"):
        if query and location:
            st.session_state["ricerche_effettuate"] += 1
            with st.spinner("Estrazione in corso..."):
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
                        st.download_button("📥 Scarica contatti CSV", data=csv, file_name="contatti.csv", mime="text/csv")
                    else:
                        st.warning("😕 Nessun risultato trovato.")
                except Exception as e:
                    st.error(f"❌ Errore durante l’estrazione: {e}")
        else:
            st.warning("⚠️ Inserisci sia la categoria che la località.")
