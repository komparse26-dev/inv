import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Konfiguration der Webseite
st.set_page_config(page_title="Rohstoff-Monitor", layout="wide", page_icon="📈")

# 1. Daten-Definition
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

selected_label = st.sidebar.selectbox(
    "Wähle einen Rohstoff aus:",
    options=list(COMMODITIES.keys())
)

period = st.sidebar.select_slider(
    "Zeitraum auswählen:",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    value="1y"
)

ticker_symbol = COMMODITIES[selected_label]

# --- DATEN LADEN ---
@st.cache_data(ttl=3600)
def load_data(ticker, p):
    # 'auto_adjust=True' sorgt für saubere Schlusskurse
    df = yf.download(ticker, period=p, auto_adjust=True)
    return df

st.title(f"📊 Rohstoff-Analyse: {selected_label}")

with st.spinner('Lade Marktdaten...'):
    data = load_data(ticker_symbol, period)

# --- FEHLERPRÜFUNG & ANZEIGE ---
if data is not None and not data.empty:
    try:
        # Falls yfinance Multi-Index Spalten liefert, flach machen
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Letzte Werte extrahieren (als reine Zahlenwerte)
        current_price = float(data['Close'].iloc[-1])
        previous_price = float(data['Close'].iloc[-2])
        change = current_price - previous_price
        pct_change = (change / previous_price) * 100

        # Metriken anzeigen
        col1, col2, col3 = st.columns(3)
        # Fix: hier war der Fehler .2d -> geändert auf .2f
        col1.metric("Aktueller Preis", f"{current_price:.2f} USD", f"{change:.2f} USD")
        col2.metric("Veränderung (%)", f"{pct_change:.2f} %")
        col3.metric("Datum", data.index[-1].strftime('%d.%m.%Y'))

        # Chart erstellen
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
            xaxis_title="Datum",
            yaxis_title="Preis in USD",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=30, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Tabellenansicht der Daten"):
            st.write(data.tail(15))

    except Exception as e:
        st.error(f"Fehler bei der Datenverarbeitung: {e}")
else:
    st.warning(f"Keine Daten für {selected_label} gefunden. Das Ticker-Symbol {ticker_symbol} ist eventuell am Wochenende oder Feiertagen nicht aktiv.")

st.sidebar.markdown("---")
st.sidebar.info("Datenquelle: Yahoo Finance")
