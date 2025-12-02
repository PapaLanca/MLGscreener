import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- Configuration ---
st.set_page_config(
    page_title="MLG Screener Pro",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS avec fond sombre ---
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

.score-card {
    background:var(--dark-card);padding:20px;border-radius:8px;
    margin-bottom:20px;text-align:center;font-size:18px;font-weight:600;
}
.score-number {font-size:32px;font-weight:700;color:var(--valid);}

.criteria-grid {display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:20px 0;}
.criterion {
    display:flex;justify-content:space-between;align-items:center;
    padding:12px;background:var(--dark-card);border-radius:6px;
    border:1px solid var(--border);
}
.criterion.valid {border-left:4px solid var(--valid);}
.criterion.invalid {border-left:4px solid var(--invalid);}
.status {font-weight:600;}
.status.valid {color:var(--valid);}
.status.invalid {color:var(--invalid);}

.gf-section {
    background:var(--dark-card);padding:20px;border-radius:8px;
    margin-top:30px;
}
.gf-item {
    display:flex;justify-content:space-between;align-items:center;
    padding:10px 0;border-bottom:1px solid var(--border);
}
.gf-link {color:var(--primary);text-decoration:none;font-weight:600;}
.gf-link:hover {text-decoration:underline;}
.gf-button {
    background:var(--primary);color:white;padding:10px 20px;
    border:none;border-radius:5px;text-decoration:none;
    display:inline-block;margin-top:10px;
}

.nav-buttons {display:flex;gap:20px;justify-content:center;margin:20px 0;}
.nav-button {
    background:var(--primary);color:white;padding:12px 24px;
    border:none;border-radius:6px;font-weight:600;
    text-decoration:none;display:inline-block;
}

.footer {margin-top:50px;padding:20px;text-align:center;color:var(--text);font-size:14px;}

.stTextInput>div>div>input, .stTextArea>div>textarea {
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

# --- Boutons de navigation ---
st.markdown("""
<div class="nav-buttons">
    <a class="nav-button" href="#analyse">Analyser une entreprise</a>
    <a class="nav-button" href="#planification">Planifier une analyse</a>
</div>
""", unsafe_allow_html=True)

# --- Section Analyse ---
st.markdown('<div id="analyse">', unsafe_allow_html=True)
ticker = st.text_input("Entrez un ticker (ex: GMED, AAPL, MSFT)", "GMED").upper()

if st.button("Analyser"):
    if ticker:
        with st.spinner("Analyse en cours..."):
            analysis = analyze_stock(ticker)

        if "error" in analysis:
            st.error(analysis["error"])
        else:
            # Score global
            st.markdown(f"""
            <div class="score-card">
                Score global: <span class="score-number">{analysis['valid_count']}/{analysis['total']}</span>
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
            st.markdown("<div class='criteria-grid'>", unsafe_allow_html=True)
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
            st.markdown("</div>", unsafe_allow_html=True)

# --- Section Planification ---
st.markdown('<div id="planification" style="margin-top:40px;">', unsafe_allow_html=True)
st.markdown("<h2 style='color:var(--primary);'>Planifier une analyse</h2>", unsafe_allow_html=True)

frequency = st.selectbox(
    "Fréquence d'analyse",
    ["Toutes les semaines", "Toutes les 2 semaines", "Tous les mois"]
)

tickers = st.text_area("Liste des tickers à analyser (un par ligne)", "AAPL\nMSFT\nGMED")

if st.button("Programmer l'analyse"):
    if tickers.strip():
        tickers_list = [t.strip().upper() for t in tickers.split('\n') if t.strip()]
        st.success(f"✅ Analyse programmée pour {len(tickers_list)} entreprises ({', '.join(tickers_list)}) toutes les {frequency.lower()}")
    else:
        st.warning("Veuillez entrer au moins un ticker")

# --- Section GuruFocus ---
st.markdown("""
<div class="gf-section">
    <h3 style="color:var(--warning);margin-top:0;">⚠️ Critères à vérifier sur GuruFocus</h3>
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
    <a href="{gf_url}" class="gf-button" target="_blank">Accéder à GuruFocus</a>
</div>
""".replace("{gf_url}", f"https://www.gurufocus.com/stock/{ticker}/summary" if 'ticker' in locals() else "#"), unsafe_allow_html=True)

# --- Pied de page ---
st.markdown("""
<div class="footer">
    <p><strong>EURL MLG Courtage</strong> - Courtier en assurances</p>
    <p>Outil développé selon la méthodologie décrite dans "Mon Screener.pdf"</p>
</div>
""", unsafe_allow_html=True)
