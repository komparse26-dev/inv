import streamlit as st
import requests
from datetime import datetime

API_KEY = "eff258d2-d6a8-4db9-94b3-95e514b48511"
FUEL_TYPE = "e10"

st.set_page_config(page_title="E10 Benzinpreis-Ticker", page_icon="⛽")

# ---------------------------------------------------------
# 📍 GPS per JavaScript abfragen (kompatibel mit allen Streamlit-Versionen)
# ---------------------------------------------------------
gps_js = """
<script>
function sendLocation() {
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            const coords = lat + "," + lng;
            const streamlitEvent = new Event("streamlit:location");
            window.dispatchEvent(streamlitEvent);
            window.parent.postMessage({type: "coords", data: coords}, "*");
        },
        (err) => {
            window.parent.postMessage({type: "coords_error", data: err.message}, "*");
        }
    );
}
sendLocation();
</script>
"""

st.markdown(gps_js, unsafe_allow_html=True)

# Listener für JS → Streamlitw
if "coords" not in st.session_state:
    st.session_state["coords"] = None

coords = st.session_state["coords"]

# Empfange Daten aus JS
coords_msg = st.experimental_get_websocket_message()

if coords_msg and isinstance(coords_msg, dict):
    if coords_msg.get("type") == "coords":
        st.session_state["coords"] = coords_msg.get("data")
        coords = st.session_state["coords"]
