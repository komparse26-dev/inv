import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 1. Grundkonfiguration
st.set_page_config(page_title="Rohstoff-Ticker Pro", layout="wide", page_icon="💹")

# HIER den CSS-Code einfügen
hide_st_style = """
            <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
           #header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# Rohstoff-Liste
COMMODITIES = {
    "Brent Öl": "BZ=F", "WTI Öl": "CL=F", "Gold": "GC=F",
    "Silber": "SI=F", "Erdgas": "NG=F", "Kupfer": "HG=F",
    "Platin": "PL=F", "Weizen": "ZW=F", "Kaffee": "KC=F"
}

# --- FUNKTIONEN ---
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

# --- SIDEBAR: EINSTELLUNGEN ---
st.sidebar.header("📊 Auswahl & Zeitraum")
selected_label = st.sidebar.selectbox("Rohstoff:", list(COMMODITIES.keys()))
period = st.sidebar.selectbox("Daten-Zeitraum:", ["6mo", "1y", "2y", "5y", "max"], index=1)

st.sidebar.markdown("---")
# Hier kommen die interaktiven Parameter
with st.sidebar.expander("🛠️ Indikator-Parameter", expanded=True):
    rsi_p = st.number_input("RSI Periode (Tage)", min_value=5, max_value=50, value=14)
    sma_s = st.number_input("Kurzer Trend (SMA)", min_value=5, max_value=100, value=20)
    sma_l = st.number_input("Langer Trend (SMA)", min_value=10, max_value=300, value=50)

# --- DATEN VERARBEITUNG ---
data = load_data(COMMODITIES[selected_label], period)

if not data.empty:
    close_prices = data['Close']
    
    # Berechnungen mit den User-Parametern
    data['RSI'] = calculate_rsi(close_prices, rsi_p)
    data['SMA_Short'] = close_prices.rolling(window=sma_s).mean()
    data['SMA_Long'] = close_prices.rolling(window=sma_l).mean()
    
    # Aktuelle Werte für das Dashboard
    current_p = float(close_prices.iloc[-1])
    last_rsi = float(data['RSI'].iloc[-1])
    s_sma = float(data['SMA_Short'].iloc[-1])
    l_sma = float(data['SMA_Long'].iloc[-1])

    # --- LOGIK: EMPFEHLUNG ---
    # Wir erstellen ein Punktesystem für die Empfehlung
    score = 0
    if current_p > s_sma: score += 1 # Positiver Kurztrend
    if s_sma > l_sma: score += 1     # Golden Cross / Positiver Langtrend
    if last_rsi < 30: score += 2     # Stark überverkauft (Kauf-Chance)
    if last_rsi > 70: score -= 2     # Überkauft (Verkaufs-Warnung)

    if score >= 2:
        rec = "KAUFEN"; color = "#2ecc71"
    elif score <= -1:
        rec = "VERKAUFEN"; color = "#e74c3c"
    else:
        rec = "HALTEN / NEUTRAL"; color = "#f1c40f"

    # --- UI: DASHBOARD ---
    st.title(f"{selected_label} Analyse")
    
    # Metriken Reihe 1
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Preis", f"{current_p:.2f} USD")
    m2.metric(f"RSI ({rsi_p})", f"{last_rsi:.1f}")
    m3.metric(f"SMA {sma_s}", f"{s_sma:.2f}")
    m4.metric(f"SMA {sma_l}", f"{l_sma:.2f}")

    # Große Empfehlungsbox
    st.markdown(f"""
        <div style="background-color:{color}; padding:15px; border-radius:10px; text-align:center;">
            <h2 style="color:white; margin:0;">EMPFEHLUNG: {rec}</h2>
            <p style="color:white; margin:0; opacity:0.8;">Basierend auf RSI {rsi_p} und SMA {sma_s}/{sma_l}</p>
        </div>
    """, unsafe_allow_html=True)
    st.write("")

    # --- CHARTS ---
    # Hauptchart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=close_prices, name="Preis", line=dict(color='white', width=2)))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_Short'], name=f"SMA {sma_s}", line=dict(color='orange', width=1.5)))
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA_Long'], name=f"SMA {sma_l}", line=dict(color='cyan', width=1.5)))
    
    fig.update_layout(template="plotly_dark", height=450, title="Preisentwicklung & Trendlinien", 
                      xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # RSI Chart
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=data.index, y=data['RSI'], name="RSI", line=dict(color='magenta', width=1.5)))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    fig_rsi.update_layout(template="plotly_dark", height=200, title="RSI Indikator", 
                          yaxis=dict(range=[0, 100]), margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_rsi, use_container_width=True)

else:
    st.error("Fehler beim Laden der Daten. Bitte prüfe die Internetverbindung oder den Ticker.")

st.sidebar.info(f"Daten für {selected_label} sind aktuell.")
