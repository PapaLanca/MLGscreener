import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import io
import csv
import time
import json
import os
from datetime import datetime

# --- Configuration ---
st.set_page_config(
    page_title="MLG Screener Pro",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Constantes ---
DAILY_LIMIT = 500  # Limite quotidienne Alpha Vantage
CACHE_FILE = "analysis_progress.json"

# --- CSS avec police augmentée ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght=400;600;700&display=swap');
:root {
    --primary: #4f81bd;
    --valid: #10b981;
    --invalid: #ef4444;
    --dark-bg: #1e293b;
    --dark-card: #334155;
    --text: #e2e8f0;
    --border: #475569;
}
body {
    font-family: 'Montserrat', sans-serif;
    background-color: var(--dark-bg) !important;
    color: var(--text) !important;
    font-size: 15px !important;
}
.stButton>button {
    font-size: 15px !important;
}
.progress-container {
    margin: 20px 0;
    background: #334155;
    padding: 20px;
    border-radius: 8px;
}
.progress-bar {
    height: 20px;
    background: #475569;
    border-radius: 10px;
    margin: 10px 0;
}
.progress {
    height: 100%;
    background: #4f81bd;
    border-radius: 10px;
    width: 0%;
    transition: width 0.3s;
}
.footer {
    margin-top: 50px;
    padding: 20px;
    text-align: center;
    color: var(--text);
    font-size: 15px !important;
    line-height: 1.6;
    border-top: 1px solid var(--border);
}
</style>
""", unsafe_allow_html=True)

# --- Gestion de la progression ---
def load_progress():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {
        "completed": [],
        "current_day": datetime.now().strftime("%Y-%m-%d"),
        "last_index": 0,
        "results": []
    }

def save_progress(progress):
    with open(CACHE_FILE, 'w') as f:
        json.dump(progress, f)

def reset_if_new_day(progress):
    today = datetime.now().strftime("%Y-%m-%d")
    if progress["current_day"] != today:
        progress["completed"] = []
        progress["last_index"] = 0
        progress["current_day"] = today
        save_progress(progress)
    return progress

# --- Fonction RSI ---
def calculate_rsi(prices, period=14):
    if len(prices) < period:
        return 50
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

# --- Analyse d'un ticker ---
@st.cache_data(ttl=86400, show_spinner=False)
def analyze_ticker(ticker):
    try:
        time.sleep(2)  # Délai pour respecter les limites

        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="3mo", interval="1d")

        # Calcul des métriques
        current_price = info.get('currentPrice', 0)
        avg_volume = info.get('averageVolume', 0)
        roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
        debt_to_equity = info.get('debtToEquity', 0)
        inst_ownership = info.get('institutionalOwnership', 0) * 100 if info.get('institutionalOwnership') else 0
        beta = info.get('beta', 1)
        eps_growth = info.get('earningsQuarterlyGrowth', 0) * 100 if info.get('earningsQuarterlyGrowth') else 0
        fcf = info.get('freeCashflow', 0)
        shares_outstanding = info.get('sharesOutstanding', 1)
        fcf_per_share = fcf / shares_outstanding if shares_outstanding else 0

        # Calcul RSI
        rsi = 50
        if not hist.empty and 'Close' in hist:
            rsi = calculate_rsi(hist['Close'].values)

        # Calcul FCF Yield
        fcf_yield = 0
        if current_price > 0 and fcf_per_share > 0:
            fcf_yield = (fcf_per_share / current_price) * 100

        # Évaluation des critères
        results = {
            "Volume quotidien": {"valid": avg_volume >= 100000, "value": f"{avg_volume:,.0f}",
                               "description": "Un volume quotidien élevé indique une bonne liquidité, essentielle pour entrer/sortir facilement d'une position."},
            "ROE": {"valid": roe >= 10, "value": f"{roe:.1f}%",
                   "description": "Le ROE (Return on Equity) mesure la rentabilité des capitaux propres. Un ROE ≥ 10% indique une bonne performance."},
            "Debt-to-Equity": {"valid": 0 <= debt_to_equity <= 0.8, "value": f"{debt_to_equity:.2f}",
                             "description": "Un ratio dettes/capitaux propres ≤ 0.8 montre une entreprise peu endettée, donc moins risquée."},
            "Ownership institutionnel": {"valid": inst_ownership > 0, "value": f"{inst_ownership:.1f}%",
                                         "description": "La présence d'investisseurs institutionnels est un gage de confiance dans l'entreprise."},
            "Beta": {"valid": 0.5 < beta < 1.5, "value": f"{beta:.2f}",
                    "description": "Un beta entre 0.5 et 1.5 indique une volatilité modérée par rapport au marché."},
            "Croissance BPA": {"valid": eps_growth > 0, "value": f"{eps_growth:.1f}%",
                               "description": "Une croissance du BPA (Bénéfice Par Action) positive montre une entreprise en expansion."},
            "FCF/Action": {"valid": fcf_per_share > 0, "value": f"{fcf_per_share:.2f}",
                          "description": "Un Free Cash Flow par action positif indique que l'entreprise génère des liquidités."},
            "FCF Yield": {"valid": fcf_yield > 5, "value": f"{fcf_yield:.1f}%",
                         "description": "Un FCF Yield > 5% montre une bonne génération de cash flow par rapport à la capitalisation."},
            "RSI": {"valid": 40 < rsi < 55, "value": f"{rsi:.1f}",
                    "description": "Un RSI entre 40 et 55 indique que le titre n'est ni suracheté ni survendu."}
        }

        valid_count = sum(1 for data in results.values() if data["valid"])

        return {
            "ticker": ticker,
            "name": info.get('longName', ticker),
            "score": f"{valid_count}/9",
            "valid_count": valid_count,
            "current_price": current_price,
            "market_cap": info.get('marketCap', 0),
            "results": results
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

# --- Analyse complète avec limite quotidienne ---
def run_bulk_analysis(tickers):
    progress = reset_if_new_day(load_progress())
    completed = progress["completed"]
    results = progress.get("results", [])
    start_idx = progress["last_index"]

    # Vérification de la limite quotidienne
    if len(completed) >= DAILY_LIMIT:
        st.warning(f"Limite quotidienne de {DAILY_LIMIT} requêtes atteinte. Reprenez demain.")
        return results

    # Calcul du nombre de tickers restants pour aujourd'hui
    remaining = DAILY_LIMIT - len(completed)
    end_idx = min(start_idx + remaining, len(tickers))

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(start_idx, end_idx):
        ticker = tickers[i]
        status_text.text(f"Analyse de {ticker} ({i+1}/{len(tickers)})... {len(completed)+1}/{DAILY_LIMIT} aujourd'hui")
        result = analyze_ticker(ticker)
        results.append(result)
        completed.append(ticker)
        progress["last_index"] = i + 1
        progress["completed"] = completed
        progress["results"] = results
        save_progress(progress)
        progress_bar.progress((i+1)/len(tickers))

    status_text.text(f"Analyse terminée pour aujourd'hui! {len(completed)} tickers analysés.")
    return results

# --- Génération CSV ---
def generate_csv(results):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Ticker", "Nom", "Score", "Prix", "Capitalisation"] +
                  [f"Critère: {c}" for c in results[0]["results"].keys()] +
                  ["Description"])

    for result in results:
        if "error" in result:
            writer.writerow([result["ticker"], "Erreur", "", "", ""] + [""]*(len(results[0]["results"])+1))
            continue

        for criterion, data in result["results"].items():
            writer.writerow([
                result["ticker"],
                result["name"],
                result["score"],
                result["current_price"],
                result["market_cap"],
                f"{criterion}: {data['value']} ({'✅' if data['valid'] else '❌'})",
                data["description"]
            ])

    return output.getvalue().encode('utf-8')

# --- Chargement des tickers NASDAQ ---
@st.cache_data
def load_nasdaq_tickers():
    try:
        url = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
        df = pd.read_csv(url, sep='|')
        return df['Symbol'].tolist()
    except:
        return ["AAPL", "MSFT", "GMED", "TSLA", "AMZN", "GOOGL", "META", "NVDA"]

# --- Interface ---
st.markdown("""
<div style="display:flex;align-items:center;gap:20px;margin-bottom:30px;">
    <img src="https://raw.githubusercontent.com/PapaLanca/MLGscreener/master/logo_mlg_courtage.webp" width="180px">
    <div>
        <div style="color:#4f81bd;font-size:25px;font-weight:600;">MLG Screener Pro</div>
        <div style="color:#9ca3af;font-size:15px;">Analyse fondamentale complète</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab_analyse, tab_planification = st.tabs(["Analyser une entreprise", "Analyse complète"])

with tab_analyse:
    ticker = st.text_input("Entrez un ticker (ex: AAPL, MSFT, GMED)", "AAPL")

    if st.button("Analyser"):
        if ticker:
            with st.spinner("Analyse en cours..."):
                result = analyze_ticker(ticker.upper())

            if "error" in result:
                st.error(f"Erreur: {result['error']}")
            else:
                st.markdown(f"""
                <div style="background:#334155;padding:20px;border-radius:8px;margin-bottom:20px;text-align:center;">
                    Score: <span style="font-size:33px;font-weight:700;color:#10b981;">{result['score']}</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"### {result['ticker']} - {result['name']}")
                st.markdown(f"**Prix actuel:** {result['current_price']} | **Capitalisation:** {result['market_cap']:,.0f}")

                for criterion, data in result["results"].items():
                    status = "✅ Valide" if data["valid"] else "❌ Invalide"
                    color = "#10b981" if data["valid"] else "#ef4444"
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:12px;background:#334155;border-radius:6px;border:1px solid #475569;margin-bottom:8px;border-left:4px solid {color};">
                        <span style="font-size:15px;">{criterion}</span>
                        <div style="display:flex;flex-direction:column;align-items:flex-end;">
                            <span style="font-weight:600;color:{color};font-size:15px;">{status}</span>
                            <span style="font-size:13px;color:#9ca3af;margin-top:2px;">{data['value']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Bouton d'export CSV avec explications
                csv = generate_csv([result])
                st.download_button(
                    label="Exporter en CSV (avec explications)",
                    data=csv,
                    file_name=f"analyse_{result['ticker']}.csv",
                    mime="text/csv",
                    key="export_csv"
                )

with tab_planification:
    st.markdown("<div style='background:#334155;padding:20px;border-radius:8px;margin-top:30px;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#4f81bd;font-size:17px;'>Analyse complète des tickers NASDAQ</h2>", unsafe_allow_html=True)

    tickers = load_nasdaq_tickers()
    progress = reset_if_new_day(load_progress())

    st.write(f"Progression: {len(progress['completed'])}/{len(tickers)} tickers analysés")
    st.write(f"Limite quotidienne: {DAILY_LIMIT} requêtes (Alpha Vantage)")

    if st.button("Lancer/Reprendre l'analyse"):
        results = run_bulk_analysis(tickers)

        # Filtrer les tickers avec score ≥ 6/9
        good_results = [r for r in results if "score" in r and int(r["score"].split("/")[0]) >= 6]

        if good_results:
            csv = generate_csv(good_results)
            st.download_button(
                label="Télécharger les résultats (score ≥ 6/9)",
                data=csv,
                file_name=f"top_tickers_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

            st.markdown("### Tickers avec score ≥ 6/9")
            for result in good_results:
                st.write(f"{result['ticker']} - {result['name']} ({result['score']})")

# --- Pied de page complet avec disclaimer ---
st.markdown("""
<div style="margin-top:50px;padding:20px;text-align:center;color:var(--text);font-size:15px;line-height:1.6;border-top:1px solid var(--border);">
    <div style="font-weight:600;margin-bottom:15px;">MLG Screener</div>

    <div style="margin-bottom:15px;">
        Proposé gratuitement par <strong>EURL MLG Courtage</strong><br>
        Courtier en assurances agréé ORIAS n°24002055<br>
        SIRET : 98324762800016<br>
        <a href="https://www.mlgcourtage.fr" style="color:var(--primary);text-decoration:none;" target="_blank">www.mlgcourtage.fr</a>
    </div>

    <div style="text-align:left;max-width:800px;margin:0 auto 20px;color:#9ca3af;">
        <strong>Disclaimer :</strong><br><br>
        MLG Screener est un outil d'analyse financière conçu pour aider les investisseurs à identifier des opportunités selon une méthodologie rigoureuse.<br>
        Les informations présentées sont basées sur des données publiques et ne constituent en aucun cas un conseil en investissement.<br>
        Tout investissement comporte des risques, y compris la perte en capital. Les performances passées ne préjugent pas des performances futures.<br>
        Nous vous recommandons vivement de consulter un conseiller financier indépendant avant toute décision d'investissement.<br><br>

        <strong>Explications des indicateurs :</strong><br>
        - <strong>Volume quotidien</strong> : Un volume élevé indique une bonne liquidité.<br>
        - <strong>ROE</strong> : Mesure la rentabilité des capitaux propres (≥10% = bonne performance).<br>
        - <strong>Debt-to-Equity</strong> : Ratio dettes/capitaux propres (≤0.8 = peu endetté).<br>
        - <strong>Ownership institutionnel</strong> : Présence d'investisseurs institutionnels = gage de confiance.<br>
        - <strong>Beta</strong> : Mesure la volatilité par rapport au marché (0.5-1.5 = volatilité modérée).<br>
        - <strong>Croissance BPA</strong> : Croissance du bénéfice par action (>0% = entreprise en expansion).<br>
        - <strong>FCF/Action</strong> : Free Cash Flow par action (>0 = génération de liquidités).<br>
        - <strong>FCF Yield</strong> : Free Cash Flow Yield (>5% = bonne génération de cash flow).<br>
        - <strong>RSI</strong> : Indice de force relative (40-55 = ni suracheté ni survendu).
    </div>

    <div style="font-size:12px;color:#6b7280;">
        © 2025 EURL MLG Courtage - Tous droits réservés
    </div>
</div>
""", unsafe_allow_html=True)

