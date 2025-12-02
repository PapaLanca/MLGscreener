import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import numpy as np
from datetime import datetime

# --- Configuration de la page ---
st.set_page_config(
    page_title="MLG Screener - EURL MLG Courtage",
    page_icon=":shield:",
    layout="wide"
)

# --- CSS personnalisé pour le branding MLG Courtage ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

    :root {
        --primary-color: #1a365d;
        --secondary-color: #8bb8e8;
        --text-color: #1a365d;
        --light-color: #f8f9fa;
        --border-color: #dee2e6;
    }

    body {
        font-family: 'Montserrat', sans-serif;
    }

    .header {
        display: flex;
        align-items: center;
        padding: 15px 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
        background-color: white;
    }

    .company-name {
        font-size: 24px;
        font-weight: 700;
        color: var(--primary-color);
    }

    .tagline {
        font-size: 14px;
        color: var(--text-color);
        font-style: italic;
        margin-left: 10px;
    }

    .footer {
        margin-top: 40px;
        padding: 20px;
        text-align: center;
        color: var(--text-color);
        font-size: 12px;
        background-color: var(--light-color);
        border-top: 1px solid var(--border-color);
    }

    .disclaimer {
        font-size: 12px;
        color: #6c757d;
        margin-top: 10px;
        font-style: italic;
        text-align: left;
    }

    .legal-box {
        background-color: var(--light-color);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border-left: 4px solid var(--primary-color);
    }

    .stButton>button {
        background-color: var(--secondary-color);
        color: white;
        border-radius: 6px;
        border: none;
    }

    a {
        color: var(--primary-color);
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    .criteria-box {
        border-left: 4px solid;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }

    .valid {
        border-left-color: #28a745;
        background-color: rgba(40, 167, 69, 0.1);
    }

    .invalid {
        border-left-color: #dc3545;
        background-color: rgba(220, 53, 69, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- En-tête avec nom de l'application ---
def display_header():
    st.markdown(f"""
    <div class="header">
        <div class="company-name">MLG SCREENER
            <span class="tagline">- votre courtier en assurances -</span>
        </div>
        <div style="font-size: 14px; color: var(--text-color);">par <a href="https://mlgcourtage.fr" target="_blank">EURL MLG Courtage</a></div>
    </div>
    """, unsafe_allow_html=True)

# --- Pied de page avec mentions légales ---
def display_footer():
    st.markdown(
        """
        <div class="footer">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p><strong>EURL MLG Courtage</strong></p>
                    <p>983 247 628 R.C.S. Paris</p>
                    <p>Courtier en assurances</p>
                </div>
                <div style="text-align: right;">
                    <p>🌐 <a href="https://mlgcourtage.fr" target="_blank">mlgcourtage.fr</a></p>
                </div>
            </div>
            <div class="disclaimer">
                <p><strong>Disclaimer :</strong></p>
                <p>MLG Screener est un outil d'aide à la décision d'investissement. Les informations fournies ne constituent pas un conseil en investissement, une recommandation d'achat ou de vente, ni une incitation à investir. Tout investissement comporte des risques, y compris la perte en capital. Il est fortement recommandé d'effectuer vos propres recherches et de consulter un conseiller financier indépendant avant de prendre toute décision d'investissement. EURL MLG Courtage ne saurait être tenue responsable des décisions prises sur la base des informations fournies par cet outil.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Préambule légal ---
def display_legal_preamble():
    st.markdown(
        """
        <div class="legal-box">
            <p style="font-size: 14px; color: var(--text-color); margin: 0;">
                <strong>⚠️ Important :</strong> MLG Screener est un outil d'<strong>aide à la décision d'investissement</strong> et ne constitue pas un conseil en investissement.
                Les informations fournies ne garantissent pas la performance future des actifs analysés.
                <strong>Effectuez toujours vos propres recherches</strong> et consultez un professionnel avant d'investir.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Fonction principale ---
def main():
    display_header()
    display_legal_preamble()

    # --- Onglets ---
    tab1, tab2, tab3 = st.tabs(["🔍 Analyse Manuelle", "⏰ Planification", "🏢 À Propos"])

    with tab1:
        st.header("Analyse Manuelle")
        ticker = st.text_input("Entrez un ticker (ex: AAPL)", "AAPL").upper()
        if st.button("Analyser"):
            st.info(f"Analyse en cours pour {ticker}...")
            # Ajoute ici la logique d'analyse

    with tab2:
        st.header("Planification Automatisée")
        frequency = st.selectbox(
            "Fréquence d'analyse",
            ["Toutes les 4 semaines", "Toutes les 6 semaines", "Toutes les 8 semaines", "Toutes les 12 semaines"]
        )
        if st.button("Lancer la planification"):
            st.success(f"Planification activée pour une analyse {frequency} à minuit.")

    with tab3:
        st.header("À Propos de MLG Screener")
        st.markdown(
            """
            **MLG Screener** est un outil développé par [EURL MLG Courtage](https://mlgcourtage.fr) pour aider les investisseurs à identifier des opportunités sur les marchés financiers.

            Notre approche combine :
            - Une analyse technique rigoureuse
            - Des critères fondamentaux stricts
            - Une veille informationnelle en temps réel

            Pour en savoir plus sur nos services, visitez notre site : [mlgcourtage.fr](https://mlgcourtage.fr)
            """
        )

    display_footer()

if __name__ == "__main__":
    main()
