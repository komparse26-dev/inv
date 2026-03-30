import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# Konfiguration der Webseite
st.set_page_config(page_title="Rohstoff-Monitor", layout="wide")

# 1. Daten-Definition (Dictionary)
COMMODITIES = {
    "Brent Öl": "BZ=F",
    "WTI Öl": "CL=F",
    "Gold": "GC=F",
    "Silber": "SI=F",
    "Erdgas": "NG=F",
    "Kupfer": "HG=F",
    "Platin": "PL=F",
    "Weizen": "ZW=F",
    "Kaffee": "KC=F"
}

# --- SIDEBAR ---
st.sidebar.header("⚙️ Einstellungen")

# Auswahlbox für den Rohstoff
selected_label = st.sidebar.selectbox(
    "Wähle einen Rohstoff aus:",
    options=list(COMMODITIES.keys())
)

# Zeitraum-Auswahl
period = st.sidebar.select_slider(
    "Zeitraum auswählen:",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    value="1y"
)

# Ticker abrufen
ticker_symbol = COMMODITIES[selected_label]

# --- HAUPTBEREICH ---
st.title(f"📊 Rohstoff-Analyse: {selected_label}")
st.markdown(f"Aktuelle Marktdaten für **{selected_label}** ({ticker_symbol}) via Yahoo Finance.")

# Daten laden
@st.cache_data(ttl=3600)  # Speichert Daten für 1 Stunde zwischen
def load_data(ticker, p):
    df = yf.download(ticker, period=p)
    return df

with st.spinner('Lade Marktdaten...'):
    data = load_data(ticker_symbol, period)

if not data.empty:
    # Berechnungen für Metriken
    # (Hinweis: yfinance gibt oft ein MultiIndex zurück, daher nutzen wir .iloc)
    current_price = data['Close'].iloc[-1]
    previous_price = data['Close'].iloc[-2]
    change = current_price - previous_price
    pct_change = (change / previous_price) * 100

    # Metriken in Spalten anzeigen
    col1, col2, col3 = st.columns(3)
    col1.metric("Aktueller Preis", f"{current_price:.2d} USD", f"{change:.2f} USD")
    col2.metric("Veränderung (%)", f"{pct_change:.2f} %")
    col3.metric("Letztes Update", data.index[-1].strftime('%d.%m.%Y'))

    # Plotly Chart erstellen
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['Close'], 
        mode='lines', 
        name=selected_label,
        line=dict(color='#00d1b2', width=2)
    ))

    fig.update_layout(
        template="plotly_dark",
        title=f"Preisverlauf: {selected_label}",
        xaxis_title="Datum",
        yaxis_title="Preis in USD",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabelle mit Rohdaten (optional ausklappbar)
    with st.expander("Rohdaten anzeigen"):
        st.dataframe(data.tail(10), use_container_width=True)

else:
    st.error(f"Keine Daten für {selected_label} gefunden. Möglicherweise ist das Ticker-Symbol {ticker_symbol} vorübergehend nicht erreichbar.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Erstellt mit Python & Streamlit.")
