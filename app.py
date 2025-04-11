import streamlit as st

# === CONFIGURAZIONE ===
st.set_page_config(page_title="Lead Extractor - Home", layout="centered")

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
    </style>
""", unsafe_allow_html=True)

# === CONTENUTO ===
st.markdown("<div class='big-title'>📍 Lead Extractor</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Lo strumento che trasforma Google Maps in un database di contatti utili per il tuo business.</div>", unsafe_allow_html=True)

st.markdown("""
<div class='benefits'>

### Perché scegliere Lead Extractor?

✅ Trova attività commerciali con **Google Maps** <br>
✅ Estrai **telefono, email, sito web e indirizzo** <br>
✅ Nessun software da installare – funziona direttamente online <br>
✅ **Esporta i contatti in CSV** per email marketing, campagne di vendita e networking <br>
✅ Ideale per agenti, imprenditori, marketer, liberi professionisti

---

### 🔓 Versione gratuita (Demo)
- ✅ 3 ricerche totali
- ✅ Max 4 contatti per ricerca

### 👑 Versione Premium
- 🔁 **30 ricerche ogni mese**
- 📇 **Fino a 60 contatti per ricerca**
- 💾 **Download CSV illimitato**
- 🔐 Accesso esclusivo e prioritario

</div>
""", unsafe_allow_html=True)

# === CALL TO ACTION ===
st.markdown("""
<div class='cta-button'>
    <a href="https://ticalcolo.gumroad.com/l/uqpgo" target="_blank">
        <button style="padding: 0.8em 1.5em; font-size: 1.1em; border-radius: 5px; background-color: #ff4b4b; color: white; border: none;">
            🚀 Passa a Premium ora - €19.90/mese
        </button>
    </a>
</div>
""", unsafe_allow_html=True)

# === INVITO AL LOGIN ===
st.markdown("""
---

🎯 Hai già un account? [**Clicca qui per accedere all'app**](https://leadextractor-it.streamlit.app)
""")
