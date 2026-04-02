import streamlit as st
import requests
from datetime import datetime

API_KEY = "eff258d2-d6a8-4db9-94b3-95e514b48511"

FUEL_TYPE = "e10"

st.set_page_config(page_title="E10 Benzinpreis-Ticker", page_icon="⛽")

# ---------------------------------------------------------
# 📱 Mobile-Optimierung
# ---------------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-size: 15px !important;
}
.price-card {
    background: #f5f7fa;
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #dce1e6;
    margin-bottom: 12px;
}
.price-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 6px;
}
.price-value {
    font-size: 22px;
    font-weight: 800;
    color: #0a7f00;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

st.title("⛽ E10 Benzinpreis‑Ticker")
st.subheader("Live‑Preise basierend auf deinem Standort")

st.info("Die Daten stammen von der Markttransparenzstelle (MTS-K).")


# ---------------------------------------------------------
# 📍 Standort abfragen
# ---------------------------------------------------------
st.write("### 📍 Standort wählen")

location = st.map_input("Bitte Standort freigeben oder auf die Karte tippen")

if location:
    LAT = location["latitude"]
    LNG = location["longitude"]
else:
    st.warning("Kein Standort gewählt – bitte Karte nutzen.")
    st.stop()


# ---------------------------------------------------------
# 🔌 API-Abfrage
# ---------------------------------------------------------
def fetch_prices(lat, lng):
    url = "https://creativecommons.tankerkoenig.de/json/list.php"
    params = {
        "lat": lat,
        "lng": lng,
        "rad": 10,
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


data = fetch_prices(LAT, LNG)

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
        <div class="price-card">
            <div class="price-title">{s['brand']} – {s['name']}</div>
            <div class="price-value">{s['price']} €</div>
            <div><b>Adresse:</b> {s['street']}, {s['place']}</div>
            <div><b>Entfernung:</b> {s['dist']:.1f} km</div>
        </div>
        """,
        unsafe_allow_html=True
    )
