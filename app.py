```python
import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import numpy as np
from datetime import datetime

# --- Configuration de la page ---
st.set_page_config(
    page_title="MLG Screener - EURL MLG Courtage",
    page_icon="\:shield:",
    layout="wide"
)

# --- CSS personnalisé pour le branding MLG Courtage ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat\:wght@400;600;700&display=swap');

    \:root {
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

    a\:hover {
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
    tab1, tab2, tab3 = st.tabs(["🔍 <followup encodedFollowup="%7B%22snippet%22%3A%22Analyse%20Manuelle%22%2C%22question%22%3A%22Quels%20types%20d'analyses%20peuvent%20%C3%AAtre%20effectu%C3%A9es%20dans%20l'onglet%20Analyse%20Manuelle%3F%22%2C%22id%22%3A%220cd1d287-c0e6-487b-a1f5-c92c0176abe6%22%7D" />", "⏰ Planification", "🏢 À Propos"])

    with tab1:
        st.header("Analyse Manuelle")
        ticker = st.text_input("Entrez un ticker (ex: AAPL)", "AAPL").upper()
        if st.button("Analyser"):
            st.info(f"Analyse en cours pour {ticker}...")
            # Ajoute ici la logique d'analyse

    with tab2:
        st.header("<followup encodedFollowup="%7B%22snippet%22%3A%22Planification%20Automatis%C3%A9e%22%2C%22question%22%3A%22Comment%20fonctionne%20exactement%20la%20planification%20automatis%C3%A9e%20des%20analyses%3F%22%2C%22id%22%3A%22966e05ff-237c-40c5-801f-8e7ab8d9b250%22%7D" />")
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
            - Une <followup encodedFollowup="%7B%22snippet%22%3A%22analyse%20technique%20rigoureuse%22%2C%22question%22%3A%22Quels%20indicateurs%20ou%20m%C3%A9thodes%20sont%20utilis%C3%A9s%20pour%20l'analyse%20technique%20dans%20MLG%20Screener%3F%22%2C%22id%22%3A%2208115ab4-478c-480d-97dd-1b43e39460a2%22%7D" />
            - Des <followup encodedFollowup="%7B%22snippet%22%3A%22crit%C3%A8res%20fondamentaux%20stricts%22%2C%22question%22%3A%22Quels%20sont%20les%20principaux%20crit%C3%A8res%20fondamentaux%20pris%20en%20compte%20par%20l'outil%3F%22%2C%22id%22%3A%22760ba7ba-5998-4707-b1f6-ff69d0b6283f%22%7D" />
            - Une <followup encodedFollowup="%7B%22snippet%22%3A%22veille%20informationnelle%20en%20temps%20r%C3%A9el%22%2C%22question%22%3A%22Quelles%20sources%20ou%20outils%20sont%20utilis%C3%A9s%20pour%20assurer%20la%20veille%20informationnelle%3F%22%2C%22id%22%3A%225c76b3ea-3154-40d5-a0d6-ee7b5e06f1a2%22%7D" />

            Pour en savoir plus sur nos services, visitez notre site : [mlgcourtage.fr](https://mlgcourtage.fr)
            """
        )

    display_footer()

if __name__ == "__main__":
    main()
