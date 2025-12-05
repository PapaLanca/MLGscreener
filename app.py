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
DAILY_LIMIT = 500
CACHE_FILE = "analysis_progress.json"

# --- CSS ---
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
    --missing: #f59e0b;
}
body {
    font-family: 'Montserrat', sans-serif;
    background-color: var(--dark-bg) !important;
    color: var(--text) !important;
    font-size: 15px !important;
}
.criterion-card {
    background: var(--dark-card);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
    border-left: 4px solid var(--border);
}
.criterion-card.valid {
    border-left-color: var(--valid);
}
.criterion-card.invalid {
    border-left-color: var(--invalid);
}
.criterion-card.missing {
    border-left-color: var(--missing);
}
.criterion-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
}
.criterion-details {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    font-size: 14px;
}
.gf-section {
    background: var(--dark-card);
    padding: 20px;
    border-radius: 8px;
    margin-top: 20px;
}
.gf-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
}
.gf-item:last-child {
    border-bottom: none;
}
.export-buttons {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-top: 20px;
}
.missing-data {
    color: var(--missing);
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

# --- Définition des critères ---
CRITERIA_DEFINITIONS = {
    "Volume quotidien": {"objectif": "≥ 100k", "description": "Un volume quotidien élevé indique une bonne liquidité"},
    "ROE": {"objectif": "≥ 10%", "description": "ROE ≥ 10% indique une bonne rentabilité"},
    "Debt-to-Equity": {"objectif": "0-0.8", "description": "Ratio dettes/capitaux propres ≤ 0.8 = peu endetté"},
    "Ownership institutionnel": {"objectif": "> 0%", "description": "Présence d'investisseurs institutionnels = gage de confiance"},
    "Beta": {"objectif": "0.5-1.5", "description": "Beta entre 0.5 et 1.5 = volatilité modérée"},
    "Croissance BPA": {"objectif": "> 0%", "description": "Croissance BPA positive = entreprise en expansion"},
    "FCF/Action": {"objectif": "> 0", "description": "FCF/Action positif = génération de liquidités"},
    "FCF Yield": {"objectif": "> 5%", "description": "FCF Yield > 5% = bonne génération de cash flow"},
    "RSI": {"objectif": "40-55", "description": "RSI entre 40 et 55 = ni suracheté ni survendu"}
}

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

# --- Analyse d'un ticker avec gestion des données manquantes ---
@st.cache_data(ttl=86400)
def analyze_ticker(ticker):
    try:
        time.sleep(2)  # Respect des limites API

        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="3mo", interval="1d")

        # Récupération des données avec gestion des valeurs manquantes
        current_price = info.get('currentPrice', None)
        avg_volume = info.get('averageVolume', None)
        roe = info.get('returnOnEquity', None)
        if roe is not None:
            roe = roe * 100
        debt_to_equity = info.get('debtToEquity', None)
        inst_ownership = info.get('institutionalOwnership', None)
        if inst_ownership is not None:
            inst_ownership = inst_ownership * 100
        beta = info.get('beta', None)
        eps_growth = info.get('earningsQuarterlyGrowth', None)
        if eps_growth is not None:
            eps_growth = eps_growth * 100
        fcf = info.get('freeCashflow', None)
        shares_outstanding = info.get('sharesOutstanding', None)
        market_cap = info.get('marketCap', None)

        # Calcul RSI (avec vérification des données)
        rsi = 50
        if not hist.empty and 'Close' in hist:
            rsi = calculate_rsi(hist['Close'].values)

        # Calcul FCF/Action et FCF Yield (avec vérification)
        fcf_per_share = None
        fcf_yield = 0
        if fcf is not None and shares_outstanding is not None and shares_outstanding > 0:
            fcf_per_share = fcf / shares_outstanding
            if current_price is not None and current_price > 0 and fcf_per_share > 0:
                fcf_yield = (fcf_per_share / current_price) * 100

        # Évaluation des critères avec gestion des données manquantes
        results = {}
        for criterion, definition in CRITERIA_DEFINITIONS.items():
            valid = None
            value = "Donnée manquante"
            card_class = "missing"

            if criterion == "Volume quotidien":
                if avg_volume is not None:
                    valid = avg_volume >= 100000
                    value = f"{avg_volume:,.0f}"
                    card_class = "valid" if valid else "invalid"
            elif criterion == "ROE":
                if roe is not None:
                    valid = roe >= 10
                    value = f"{roe:.1f}%"
                    card_class = "valid" if valid else "invalid"
            elif criterion == "Debt-to-Equity":
                if debt_to_equity is not None:
                    valid = 0 <= debt_to_equity <= 0.8
                    value = f"{debt_to_equity:.2f}"
                    card_class = "valid" if valid else "invalid"
            elif criterion == "Ownership institutionnel":
                if inst_ownership is not None:
                    valid = inst_ownership > 0
                    value = f"{inst_ownership:.1f}%"
                    card_class = "valid" if valid else "invalid"
            elif criterion == "Beta":
                if beta is not None:
                    valid = 0.5 < beta < 1.5
                    value = f"{beta:.2f}"
                    card_class = "valid" if valid else "invalid"
            elif criterion == "Croissance BPA":
                if eps_growth is not None:
                    valid = eps_growth > 0
                    value = f"{eps_growth:.1f}%"
                    card_class = "valid" if valid else "invalid"
            elif criterion == "FCF/Action":
                if fcf_per_share is not None:
                    valid = fcf_per_share > 0
                    value = f"{fcf_per_share:.2f}"
                    card_class = "valid" if valid else "invalid"
            elif criterion == "FCF Yield":
                if fcf_yield > 0:
                    valid = fcf_yield > 5
                    value = f"{fcf_yield:.1f}%"
                    card_class = "valid" if valid else "invalid"
            elif criterion == "RSI":
                valid = 40 < rsi < 55
                value = f"{rsi:.1f}"
                card_class = "valid" if valid else "invalid"

            results[criterion] = {
                "valid": valid,
                "value": value,
                "objectif": definition["objectif"],
                "description": definition["description"],
                "card_class": card_class
            }

        # Calcul du score (seulement pour les critères avec données disponibles)
        valid_count = sum(1 for data in results.values() if data["valid"] is not None and data["valid"])

        return {
            "ticker": ticker,
            "name": info.get('longName', ticker),
            "score": f"{valid_count}/9",
            "valid_count": valid_count,
            "current_price": current_price if current_price is not None else "N/A",
            "market_cap": market_cap if market_cap is not None else "N/A",
            "results": results,
            "gf_url": f"https://www.gurufocus.com/stock/{ticker}/summary"
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

# --- Génération CSV ---
def generate_csv(results):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Ticker", "Nom", "Score", "Prix", "Capitalisation"] +
                  ["Critère", "Objectif", "Résultat", "Statut", "Description"] * len(CRITERIA_DEFINITIONS))

    for result in results:
        if "error" in result:
            writer.writerow([result["ticker"], "Erreur", "", "", ""])
            continue

        row = [
            result["ticker"],
            result["name"],
            result["score"],
            result["current_price"],
            result["market_cap"]
        ]

        for criterion, data in result["results"].items():
            status = "✅ Valide" if data["valid"] else "❌ Invalide" if data["valid"] is not None else "Donnée manquante"
            row.extend([
                criterion,
                data["objectif"],
                data["value"],
                status,
                data["description"]
            ])

        writer.writerow(row)

    return output.getvalue().encode('utf-8')

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
                    <div style="font-size:15px;color:#9ca3af;">{result['valid_count']} critères validés sur 9</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"### {result['ticker']} - {result['name']}")
                st.markdown(f"**Prix actuel:** {result['current_price']} | **Capitalisation:** {result['market_cap']}")

                # Affichage détaillé des critères
                for criterion, data in result["results"].items():
                    status = "✅ Valide" if data["valid"] else "❌ Invalide" if data["valid"] is not None else "<span class='missing-data'>Donnée manquante</span>"
                    color = "#10b981" if data["valid"] else "#ef4444" if data["valid"] is not None else "#f59e0b"
                    card_class = data["card_class"]

                    st.markdown(f"""
                    <div class="criterion-card {card_class}">
                        <div class="criterion-header">
                            <span style="font-weight:600;font-size:16px;">{criterion}</span>
                            <span style="color:{color};font-weight:600;">{status}</span>
                        </div>
                        <div class="criterion-details">
                            <div><strong>Objectif:</strong> {data['objectif']}</div>
                            <div><strong>Résultat:</strong> {data['value']}</div>
                            <div><strong>Statut:</strong> <span style="color:{color}">{status}</span></div>
                        </div>
                        <div style="font-size:13px;color:#9ca3af;margin-top:8px;">
                            {data['description']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Section GuruFocus COMPLÈTE
                st.markdown(f"""
                <div class="gf-section">
                    <h3 style="color:#f59e0b;margin-top:0;font-size:17px;">⚠️ Critères GuruFocus à vérifier</h3>
                    <div class="gf-item">
                        <span>GF Valuation (Significatively/Modestly undervalued)</span>
                        <a href="{result['gf_url']}" style="color:#4f81bd;text-decoration:none;" target="_blank">Vérifier →</a>
                    </div>
                    <div class="gf-item">
                        <span>GF Score (≥ 70)</span>
                        <a href="{result['gf_url']}" style="color:#4f81bd;text-decoration:none;" target="_blank">Vérifier →</a>
                    </div>
                    <div class="gf-item">
                        <span>Progression GF Value (FY1 < FY2 ≤ FY3)</span>
                        <a href="{result['gf_url']}" style="color:#4f81bd;text-decoration:none;" target="_blank">Vérifier →</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Bouton d'export sous les critères GuruFocus
                st.markdown('<div class="export-buttons">', unsafe_allow_html=True)
                csv = generate_csv([result])
                st.download_button(
                    label="Exporter en CSV",
                    data=csv,
                    file_name=f"analyse_{result['ticker']}.csv",
                    mime="text/csv"
                )
                st.markdown('</div>', unsafe_allow_html=True)

with tab_planification:
    # Code pour l'analyse complète (à compléter si nécessaire)
    pass

# --- Pied de page exact ---
st.markdown("""
<div style="margin-top:50px;padding:20px;text-align:center;color:var(--text);font-size:15px;line-height:1.6;border-top:1px solid var(--border);">
MLG Screener

Proposé gratuitement par EURL MLG Courtage
Courtier en assurances agréé ORIAS n°24002055
SIRET : 98324762800016
www.mlgcourtage.fr

MLG Screener est un outil d'analyse financière conçu pour aider les investisseurs à identifier des opportunités selon une méthodologie rigoureuse.
Les informations présentées sont basées sur des données publiques et ne constituent en aucun cas un conseil en investissement.
Tout investissement comporte des risques, y compris la perte en capital. Les performances passées ne préjugent pas des performances futures.
Nous vous recommandons vivement de consulter un conseiller financier indépendant avant toute décision d'investissement.

© 2025 EURL MLG Courtage - Tous droits réservés
</div>
""", unsafe_allow_html=True)
