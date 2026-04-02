import streamlit as st
import requests
from datetime import datetime

API_KEY = "eff258d2-d6a8-4db9-94b3-95e514b48511"

FUEL_TYPE = "e10"

st.set_page_config(page_title="E10 Benzinpreis-Ticker", page_icon="⛽")



# ---------------------------------------------------------
# 📍 GPS per JavaScript abfragen
# ---------------------------------------------------------
gps_code = """
<script>
navigator.geolocation.getCurrentPosition(
    (pos) => {
        const coords = pos.coords.latitude + "," + pos.coords.longitude;
        window.parent.postMessage({type: "gps", coords: coords}, "*");
    },
    (err) => {
        window.parent.postMessage({type: "gps_error", message: err.message}, "*");
    }
);
</script>
"""

st.markdown(gps_code, unsafe_allow_html=True)

# Listener für GPS-Daten
gps_data = st.session_state.get("gps_data", None)

message = st.experimental_get_query_params()

# Streamlit empfängt die Daten über on_event
def on_gps_event():
    pass

st.markdown("""
<script>
window.addEventListener("message", (event) => {
    if (event.data.type === "gps") {
        const coords = event.data.coords;
        const url = new URL(window.location.href);
        url.searchParams.set("gps", coords);
        window.location.href = url.toString();
    }
});
</script>
""", unsafe_allow_html=True)

# GPS aus URL lesen
gps_param = st.experimental_get_query_params().get("gps", None)

if gps_param:
    lat, lng = gps_param[0].split(",")
    LAT = float(lat)
    LNG = float(lng)
    st.success(f"📍 Standort erkannt: {LAT:.5f}, {LNG:.5f}")
else:
    st.warning("📍 Standort wird abgefragt… bitte Freigabe erteilen.")
    st.stop()


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
