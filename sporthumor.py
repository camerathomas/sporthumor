import json
import random
import streamlit as st
from google import genai

# --- Configuratie ---
st.set_page_config(page_title="Sporthumor Prompt Generator", page_icon="🤪")
st.title("🤪 Sporthumor Prompt Generator")
st.caption("Genereer absurde situaties voor je 5-seconden video's.")

# API key ophalen (lokaal via .streamlit/secrets.toml, cloud via Settings > Secrets)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ Geen GEMINI_API_KEY gevonden. Voeg deze toe aan je Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- JSON bestanden laden ---
@st.cache_data
def laad_json(bestandsnaam):
    with open(bestandsnaam, "r", encoding="utf-8") as f:
        return json.load(f)

sporten_data = laad_json("sporten.json")
handelingen_data = laad_json("handelingen.json")
twist_data = laad_json("twist.json")

# --- Willekeurige selectie ---
def kies_willekeurig(data, sleutel):
    if sleutel not in data:
        st.error(f"❌ Sleutel '{sleutel}' niet gevonden. Beschikbare sleutels: {list(data.keys())}")
        st.stop()
    return random.choice(data[sleutel])

# --- Prompt naar Gemini sturen ---
def genereer_image_prompt(sport, handeling, twist):
    geslacht = random.choice(sport["geslacht"]) if isinstance(sport["geslacht"], list) else sport["geslacht"]

    ruwe_situatie = (
        f"Een {geslacht} {sport['naam']}speler "
        f"probeert te {handeling['naam']} ({handeling['omschrijving']}), "
        f"maar dan gebeurt het onverwachte: {twist['omschrijving']}"
    )

    system_instruction = (
        "Je bent een creatieve prompt engineer voor AI image generators (zoals Midjourney, DALL-E). "
        "Je krijgt een absurde sportscène in het Nederlands. "
        "Jouw taak: zet dit om naar een Engelstalige image prompt die de scène visueel zo komisch en onverwacht mogelijk maakt. "
        "Focus op: rare gezichtsuitdrukkingen, onmogelijke natuurkunde, verrassende details. "
        "Geef alleen de prompt zelf terug, zonder uitleg of inleiding. "
        "Houd het bij 1-2 zinnen, maximaal 60 woorden."
    )

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[system_instruction, ruwe_situatie]
    )

    return ruwe_situatie, response.text.strip()

# --- UI ---
st.markdown("Klik op de knop om een willekeurige absurde sportscène te genereren.")

if st.button("🎲 Genereer een sporthumor situatie", type="primary"):
    sport = kies_willekeurig(sporten_data, "sporten")
    handeling = kies_willekeurig(handelingen_data, "handelingen")
    twist = kies_willekeurig(twist_data, "twist")

    with st.spinner("Bezig met genereren..."):
        ruwe_situatie, image_prompt = genereer_image_prompt(sport, handeling, twist)

    st.subheader("📋 Ruwe situatie (Nederlands)")
    st.info(ruwe_situatie)

    st.subheader("🎨 Image Generator Prompt (Engels)")
    st.success(image_prompt)

    st.code(image_prompt, language="text")

    with st.expander("Gekozen componenten"):
        st.write(f"**Sport:** {sport['naam']} ({', '.join(sport['geslacht'])})")
        st.write(f"**Handeling:** {handeling['naam']} — {handeling['omschrijving']}")
        st.write(f"**Twist:** {twist['naam']} — {twist['omschrijving']}")

st.divider()
st.caption("Totaal aantal combinaties: 20 × 20 × 20 = **8000**")
