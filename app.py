import streamlit as st
import googlemaps
import requests
from bs4 import BeautifulSoup
import pandas as pd

# === CONFIG ===
st.set_page_config(page_title="Google Maps Lead Extractor", layout="centered")
st.title("📍 Google Maps Lead Extractor")

# === DEMO INFO ===
MAX_RICERCHE = 3
MAX_CONTATTI = 4

# === SESSION STATE PER TRACCIARE USO ===
if "ricerche_effettuate" not in st.session_state:
    st.session_state["ricerche_effettuate"] = 0

st.markdown(f"""
💡 <span style='color:orange'><strong>DEMO GRATUITA</strong>:</span><br>
• Massimo <strong>{MAX_RICERCHE}</strong> ricerche totali<br>
• Fino a <strong>{MAX_CONTATTI}</strong> contatti per ogni ricerca<br><br>

👑 Vuoi la versione completa?<br>
➡️ <a href="https://buy.stripe.com/test_fZe00lahzdbM2WYcMN" target="_blank"><strong>Passa a Premium</strong> (30 ricerche / 60 contatti)</a>
""", unsafe_allow_html=True)

# === Google Maps Client ===
gmaps = googlemaps.Client(key="AIzaSyCAaPuraZRkHip3QAT39F-Mi2rHsZjFmQg")

# === FORM RICERCA ===
if st.session_state["ricerche_effettuate"] >= MAX_RICERCHE:
    st.warning("🚫 Hai raggiunto il numero massimo di ricerche gratuite. Passa a Premium per continuare.")
    st.stop()

query = st.text_input("🔍 Tipo di attività", placeholder="Es: Estetista, Ristorante")
location = st.text_input("📍 Località", placeholder="Es: Roma, Milano")

if st.button("Estrai contatti"):
    if query and location:
        st.session_state["ricerche_effettuate"] += 1
        with st.spinner("🔍 Estrazione in corso..."):
            try:
                results = gmaps.places(query=f"{query} a {location}")
                business_data = []
                for place in results.get("results", [])[:MAX_CONTATTI]:
                    name = place.get("name")
                    place_id = place.get("place_id")
                    details = gmaps.place(place_id)["result"]

                    address = details.get("formatted_address") or \
                              details.get("vicinity") or "Non disponibile"

                    phone_number = details.get("international_phone_number") or \
                                   details.get("formatted_phone_number") or "Non disponibile"

                    telefono_finale = "Non disponibile"
                    if phone_number.startswith("+39 3"):
                        telefono_finale = phone_number  # cellulare
                    elif phone_number != "Non disponibile":
                        telefono_finale = phone_number  # fisso se non c'è altro

                    website = details.get("website", "Non disponibile")
                    email_estratto = "Non disponibile"

                    try:
                        if website != "Non disponibile":
                            html = requests.get(website, timeout=5).text
                            soup = BeautifulSoup(html, "html.parser")
                            for a in soup.find_all("a", href=True):
                                href = a["href"]
                                if "mailto:" in href:
                                    email_estratto = href.split("mailto:")[1].split("?")[0]
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
