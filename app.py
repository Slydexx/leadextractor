import streamlit as st
import googlemaps
import requests
from bs4 import BeautifulSoup
import pandas as pd

# === CONFIG STREAMLIT ===
st.set_page_config(page_title="Google Maps Lead Extractor", layout="centered")
st.title("📍 Google Maps Lead Extractor")

st.markdown("""
Questo strumento ti permette di cercare attività commerciali su **Google Maps**  
e ottenere **contatti utili** come **telefono, email, sito web e indirizzo**.

---

👉 Inserisci una categoria e una località per iniziare la ricerca.
""")

# === Google Maps Client ===
gmaps = googlemaps.Client(key="AIzaSyCAaPuraZRkHip3QAT39F-Mi2rHsZjFmQg")

# === MODULO DI RICERCA ===
query = st.text_input("🔍 Tipo di attività", placeholder="Es: Estetista, Ristorante")
location = st.text_input("📍 Località", placeholder="Es: Roma, Milano")

if st.button("Estrai contatti"):
    if query and location:
        with st.spinner("🔍 Estrazione in corso..."):
            try:
                results = gmaps.places(query=f"{query} a {location}")
                business_data = []
                for place in results.get("results", []):
                    name = place.get("name")
                    place_id = place.get("place_id")
                    details = gmaps.place(place_id)["result"]

                    address = details.get("formatted_address") or \
                              details.get("vicinity") or "Non disponibile"

                    phone_number = details.get("international_phone_number") or \
                                   details.get("formatted_phone_number") or "Non disponibile"

                    # === Priorità a cellulare ===
                    telefono_finale = "Non disponibile"
                    if phone_number.startswith("+39 3"):  # Cellulare italiano
                        telefono_finale = phone_number
                    elif phone_number != "Non disponibile":
                        telefono_finale = phone_number  # Usa fisso solo se non c'è il cellulare

                    website = details.get("website", "Non disponibile")
                    email_estratto = "Non disponibile"

                    try:
                        if website != "Non disponibile":
                            html = requests.get(website, timeout=5).text
                            soup = BeautifulSoup(html, "html.parser")
                            links = soup.find_all("a", href=True)
                            for a in links:
                                href = a["href"]
                                if "mailto:" in href:
                                    email_estratto = href.split("mailto:")[1].split("?")[0]
                                    break
                    except Exception:
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
aa
