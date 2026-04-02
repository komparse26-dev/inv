import streamlit as st
import requests
from datetime import datetime

# ---------------------------------------------------------
# 🔑 API-KEY EINTRAGEN
# ---------------------------------------------------------
API_KEY = "eff258d2-d6a8-4db9-94b3-95e514b48511"   # <-- HIER EINTRAGEN

# ---------------------------------------------------------
# 📍 Standort Wendelstein (PLZ 90530)
# ---------------------------------------------------------
LAT = 49.352
LNG = 11.150
RADIUS_KM = 10
FUEL_TYPE = "e10"


# ---------------------------------------------------------
# 🔌 Funktion: Preise abrufen
# ---------------------------------------------------------
def fetch_prices():
    url = "https://creativecommons.tankerkoenig.de/json/list.php"
    params = {
        "lat": LAT,
        "lng": LNG,
        "rad": RADIUS_KM,
        "sort": "price",
        "type": FUEL_TYPE,
        "apikey": API_KEY,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        return {"ok": False, "message": f"Verbindungsfehler: {e}"}

    return data


# ---------------------------------------------------------
# 🖥 Streamlit UI
# ---------------------------------------------------------
st.set_page_config(page_title="E10 Benzinpreis-Ticker", page_icon="⛽")

st.title("⛽ E10 Benzinpreis‑Ticker")
st.subheader("Region 90530 Wendelstein ±10 km")

st.info("Die Daten stammen von der Markttransparenzstelle (MTS-K).")


# ---------------------------------------------------------
# 📡 API abrufen
# ---------------------------------------------------------
data = fetch_prices()

if not data.get("ok"):
    st.error(f"API‑Fehler: {data.get('message')}")
    st.stop()

stations = data.get("stations", [])

if not stations:
    st.warning("Keine Tankstellen gefunden.")
    st.stop()


# ---------------------------------------------------------
# 📊 Ausgabe
# ---------------------------------------------------------
st.write(f"**Stand:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

for s in stations:
    if s.get("price") is None:
        continue

    st.markdown(
        f"""
        ### {s['brand']} – {s['name']}
        **Preis:** {s['price']} €  
        **Adresse:** {s['street']}, {s['place']}  
        **Entfernung:** {s['dist']:.1f} km  
        ---
        """
    )
