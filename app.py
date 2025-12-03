import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import io
import csv
from datetime import datetime, timedelta

# --- Configuration ---
st.set_page_config(
    page_title="MLG Screener Pro",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Constantes ---
NEWS_API_AI_KEY = "51aa6af9-be5d-4f40-a853-bea7c8c6e5f0"
NEWS_API_AI_URL = "https://eventregistry.org/api/v1/article/getArticles"

# --- CSS avec fond sombre ---
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
body {font-family: 'Montserrat', sans-serif; background-color: var(--dark-bg) !important; color: var(--text) !important;}
[data-testid="stAppViewContainer"] {background-color: var(--dark-bg) !important;}

.footer {
    margin-top: 50px;
    padding: 20px;
    text-align: center;
    color: var(--text);
    font-size: 14px;
    line-height: 1.6;
    border-top: 1px solid var(--border);
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

# --- Récupération des news via NewsAPI.ai uniquement ---
@st.cache_data(ttl=3600)
def get_financial_news(ticker):
    company_mapping = {
        "AAPL": {"name": "Apple", "keywords": ["Apple", "AAPL", "iPhone", "Tim Cook"]},
        "MSFT": {"name": "Microsoft", "keywords": ["Microsoft", "MSFT", "Windows", "Azure"]},
        "GMED": {"name": "Globus Medical", "keywords": ["Globus Medical", "GMED"]},
        "TSLA": {"name": "Tesla", "keywords": ["Tesla", "TSLA", "Elon Musk", "Model 3"]},
        "AMZN": {"name": "Amazon", "keywords": ["Amazon", "AMZN", "AWS", "Jeff Bezos"]}
    }

    company = company_mapping.get(ticker, {"name": ticker, "keywords": [ticker]})

    try:
        params = {
            "action": "getArticles",
            "keyword": " OR ".join(company["keywords"]),
            "articlesPage": 1,
            "articlesCount": 5,
            "articlesSortBy": "date",
            "articlesSortByAsc": False,
            "apiKey": NEWS_API_AI_KEY,
            "resultType": "articles",
            "articlesArticleBodyLen": -1,
            "lang": "eng"
        }

        response = requests.post(NEWS_API_AI_URL, json=params, timeout=10)
        data = response.json()

        if data.get("articles") and data["articles"].get("results"):
            return [{
                'title': article["title"],
                'source': article["source"]["title"],
                'url': article["url"],
                'publishedAt': article["date"]
            } for article in data["articles"]["results"][:5]]

    except Exception as e:
        st.warning(f"Erreur lors de la récupération des actualités: {str(e)}")

    # Solution de secours: Yahoo Finance uniquement
    try:
        stock = yf.Ticker(ticker)
        yahoo_news = stock.news
        if yahoo_news:
            return [{
                'title': item['title'],
                'source': item.get('publisher', 'Yahoo Finance'),
                'url': item.get('link', '#'),
                'publishedAt': datetime.now().isoformat()
            } for item in yahoo_news[:5]]

    except Exception as e:
        st.warning(f"Erreur Yahoo Finance: {str(e)}")

    return []

# --- Analyse complète ---
def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="3mo", interval="1d")

        # Calcul des métriques
        current_price = info.get('currentPrice', 'N/A')
        avg_volume = info.get('averageVolume', 0)
        roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
        debt_to_equity = info.get('debtToEquity', 0)
        inst_ownership = info.get('institutionalOwnership', 0) * 100 if info.get('institutionalOwnership') else 0
        beta = info.get('beta', 'N/A')
        eps_growth = info.get('earningsQuarterlyGrowth', 0) * 100 if info.get('earningsQuarterlyGrowth') else 0
        fcf = info.get('freeCashflow', 0)
        shares_outstanding = info.get('sharesOutstanding', 1)
        fcf_per_share = fcf / shares_outstanding if shares_outstanding else 0

        # Calcul RSI
        rsi = calculate_rsi(hist['Close'].values) if not hist.empty and 'Close' in hist else 50

        # Calcul FCF Yield
        fcf_yield = 0
        if current_price and current_price > 0 and fcf_per_share > 0:
            fcf_yield = (fcf_per_share / current_price) * 100

        results = {
            "Volume quotidien": {"valid": avg_volume >= 100000, "threshold": "≥ 100k", "value": f"{avg_volume:,.0f}"},
            "ROE": {"valid": roe >= 10, "threshold": "≥ 10%", "value": f"{roe:.1f}%"},
            "Debt-to-Equity": {"valid": 0 <= debt_to_equity <= 0.8, "threshold": "0-0.8", "value": f"{debt_to_equity:.2f}"},
            "Ownership institutionnel": {"valid": inst_ownership > 0, "threshold": "> 0%", "value": f"{inst_ownership:.1f}%"},
            "Beta": {"valid": 0.5 < beta < 1.5 if isinstance(beta, (int, float)) else False, "threshold": "0.5-1.5", "value": f"{beta:.2f}" if isinstance(beta, (int, float)) else "N/A"},
            "Croissance BPA": {"valid": eps_growth > 0, "threshold": "> 0%", "value": f"{eps_growth:.1f}%"},
            "FCF/Action": {"valid": fcf_per_share > 0, "threshold": "> 0", "value": f"{fcf_per_share:.2f}"},
            "FCF Yield": {"valid": fcf_yield > 5, "threshold": "> 5%", "value": f"{fcf_yield:.1f}%"},
            "RSI": {"valid": 40 < rsi < 55, "threshold": "40-55", "value": f"{rsi:.1f}"}
        }

        holders = []
        try:
            holders_data = stock.institutional_holders
            if holders_data is not None and not holders_data.empty:
                holders = [{
                    'name': row['Holder'],
                    'shares': row['Shares'],
                    'dateReported': row['Date Reported'],
                    'pctHeld': row['% Out']
                } for _, row in holders_data.head(5).iterrows()]
        except:
            pass

        return {
            "ticker": ticker,
            "name": info.get('longName', ticker),
            "results": results,
            "valid_count": sum(1 for data in results.values() if data["valid"]),
            "total": len(results),
            "current_price": current_price,
            "market_cap": info.get('marketCap', 0),
            "fcf_yield": fcf_yield,
            "rsi": rsi,
            "gf_url": f"https://www.gurufocus.com/stock/{ticker}/summary",
            "holders": holders
        }
    except Exception as e:
        return {"error": f"Erreur: {str(e)}"}

# --- Génération CSV ---
def generate_csv(analysis):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Critère", "Statut", "Seuil", "Valeur"])
    for criterion, result in analysis['results'].items():
        writer.writerow([
            criterion,
            "✅ Valide" if result["valid"] else "❌ Invalide",
            result["threshold"],
            result["value"]
        ])
    if 'holders' in analysis and analysis['holders']:
        writer.writerow([])
        writer.writerow(["Principaux actionnaires institutionnels"])
        writer.writerow(["Nom", "Actions", "Date", "% Détenu"])
        for holder in analysis['holders']:
            writer.writerow([
                holder['name'],
                holder['shares'],
                holder['dateReported'],
                f"{holder['pctHeld']:.2f}%"
            ])
    return output.getvalue().encode('utf-8')

# --- Interface ---
st.markdown("""
<div style="display:flex;align-items:center;gap:20px;margin-bottom:30px;">
    <img src="https://raw.githubusercontent.com/PapaLanca/MLGscreener/master/logo_mlg_courtage.webp" width="180px">
    <div>
        <div style="color:#4f81bd;font-size:24px;font-weight:600;">MLG Screener Pro</div>
        <div style="color:#9ca3af">Analyse fondamentale complète</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab_analyse, tab_planification = st.tabs(["Analyser une entreprise", "Planifier une analyse complète"])

with tab_analyse:
    ticker = st.text_input("Entrez un ticker (ex: AAPL, MSFT, GMED)", "AAPL").upper()

    if st.button("Analyser"):
        if ticker:
            with st.spinner("Analyse en cours..."):
                analysis = analyze_stock(ticker)
                news = get_financial_news(ticker)

            if "error" in analysis:
                st.error(analysis["error"])
            else:
                st.markdown(f"""
                <div style="background:#334155;padding:20px;border-radius:8px;margin-bottom:20px;text-align:center;">
                    Score: <span style="font-size:32px;font-weight:700;color:#10b981;">{analysis['valid_count']}/{analysis['total']}</span>
                    <div style="font-size:14px;color:#9ca3af;">critères vérifiés</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"### {analysis['ticker']} - {analysis['name']}")
                st.markdown(f"**Prix actuel:** {analysis['current_price']} | **Capitalisation:** {analysis['market_cap']:,.0f} | **FCF Yield:** {analysis['fcf_yield']:.2f}% | **RSI (14j):** {analysis['rsi']:.1f}")

                for criterion, result in analysis['results'].items():
                    status = "✅ Valide" if result["valid"] else "❌ Invalide"
                    color = "#10b981" if result["valid"] else "#ef4444"
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:12px;background:#334155;border-radius:6px;border:1px solid #475569;margin-bottom:8px;border-left:4px solid {color};">
                        <span>{criterion}</span>
                        <div style="display:flex;flex-direction:column;align-items:flex-end;">
                            <span style="font-weight:600;color:{color};">{status}</span>
                            <span style="font-size:12px;color:#9ca3af;margin-top:2px;">{result["value"]} ({result["threshold"]})</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                if analysis['holders']:
                    st.markdown("<div style='background:#334155;padding:20px;border-radius:8px;margin-top:20px;'>", unsafe_allow_html=True)
                    st.markdown("<h3 style='color:#4f81bd;margin-top:0;'>🏛️ Principaux actionnaires institutionnels</h3>", unsafe_allow_html=True)
                    for holder in analysis['holders']:
                        st.markdown(f"""
                        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #475569;">
                            <span>{holder['name']}</span>
                            <span>{holder['shares']:,.0f} actions ({holder['pctHeld']:.1f}%)</span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("""
                <div style="background:#334155;padding:20px;border-radius:8px;margin-top:20px;">
                    <h3 style="color:#f59e0b;margin-top:0;">⚠️ Critères GuruFocus à vérifier</h3>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #475569;">
                    <span>GF Valuation (Significatively/Modestly undervalued)</span>
                    <a href="{analysis['gf_url']}" style="color:#4f81bd;text-decoration:none;" target="_blank">Vérifier →</a>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<div style='background:#334155;padding:20px;border-radius:8px;margin-top:30px;'>", unsafe_allow_html=True)
                st.markdown("<h3 style='color:#4f81bd;'>📰 Actualités financières récentes</h3>", unsafe_allow_html=True)

                if news:
                    for article in news:
                        st.markdown(f"""
                        <div style="border-bottom:1px solid #475569;padding:15px 0;">
                            <div style="color:var(--text);font-weight:600;margin-bottom:5px;">{article['title']}</div>
                            <div style="color:#9ca3af;font-size:12px;">
                                {article['source']} • {datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d/%m/%Y %H:%M') if 'publishedAt' in article else 'Date inconnue'}
                                <a href="{article['url']}" style="color:#4f81bd;" target="_blank">Lire →</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="color:#9ca3af;">
                        Aucune actualité récente trouvée.<br>
                        Nous utilisons Yahoo Finance comme source alternative.
                    </div>
                    """, unsafe_allow_html=True)

# --- Pied de page exactement comme demandé ---
st.markdown("""
<div style="margin-top:50px;padding:20px;text-align:center;color:var(--text);font-size:14px;line-height:1.6;border-top:1px solid var(--border);">
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
