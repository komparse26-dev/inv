import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# ---------------------------------------------------------
# 🔑 API-Keys
# ---------------------------------------------------------
TANKERKOENIG_API_KEY = "eff258d2-d6a8-4db9-94b3-95e514b48511"  # <-- hier deinen Tankerkoenig-Key eintragen
OPENCAGE_KEY = "0a9a41d618f646ffb134cb14830e46be"

# ---------------------------------------------------------
# 🔧 Streamlit Grundkonfiguration
# ---------------------------------------------------------
st.set_page_config(
    page_title="E10 Benzinpreis-Ticker",
    page_icon="⛽",
    layout="centered"
)

# Auto-Refresh alle 300 Sekunden (5 Minuten)
st.markdown(
    '<meta http-equiv="refresh" content="300">', unsafe_allow_html=True
)

# ---------------------------------------------------------
# 🎨 Mobile-optimiertes Styling
# ---------------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-size: 14px !important;
}
.price-card {
    background: gray;
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #dce1e6;
    margin-bottom: 12px;
}
.price-title {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 6px;
}
.price-value {
    font-size: 18px;
    font-weight:600;
    color: #0a7f00;
    margin-bottom: 8px;
}
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    background: gray;
    font-size: 12px;
    margin-right: 4px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 🧩 Header
# ---------------------------------------------------------
st.title("⛽ Benzinpreis‑Ticker")
#st.subheader("Live‑Preise basierend auf deinem Standort")
#st.info("Daten: Markttransparenzstelle (MTS-K) + OpenCage Geocoding")

#st.write("🔄 Die Seite aktualisiert sich automatisch alle **5 Minuten**.")

# ---------------------------------------------------------
# 📍 Standort & Filter
# ---------------------------------------------------------
st.write("### 📍 Standort & Filter")

col1, col2 = st.columns([2, 1])

with col1:
    address = st.text_input("Adresse / Ort eingeben:", "Wendelstein")

with col2:
    radius = st.slider("Radius (km)", min_value=2, max_value=25, value=10, step=1)

fuel_type = st.selectbox(
    "Kraftstoff",
    options=[("e10", "E10"), ("diesel", "Diesel")],
    format_func=lambda x: x[1]
)[0]

if not address:
    st.warning("Bitte einen Ort eingeben.")
    st.stop()

# ---------------------------------------------------------
# 🌍 Geocoding mit OpenCage
# ---------------------------------------------------------
geo_url = "https://api.opencagedata.com/geocode/v1/json"
geo_params = {
    "q": address,
    "key": OPENCAGE_KEY,
    "limit": 1,
    "no_annotations": 1
}

try:
    geo_res = requests.get(geo_url, params=geo_params, timeout=10)
    geo_json = geo_res.json()
except Exception as e:
    st.error(f"Geocoding-Fehler: {e}")
    st.stop()

if not geo_json.get("results"):
    st.error("Ort nicht gefunden.")
    st.stop()

LAT = geo_json["results"][0]["geometry"]["lat"]
LNG = geo_json["results"][0]["geometry"]["lng"]

st.success(f"📍 Standort erkannt: {address} ({LAT:.5f}, {LNG:.5f})")

# ---------------------------------------------------------
# ⛽ Tankerkoenig API
# ---------------------------------------------------------
def fetch_prices(lat, lng, radius_km, fuel):
    url = "https://creativecommons.tankerkoenig.de/json/list.php"
    params = {
        "lat": lat,
        "lng": lng,
        "rad": radius_km,
        "sort": "price",
        "type": fuel,
        "apikey": TANKERKOENIG_API_KEY,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        return {"ok": False, "message": f"Verbindungsfehler: {e}"}

    return data

data = fetch_prices(LAT, LNG, radius, fuel_type)

if not data.get("ok"):
    st.error(f"API‑Fehler: {data.get('message')}")
    st.stop()

stations = data.get("stations", [])

if not stations:
    st.warning("Keine Tankstellen gefunden.")
    st.stop()

# ---------------------------------------------------------
# ⛽ Preis aufsteigend sortieren
# ---------------------------------------------------------
stations = [s for s in stations if s.get("price") is not None]
stations = sorted(stations, key=lambda x: x["price"])

st.write(f"**Stand:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

# ---------------------------------------------------------
# 🗺️ Karte
# ---------------------------------------------------------
#st.write("### 🗺️ Tankstellen auf Karte")

#map_df = pd.DataFrame([
   # {"lat": s["lat"], "lon": s["lng"], "name": s["name"], "price": s["price"]}
   # for s in stations
#])

#st.map(map_df)

# ---------------------------------------------------------
# 📊 Detailansicht als Premium-Boxen
# ---------------------------------------------------------
st.write("### ⛽ Preise (aufsteigend sortiert)")

for s in stations:
    st.markdown(
        f"""
        <div class="price-card">
            <div class="price-title">{s['brand']} – {s['name']}</div>
            <div class="price-value">{s['price']} €</div>
            <div>
                <span class="badge">{fuel_type.upper()}</span>
                <span class="badge">{s['dist']:.1f} entfernt</span>
            </div>
            <div>{s['street']}, {s['place']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
