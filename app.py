import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import io
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- Configuration ---
st.set_page_config(
    page_title="MLG Screener Pro",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS avec fond sombre et police augmentée ---
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
[data-testid="stAppViewContainer"] {background-color: var(--dark-bg) !important;}
.stButton>button {font-size: 15px !important;}
.footer {font-size: 15px !important;}
.export-buttons {display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;}
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
            "Volume quotidien": {"valid": avg_volume >= 100000, "threshold": "≥ 100k", "value": f"{avg_volume:,.0f}",
                                "description": "Un volume quotidien élevé indique une bonne liquidité, essentielle pour entrer/sortir facilement d'une position."},
            "ROE": {"valid": roe >= 10, "threshold": "≥ 10%", "value": f"{roe:.1f}%",
                   "description": "Le ROE (Return on Equity) mesure la rentabilité des capitaux propres. Un ROE ≥ 10% indique une bonne performance."},
            "Debt-to-Equity": {"valid": 0 <= debt_to_equity <= 0.8, "threshold": "0-0.8", "value": f"{debt_to_equity:.2f}",
                              "description": "Un ratio dettes/capitaux propres ≤ 0.8 montre une entreprise peu endettée, donc moins risquée."},
            "Ownership institutionnel": {"valid": inst_ownership > 0, "threshold": "> 0%", "value": f"{inst_ownership:.1f}%",
                                         "description": "La présence d'investisseurs institutionnels est un gage de confiance dans l'entreprise."},
            "Beta": {"valid": 0.5 < beta < 1.5 if isinstance(beta, (int, float)) else False, "threshold": "0.5-1.5", "value": f"{beta:.2f}" if isinstance(beta, (int, float)) else "N/A",
                    "description": "Un beta entre 0.5 et 1.5 indique une volatilité modérée par rapport au marché."},
            "Croissance BPA": {"valid": eps_growth > 0, "threshold": "> 0%", "value": f"{eps_growth:.1f}%",
                               "description": "Une croissance du BPA (Bénéfice Par Action) positive montre une entreprise en expansion."},
            "FCF/Action": {"valid": fcf_per_share > 0, "threshold": "> 0", "value": f"{fcf_per_share:.2f}",
                          "description": "Un Free Cash Flow par action positif indique que l'entreprise génère des liquidités."},
            "FCF Yield": {"valid": fcf_yield > 5, "threshold": "> 5%", "value": f"{fcf_yield:.1f}%",
                         "description": "Un FCF Yield > 5% montre une bonne génération de cash flow par rapport à la capitalisation."},
            "RSI": {"valid": 40 < rsi < 55, "threshold": "40-55", "value": f"{rsi:.1f}",
                    "description": "Un RSI entre 40 et 55 indique que le titre n'est ni suracheté ni survendu."}
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

# --- Génération PDF avec explications ---
def generate_pdf(analysis):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Titre
    elements.append(Paragraph(f"Rapport d'analyse - {analysis['ticker']} - {analysis['name']}", styles['Title']))
    elements.append(Spacer(1, 12))

    # Score
    elements.append(Paragraph(f"Score: {analysis['valid_count']}/{analysis['total']}", styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Métriques principales
    elements.append(Paragraph(f"Prix actuel: {analysis['current_price']} | Capitalisation: {analysis['market_cap']:,.0f} | FCF Yield: {analysis['fcf_yield']:.2f}% | RSI: {analysis['rsi']:.1f}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Tableau des critères avec explications
    data = [["Critère", "Statut", "Valeur", "Seuil", "Explication"]]
    for criterion, result in analysis['results'].items():
        status = "Valide" if result["valid"] else "Invalide"
        data.append([
            criterion,
            status,
            result["value"],
            result["threshold"],
            result["description"]
        ])

    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 24))

    # Actionnaires institutionnels
    if analysis['holders']:
        elements.append(Paragraph("Principaux actionnaires institutionnels:", styles['Heading3']))
        holder_data = [["Nom", "Actions", "% Détenu", "Date"]]
        for holder in analysis['holders']:
            holder_data.append([
                holder['name'],
                f"{holder['shares']:,.0f}",
                f"{holder['pctHeld']:.1f}%",
                holder['dateReported']
            ])
        holder_table = Table(holder_data)
        holder_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(holder_table)

    # Lien GuruFocus
    elements.append(Spacer(1, 24))
    elements.append(Paragraph("Vérifiez les critères GuruFocus:", styles['Heading3']))
    elements.append(Paragraph(f"<link color='blue'>{analysis['gf_url']}</link>", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- Génération CSV ---
def generate_csv(analysis):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Critère", "Statut", "Seuil", "Valeur", "Explication"])
    for criterion, result in analysis['results'].items():
        writer.writerow([
            criterion,
            "Valide" if result["valid"] else "Invalide",
            result["threshold"],
            result["value"],
            result["description"]
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
        <div style="color:#4f81bd;font-size:25px;font-weight:600;">MLG Screener Pro</div>
        <div style="color:#9ca3af;font-size:15px;">Analyse fondamentale complète</div>
    </div>
</div>
""", unsafe_allow_html=True)

tab_analyse, tab_planification = st.tabs(["Analyser une entreprise", "Planifier une analyse complète"])

with tab_analyse:
    ticker = st.text_input("Entrez un ticker (ex: AAPL, MSFT, GMED)", "AAPL", key="ticker_input")

    if st.button("Analyser", key="analyze_button"):
        if ticker:
            with st.spinner("Analyse en cours..."):
                analysis = analyze_stock(ticker)

            if "error" in analysis:
                st.error(analysis["error"])
            else:
                st.markdown(f"""
                <div style="background:#334155;padding:20px;border-radius:8px;margin-bottom:20px;text-align:center;">
                    Score: <span style="font-size:33px;font-weight:700;color:#10b981;">{analysis['valid_count']}/{analysis['total']}</span>
                    <div style="font-size:15px;color:#9ca3af;">critères vérifiés</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"### {analysis['ticker']} - {analysis['name']}")
                st.markdown(f"**Prix actuel:** {analysis['current_price']} | **Capitalisation:** {analysis['market_cap']:,.0f} | **FCF Yield:** {analysis['fcf_yield']:.2f}% | **RSI (14j):** {analysis['rsi']:.1f}")

                for criterion, result in analysis['results'].items():
                    status = "✅ Valide" if result["valid"] else "❌ Invalide"
                    color = "#10b981" if result["valid"] else "#ef4444"
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:12px;background:#334155;border-radius:6px;border:1px solid #475569;margin-bottom:8px;border-left:4px solid {color};">
                        <span style="font-size:15px;">{criterion}</span>
                        <div style="display:flex;flex-direction:column;align-items:flex-end;">
                            <span style="font-weight:600;color:{color};font-size:15px;">{status}</span>
                            <span style="font-size:13px;color:#9ca3af;margin-top:2px;">{result["value"]} ({result["threshold"]})</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                if analysis['holders']:
                    st.markdown("<div style='background:#334155;padding:20px;border-radius:8px;margin-top:20px;'>", unsafe_allow_html=True)
                    st.markdown("<h3 style='color:#4f81bd;margin-top:0;font-size:17px;'>🏛️ Principaux actionnaires institutionnels</h3>", unsafe_allow_html=True)
                    for holder in analysis['holders']:
                        st.markdown(f"""
                        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #475569;">
                            <span style="font-size:15px;">{holder['name']}</span>
                            <span style="font-size:15px;">{holder['shares']:,.0f} actions ({holder['pctHeld']:.1f}%)</span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                # Section GuruFocus COMPLÈTE
                st.markdown("""
                <div style="background:#334155;padding:20px;border-radius:8px;margin-top:20px;">
                    <h3 style="color:#f59e0b;margin-top:0;font-size:17px;">⚠️ Critères GuruFocus à vérifier</h3>
                """, unsafe_allow_html=True)

                # GF Valuation
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #475569;">
                    <span style="font-size:15px;">GF Valuation (Significatively/Modestly undervalued)</span>
                    <a href="{analysis['gf_url']}" style="color:#4f81bd;text-decoration:none;font-size:15px;" target="_blank">Vérifier →</a>
                </div>
                """, unsafe_allow_html=True)

                # GF Score
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #475569;">
                    <span style="font-size:15px;">GF Score (≥ 70)</span>
                    <a href="{analysis['gf_url']}" style="color:#4f81bd;text-decoration:none;font-size:15px;" target="_blank">Vérifier →</a>
                </div>
                """, unsafe_allow_html=True)

                # Progression GF Value
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;">
                    <span style="font-size:15px;">Progression GF Value (FY1 < FY2 ≤ FY3)</span>
                    <a href="{analysis['gf_url']}" style="color:#4f81bd;text-decoration:none;font-size:15px;" target="_blank">Vérifier →</a>
                </div>
                """, unsafe_allow_html=True)

                # Bouton EXPORT sous les critères GuruFocus comme demandé
                st.markdown('<div class="export-buttons">', unsafe_allow_html=True)

                # Bouton CSV
                csv = generate_csv(analysis)
                st.download_button(
                    label="Exporter en CSV",
                    data=csv,
                    file_name=f"analyse_{analysis['ticker']}.csv",
                    mime="text/csv",
                    key="export_csv"
                )

                # Bouton PDF
                pdf = generate_pdf(analysis)
                st.download_button(
                    label="Exporter en PDF",
                    data=pdf,
                    file_name=f"analyse_{analysis['ticker']}.pdf",
                    mime="application/pdf",
                    key="export_pdf"
                )
                st.markdown('</div>', unsafe_allow_html=True)

with tab_planification:
    st.markdown("<div style='background:#334155;padding:20px;border-radius:8px;margin-top:30px;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#4f81bd;font-size:17px;'>Planification complète</h2>", unsafe_allow_html=True)

    frequency = st.selectbox(
        "Fréquence d'analyse",
        ["Toutes les 4 semaines", "Toutes les 6 semaines", "Toutes les 8 semaines", "Toutes les 12 semaines"],
        key="frequency_select"
    )

    start_date = st.date_input("Date de la première analyse", datetime.now(), key="start_date")
    st.info(f"Analyse programmée pour {start_date.strftime('%d/%m/%Y')} à 22h00")

    if st.button("Lancer l'analyse complète", key="launch_button"):
        st.success(f"✅ Analyse complète programmée pour {start_date.strftime('%d/%m/%Y')} à 22h00")

# --- Pied de page exactement comme demandé ---
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
