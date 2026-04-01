import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 1. Konfiguration (Muss ganz oben stehen)
st.set_page_config(page_title="Rohstoff-Analyst Pro", layout="wide")

# --- DESIGN: KOPF/FUSSZEILE AUSBLENDEN & ABSTÄNDE OPTIMIEREN ---
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    #footer {visibility: hidden;}
    #header {visibility: hidden;}
   /* DIESE ZEILE BLENDET DEN 'MANAGE APP' BUTTON AUS */
    div[data-testid="stStatusWidget"] {visibility: hidden;}

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    /* Das Design der Auswahlfelder anpassen */
    .stSelectbox, .stSlider {
        margin-bottom: 10px;
    }
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- DATEN-LOGIK ---
COMMODITIES = {
    "Brent Öl": "BZ=F", "WTI Öl": "CL=F", "Gold": "GC=F",
    "Silber": "SI=F", "Erdgas": "NG=F", "Kupfer": "HG=F"
}

def calculate_rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=600)
def load_data(ticker, p):
    df = yf.download(ticker, period=p, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

# --- ON-TOP NAVIGATION (Zuerst die Auswahlfelder) ---
# Wir erstellen zwei Reihen für die Steuerung
row1_col1, row1_col2 = st.columns([2, 1])

with row1_col1:
    selected_label = st.selectbox("Rohstoff wählen:", list(COMMODITIES.keys()))

with row1_col2:
    period = st.selectbox("Zeitraum:", ["6mo", "1y", "2y", "5y", "max"], index=1)

# Ein Expander für die technischen Parameter (platzsparend)
with st.expander("🛠️ Analyse-Parameter anpassen (RSI, Trend)"):
    c1, c2, c3 = st.columns(3)
    rsi_p = c1.number_input("RSI (Tage)", 5, 50, 14)
    sma_s = c2.number_input("SMA Kurz", 5, 100, 20)
    sma_l = c3.number_input("SMA Lang", 10, 300, 50)

# --- DATEN LADEN & BERECHNEN ---
data = load_data(COMMODITIES[selected_label], period)

if not data.empty:
    close_prices = data['Close']
    data['RSI'] = calculate_rsi(close_prices, rsi_p)
    data['SMA_Short'] = close_prices.rolling(window=sma_s).mean()
    data['SMA_Long'] = close_prices.rolling(window=sma_l).mean()
    
    current_p = float(close_prices.iloc[-1])
    last_rsi = float(data['RSI'].iloc[-1])
    s_sma = float(data['SMA_Short'].iloc[-1])
    l_sma = float(data['SMA_Long'].iloc[-1])

    # Empfehlungs-Logik (einfach)
    if last_rsi < 35: rec = "KAUFEN"; color = "#2ecc71"
    elif last_rsi > 65: rec = "VERKAUFEN"; color = "#e74c3c"
    else: rec = "HALTEN"; color = "#f1c40f"

    # --- UI: ANZEIGE ---
    # Metriken kompakt nebeneinander
    m1, m2, m3 = st.columns(3)
    m1.metric("Kurs", f"{current_p:.2f} USD")
    m2.metric("RSI", f"{last_rsi:.1f}")
    
    with m3:
        st.markdown(f"""
            <div style="background-color:{color}; padding:10px; border-radius:5px; text-align:center; color:white; font-weight:bold;">
                {rec}
            </div>
        """, unsafe_allow_html=True)

    # Charts
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=close_prices, name="Preis", line=dict(color='white', width=2)))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_Short'], name="SMA S", line=dict(color='orange', width=1)))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_Long'], name="SMA L", line=dict(color='cyan', width=1)))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

    # Kleiner RSI Chart darunter
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], name="RSI", line=dict(color='magenta', width=1)))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    fig_rsi.update_layout(template="plotly_dark", height=180, margin=dict(l=10, r=10, t=0, b=0), yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_rsi, use_container_width=True)

else:
    st.error("Keine Daten verfügbar.")
