import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- Configuration ---
st.set_page_config(page_title="MLG Screener Pro", layout="wide")

# --- CSS mis à jour ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
:root {
    --primary: #1e3a8a;
    --secondary: #3b82f6;
    --valid: #10b981;
    --invalid: #ef4444;
    --warning: #f59e0b;
}
body {font-family: 'Montserrat', sans-serif;}
.banner {display:flex;align-items:center;gap:20px;margin-bottom:30px;}
.banner img {width:180px;}
.title {color:var(--primary);font-size:24px;font-weight:600;}
.criteria {display:grid;grid-template-columns:1fr 1fr;gap:15px;margin:20px 0;}
.criterion {border-left:4px solid;padding:10px;border-radius:5px;}
.criterion.valid {border-color:var(--valid);background:rgba(16, 185, 129, 0.1);}
.criterion.invalid {border-color:var(--invalid);background:rgba(239, 68, 68, 0.1);}
.criterion.warning {border-color:var(--warning);background:rgba(245, 158, 11, 0.1);}
.metric {display:flex;justify-content:space-between;padding:8px 0;}
.metric.valid {color:var(--valid);}
.metric.invalid {color:var(--invalid);}
.metric.warning {color:var(--warning);}
.footer {margin-top:50px;padding:20px;text-align:center;color:#6b7280;font-size:14px;}
.gf-link {color:var(--primary);text-decoration:none;font-weight:600;}
.gf-link:hover {text-decoration:underline;}
</style>
""", unsafe_allow_html=True)

# --- Fonctions d'analyse ---
def get_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100./(1.+rs)

    for i in range(period, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(period-1) + upval)/period
        down = (down*(period-1) + downval)/period
        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)
    return rsi[-1]

def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="5y")

        # Calcul des métriques
        current_price = info.get('currentPrice')
        avg_volume = info.get('averageVolume', 0)
        roe = info.get('returnOnEquity', 0) * 100
        debt_to_equity = info.get('debtToEquity', 0)
        inst_ownership = info.get('institutionalOwnership', 0)
        beta = info.get('beta', 1)
        eps_growth = info.get('earningsQuarterlyGrowth', 0)
        fcf = info.get('freeCashflow', 0)
        shares_outstanding = info.get('sharesOutstanding', 1)
        fcf_per_share = fcf / shares_outstanding if shares_outstanding else 0
        market_cap = info.get('marketCap', 0)
        rsi = get_rsi(hist['Close'].values)

        # Estimation GF Value (simplifiée)
        fy1 = current_price * 0.9 if current_price else 0
        fy2 = fy1 * 1.1
        fy3 = fy2 * 1.1
        gf_progression = fy1 < fy2 <= fy3

        # Calcul du FCF Yield
        fcf_yield_valid = False
        fcf_yield = 0
        if current_price and current_price > 0 and fcf_per_share > 0:
            fcf_yield = (fcf_per_share / current_price) * 100
            fcf_yield_valid = fcf_yield > 5

        # Vérification des critères
        results = {
            "GF Valuation": ("⚠️ À analyser", "Significatively/Modestly undervalued (Vérifier sur GuruFocus)"),
            "GF Score": ("⚠️ À analyser", "≥ 70 (Vérifier sur GuruFocus)"),
            "Volume quotidien": ("✅ Valide" if avg_volume >= 100000 else "❌ Invalide", "≥ 100k"),
            "ROE": ("✅ Valide" if roe >= 10 else "❌ Invalide", "≥ 10%"),
            "Debt-to-Equity": ("✅ Valide" if 0 <= debt_to_equity <= 0.8 else "❌ Invalide", "0-0.8"),
            "Ownership institutionnel": ("✅ Valide" if inst_ownership > 0 else "❌ Invalide", "> 0%"),
            "Beta": ("✅ Valide" if 0.5 < beta < 1.5 else "❌ Invalide", "0.5-1.5"),
            "Croissance BPA": ("✅ Valide" if eps_growth > 0 else "❌ Invalide", "> 0%"),
            "FCF/Action": ("✅ Valide" if fcf_per_share > 0 else "❌ Invalide", "> 0"),
            "FCF Yield": ("✅ Valide" if fcf_yield_valid else "❌ Invalide", "> 5%"),
            "Progression GF Value": ("⚠️ À analyser", "FY1<FY2≤FY3 (Vérifier sur GuruFocus)"),
            "RSI": ("✅ Valide" if 40 < rsi < 55 else "❌ Invalide", "40-55")
        }

        valid_count = sum(1 for status, _ in results.items() if status != "⚠️ À analyser" and status == "✅ Valide")
        total_checkable = sum(1 for status, _ in results.items() if status != "⚠️ À analyser")

        return {
            "ticker": ticker,
            "name": info.get('longName', ticker),
            "results": results,
            "valid_count": valid_count,
            "total": len(results),
            "total_checkable": total_checkable,
            "current_price": current_price,
            "market_cap": market_cap,
            "fcf_yield": fcf_yield if fcf_yield_valid else 0,
            "gf_url": f"https://www.gurufocus.com/stock/{ticker}/summary"
        }
    except Exception as e:
        return {"error": str(e)}

# --- Interface ---
st.markdown("""
<div class="banner">
    <img src="https://raw.githubusercontent.com/PapaLanca/MLGscreener/master/logo_mlg_courtage.webp">
    <div>
        <div class="title">MLG Screener Pro</div>
        <div style="color:#6b7280">Analyse fondamentale selon vos 12 critères stricts</div>
    </div>
</div>
""", unsafe_allow_html=True)

ticker = st.text_input("Entrez un ticker (ex: GMED, AAPL, MSFT)", "GMED").upper()

if st.button("Analyser"):
    if ticker:
        with st.spinner("Analyse en cours..."):
            analysis = analyze_stock(ticker)

        if "error" in analysis:
            st.error(f"Erreur: {analysis['error']}")
        else:
            st.markdown(f"### {analysis['ticker']} - {analysis['name']}")
            st.markdown(f"""
            **Prix actuel:** {analysis['current_price']:.2f} |
            **Capitalisation:** {analysis['market_cap']:,.0f} |
            **FCF Yield:** {analysis['fcf_yield']:.2f}% |
            [Voir sur GuruFocus →]({analysis['gf_url']}){'' if not analysis['gf_url'] else ''}
            """, unsafe_allow_html=True)

            st.markdown("#### Résultats du screening:")
            st.progress(analysis['valid_count']/analysis['total_checkable'])

            for criterion, (status, threshold) in analysis['results'].items():
                css_class = 'valid' if status == "✅ Valide" else 'invalid' if status == "❌ Invalide" else 'warning'
                st.markdown(f"""
                <div class="criterion {css_class}">
                    <div class="metric {css_class}">
                        <span>{criterion}</span>
                        <span>{status} {f'({threshold})' if threshold else ''}</span>
                    </div>
                    {'<div style="font-size:12px;margin-top:5px;color:#6b7280">Ce critère nécessite une vérification manuelle sur GuruFocus</div>' if status == "⚠️ À analyser" else ''}
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="margin-top:20px;font-weight:600;color:{'var(--valid)' if analysis['valid_count'] == analysis['total_checkable'] else 'var(--warning)' if analysis['valid_count'] >= analysis['total_checkable']*0.7 else 'var(--invalid)'}">
                Résultat final: {analysis['valid_count']}/{analysis['total_checkable']} critères vérifiables validés
            </div>
            """, unsafe_allow_html=True)

            if analysis['valid_count'] == analysis['total_checkable']:
                st.success("🎉 Cette action répond à TOUS les critères vérifiables ! Vérifiez les critères GF sur GuruFocus")
            elif analysis['valid_count'] >= analysis['total_checkable']*0.7:
                st.warning("⚠️ Cette action est intéressante mais nécessite une vérification des critères GF sur GuruFocus")
            else:
                st.error("❌ Cette action ne répond pas à suffisamment de critères vérifiables")

# --- Pied de page ---
st.markdown("""
<div class="footer">
    <p><strong>EURL MLG Courtage</strong> - Courtier en assurances</p>
    <p>Outil développé selon la méthodologie décrite dans "Mon Screener.pdf"</p>
    <p>Les critères GF Valuation et GF Score nécessitent une vérification manuelle sur <a href="https://www.gurufocus.com" class="gf-link">GuruFocus</a></p>
</div>
""", unsafe_allow_html=True)

