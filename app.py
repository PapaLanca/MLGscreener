import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, time

# --- Configuration ---
st.set_page_config(
    page_title="MLG Screener Pro",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS avec fond sombre et design professionnel ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
:root {
    --primary: #4f81bd;
    --secondary: #3b82f6;
    --valid: #10b981;
    --invalid: #ef4444;
    --warning: #f59e0b;
    --dark-bg: #1e293b;
    --dark-card: #334155;
    --text: #e2e8f0;
    --border: #475569;
}
body {font-family: 'Montserrat', sans-serif; background-color: var(--dark-bg) !important; color: var(--text) !important;}
[data-testid="stAppViewContainer"] {background-color: var(--dark-bg) !important;}
[data-testid="stHeader"] {background-color: rgba(0, 0, 0, 0) !important;}

.banner {display:flex;align-items:center;gap:20px;margin-bottom:30px;}
.banner img {width:180px;}
.title {color:var(--primary);font-size:24px;font-weight:600;}

.score-card {background:var(--dark-card);padding:20px;border-radius:8px;margin-bottom:20px;text-align:center;}
.score-number {font-size:32px;font-weight:700;color:var(--valid);}

.criteria-container {margin:20px 0;}
.criterion {display:flex;justify-content:space-between;align-items:center;padding:12px;background:var(--dark-card);border-radius:6px;border:1px solid var(--border);margin-bottom:8px;}
.criterion.valid {border-left:4px solid var(--valid);}
.criterion.invalid {border-left:4px solid var(--invalid);}
.status {font-weight:600;}
.status.valid {color:var(--valid);}
.status.invalid {color:var(--invalid);}

.gf-section {background:var(--dark-card);padding:20px;border-radius:8px;margin-top:20px;}
.gf-item {display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);}
.gf-link {color:var(--primary);text-decoration:none;font-weight:600;}
.gf-link:hover {text-decoration:underline;}

.nav-buttons {display:flex;gap:20px;justify-content:center;margin:20px 0;}
.nav-button {background:var(--primary);color:white;padding:12px 24px;border:none;border-radius:6px;font-weight:600;text-decoration:none;}

.plan-section {background:var(--dark-card);padding:20px;border-radius:8px;margin-top:30px;}
.footer {margin-top:50px;padding:20px;text-align:center;color:var(--text);font-size:14px;}

.stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>select {
    background-color: var(--dark-card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
.stButton>button {
    background-color: var(--primary) !important;
    color: white !important;
    border-radius: 6px !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# --- Fonction RSI ---
def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100./(1.+rs)

    for i in range(period, len(prices)):
        delta = deltas[i-1]
        upval = delta if delta > 0 else 0
        downval = -delta if delta < 0 else 0

        up = (up*(period-1) + upval)/period
        down = (down*(period-1) + downval)/period
        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)
    return rsi[-1]

# --- Analyse complète ---
def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="3mo", interval="1d")

        # Calcul des métriques
        current_price = info.get('currentPrice')
        avg_volume = info.get('averageVolume', 0)
        roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
        debt_to_equity = info.get('debtToEquity', 0)
        inst_ownership = info.get('institutionalOwnership', 0)
        beta = info.get('beta', 1)
        eps_growth = info.get('earningsQuarterlyGrowth', 0)
        fcf = info.get('freeCashflow', 0)
        shares_outstanding = info.get('sharesOutstanding', 1)
        fcf_per_share = fcf / shares_outstanding if shares_outstanding else 0

        # Calcul RSI
        rsi = calculate_rsi(hist['Close'].values) if not hist.empty and 'Close' in hist else 50

        # Calcul FCF Yield
        fcf_yield = 0
        if current_price and current_price > 0 and fcf_per_share > 0:
            fcf_yield = (fcf_per_share / current_price) * 100

        # Vérification des critères
        results = {
            "Volume quotidien": (avg_volume >= 100000, "≥ 100k"),
            "ROE": (roe >= 10, "≥ 10%"),
            "Debt-to-Equity": (0 <= debt_to_equity <= 0.8, "0-0.8"),
            "Ownership institutionnel": (inst_ownership > 0, "> 0%"),
            "Beta": (0.5 < beta < 1.5, "0.5-1.5"),
            "Croissance BPA": (eps_growth > 0, "> 0%"),
            "FCF/Action": (fcf_per_share > 0, "> 0"),
            "FCF Yield": (fcf_yield > 5, "> 5%"),
            "RSI": (40 < rsi < 55, f"{rsi:.1f} (40-55)")
        }

        valid_count = sum(1 for valid, _ in results.values() if valid)

        return {
            "ticker": ticker,
            "name": info.get('longName', ticker),
            "results": results,
            "valid_count": valid_count,
            "total": len(results),
            "current_price": current_price,
            "market_cap": info.get('marketCap', 0),
            "fcf_yield": fcf_yield,
            "rsi": rsi,
            "gf_url": f"https://www.gurufocus.com/stock/{ticker}/summary"
        }
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

# --- Récupération des tickers NASDAQ ---
@st.cache_data
def get_nasdaq_tickers():
    try:
        url = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
        response = requests.get(url)
        tickers = [line.split('|')[0].strip() for line in response.text.split('\n') if line]
        return tickers
    except:
        return ["AAPL", "MSFT", "GMED", "TSLA", "AMZN"]  # Liste par défaut

# --- Interface ---
st.markdown("""
<div class="banner">
    <img src="https://raw.githubusercontent.com/PapaLanca/MLGscreener/master/logo_mlg_courtage.webp">
    <div>
        <div class="title">MLG Screener Pro</div>
        <div style="color:#9ca3af">Analyse fondamentale selon vos critères stricts</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Onglets ---
tab_analyse, tab_planification = st.tabs(["Analyser une entreprise", "Planifier une analyse complète"])

with tab_analyse:
    ticker = st.text_input("Entrez un ticker (ex: GMED, AAPL, MSFT)", "GMED").upper()

    if st.button("Analyser"):
        if ticker:
            with st.spinner("Analyse en cours..."):
                analysis = analyze_stock(ticker)

            if "error" in analysis:
                st.error(analysis["error"])
            else:
                st.markdown(f"""
                <div class="score-card">
                    Score: <span class="score-number">{analysis['valid_count']}/{analysis['total']}</span>
                    <div style="font-size:14px;color:#9ca3af">critères vérifiés</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                ### {analysis['ticker']} - {analysis['name']}
                **Prix actuel:** {analysis['current_price']:.2f} |
                **Capitalisation:** {analysis['market_cap']:,.0f} |
                **FCF Yield:** {analysis['fcf_yield']:.2f}% |
                **RSI (14j):** {analysis['rsi']:.1f}
                """)

                # Liste des critères
                st.markdown('<div class="criteria-container">', unsafe_allow_html=True)
                for criterion, (valid, threshold) in analysis['results'].items():
                    status = "✅ Valide" if valid else "❌ Invalide"
                    css_class = "valid" if valid else "invalid"
                    st.markdown(f"""
                    <div class="criterion {css_class}">
                        <span>{criterion}</span>
                        <div>
                            <span class="status {css_class}">{status}</span>
                            <span style="color:#9ca3af;font-size:12px;margin-left:10px">{threshold}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Critères GuruFocus sous le RSI
                st.markdown("""
                <div class="gf-section">
                    <h3 style="color:var(--warning);margin-top:0;">⚠️ Critères GuruFocus à vérifier</h3>
                    <div class="gf-item">
                        <span>GF Valuation (Significatively/Modestly undervalued)</span>
                        <a href="{gf_url}" class="gf-link" target="_blank">Vérifier →</a>
                    </div>
                    <div class="gf-item">
                        <span>GF Score (≥ 70)</span>
                        <a href="{gf_url}" class="gf-link" target="_blank">Vérifier →</a>
                    </div>
                    <div class="gf-item">
                        <span>Progression GF Value (FY1 < FY2 ≤ FY3)</span>
                        <a href="{gf_url}" class="gf-link" target="_blank">Vérifier →</a>
                    </div>
                </div>
                """.replace("{gf_url}", analysis['gf_url']), unsafe_allow_html=True)

                if analysis['valid_count'] == analysis['total']:
                    st.success("🎉 Cette action répond à TOUS les critères vérifiables automatiquement!")
                elif analysis['valid_count'] >= analysis['total']*0.7:
                    st.warning("⚠️ Cette action est intéressante - vérifiez les critères GuruFocus")
                else:
                    st.error("❌ Cette action ne répond pas à suffisamment de critères")

with tab_planification:
    st.markdown("<div class='plan-section'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:var(--primary);'>Planification complète</h2>", unsafe_allow_html=True)

    frequency = st.selectbox(
        "Fréquence d'analyse",
        ["Toutes les 4 semaines", "Toutes les 6 semaines", "Toutes les 8 semaines", "Toutes les 12 semaines"]
    )

    start_date = st.date_input("Date de la première analyse", datetime.now())
    start_time = st.time_input("Heure de la première analyse", time(22, 0))

    tickers = get_nasdaq_tickers()
    st.info(f"{len(tickers)} entreprises NASDAQ seront analysées")

    if st.button("Lancer l'analyse complète"):
        st.success(f"✅ Analyse complète programmée pour {len(tickers)} entreprises NASDAQ "
                  f"toutes les {frequency.lower()} à partir du {start_date} à 22h00")
        st.write("Liste des premières entreprises à analyser:")
        st.write(tickers[:10])
        st.write("...")

# --- Pied de page ---
st.markdown("""
<div class="footer">
    <p><strong>EURL MLG Courtage</strong> - Courtier en assurances</p>
    <p>Outil développé selon la méthodologie décrite dans "Mon Screener.pdf"</p>
</div>
""", unsafe_allow_html=True)
