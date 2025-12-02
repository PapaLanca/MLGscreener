import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import numpy as np
from datetime import datetime

# --- Configuration de la page ---
st.set_page_config(
    page_title="MLG Courtage - Solutions d'Investissement",
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)

# --- CSS personnalisé pour un style professionnel avec images ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

    :root {
        --primary-color: #1e3a8a;
        --secondary-color: #3b82f6;
        --text-color: #1e3a8a;
        --light-color: #f8fafc;
        --border-color: #e2e8f0;
    }

    body {
        font-family: 'Montserrat', sans-serif;
        background-color: var(--light-color);
    }

    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        background-color: white;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }

    .logo {
        font-size: 24px;
        font-weight: 700;
        color: var(--primary-color);
    }

    .tagline {
        font-size: 14px;
        color: var(--text-color);
        font-style: italic;
    }

    .nav {
        display: flex;
        gap: 20px;
    }

    .nav a {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 500;
    }

    .nav a:hover {
        color: var(--secondary-color);
    }

    .main-content {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    .hero-section {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 40px;
        border-radius: 8px;
        margin-bottom: 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: url('https://images.unsplash.com/photo-1630108607727-999ca9b752c8?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80') no-repeat center center;
        background-size: cover;
        opacity: 0.3;
    }

    .hero-content {
        position: relative;
        z-index: 1;
    }

    .section-title {
        color: var(--primary-color);
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }

    .section-icon {
        margin-right: 10px;
    }

    .feature-card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid var(--secondary-color);
    }

    .feature-card h3 {
        color: var(--primary-color);
        margin-top: 0;
    }

    .feature-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 4px;
        margin-bottom: 15px;
    }

    .footer {
        background-color: var(--primary-color);
        color: white;
        padding: 30px 20px 20px;
        margin-top: 40px;
    }

    .footer-content {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }

    .footer-section h3 {
        color: white;
        font-size: 18px;
        margin-bottom: 10px;
    }

    .footer-section p, .footer-section a {
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 5px;
        text-decoration: none;
    }

    .footer-section a:hover {
        color: white;
    }

    .disclaimer {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.7);
        margin-top: 20px;
        line-height: 1.4;
    }

    .legal-box {
        background-color: rgba(30, 58, 138, 0.1);
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

    .stTextInput>div>div>input {
        border: 1px solid var(--border-color);
    }

    .stSelectbox>div>div>select {
        border: 1px solid var(--border-color);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- En-tête professionnel ---
def display_header():
    st.markdown(
        f"""
        <div class="header">
            <div>
                <div class="logo">MLG COURTAGE</div>
                <div class="tagline">Solutions d'investissement sur mesure</div>
            </div>
            <div class="nav">
                <a href="#analyse">Analyse</a>
                <a href="#planification">Planification</a>
                <a href="#apropos">À Propos</a>
                <a href="https://mlgcourtage.fr" target="_blank">Site Web</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Section héroïque avec image ---
def display_hero_section():
    st.markdown(
        """
        <div class="hero-section">
            <div class="hero-content">
                <h1>Découvrez les opportunités d'investissement</h1>
                <p>Identifiez les pépites et licornes du marché avec nos outils d'analyse avancés.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Pied de page professionnel ---
def display_footer():
    st.markdown(
        f"""
        <div class="footer">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>MLG Courtage</h3>
                    <p>EURL MLG Courtage</p>
                    <p>SIRET : 98324762800016</p>
                    <p>ORIAS : 24002055</p>
                    <p>📍 Adresse : 12 La Garnaudière, 44310 La Limouzinière</p>
                </div>
                <div class="footer-section">
                    <h3>Liens</h3>
                    <p><a href="https://mlgcourtage.fr" target="_blank">Site Web</a></p>
                </div>
            </div>
            <div class="disclaimer">
                <p><strong>Disclaimer :</strong></p>
                <p>MLG Courtage est un outil d'aide à la décision d'investissement. Les informations fournies ne constituent pas un conseil en investissement, une recommandation d'achat ou de vente, ni une incitation à investir. Tout investissement comporte des risques, y compris la perte en capital. Il est fortement recommandé d'effectuer vos propres recherches et de consulter un conseiller financier indépendant avant de prendre toute décision d'investissement. EURL MLG Courtage ne saurait être tenue responsable des décisions prises sur la base des informations fournies par cet outil.</p>
                <p>© 2025 EURL MLG Courtage. Tous droits réservés.</p>
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
    display_hero_section()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    display_legal_preamble()

    # --- Section Opportunités ---
    st.markdown('<div id="analyse"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title"><span class="section-icon">🔍</span> Opportunités d\'Investissement</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="feature-card">
                <img class="feature-image" src="https://images.unsplash.com/photo-1630108607727-999ca9b752c8?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80" alt="Trading Opportunities">
                <h3>Trading & Opportunités</h3>
                <p>Identifiez les meilleures opportunités de trading avec nos outils d'analyse technique et fondamentale.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="feature-card">
                <img class="feature-image" src="https://images.unsplash.com/photo-1611974928042caf4008a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80" alt="High Yield Investments">
                <h3>Rendements Élevés</h3>
                <p>Découvrez les actifs avec les meilleurs rendements et optimisez votre portefeuille.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- Onglets ---
    tab1, tab2, tab3 = st.tabs(["📊 Analyse Manuelle", "⏰ Planification", "🏢 À Propos"])

    with tab1:
        st.markdown('<div id="analyse"></div>', unsafe_allow_html=True)
        st.header("Analyse Manuelle")
        ticker = st.text_input("Entrez un ticker (ex: AAPL)", "AAPL").upper()
        if st.button("Analyser"):
            st.info(f"Analyse en cours pour {ticker}...")
            # Ajoute ici la logique d'analyse

    with tab2:
        st.markdown('<div id="planification"></div>', unsafe_allow_html=True)
        st.header("Planification Automatisée")
        frequency = st.selectbox(
            "Fréquence d'analyse",
            ["Toutes les 4 semaines", "Toutes les 6 semaines", "Toutes les 8 semaines", "Toutes les 12 semaines"]
        )
        if st.button("Lancer la planification"):
            st.success(f"Planification activée pour une analyse {frequency} à minuit.")

    with tab3:
        st.markdown('<div id="apropos"></div>', unsafe_allow_html=True)
        st.header("À Propos de MLG Courtage")
        st.markdown(
            """
            <div class="feature-card">
                <img class="feature-image" src="https://images.unsplash.com/photo-1579389083078-7e055ed9f87d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80" alt="About MLG Courtage">
                <h3>Notre Mission</h3>
                <p>MLG Courtage est une entreprise spécialisée dans les solutions d'investissement sur mesure. Nous proposons des outils d'analyse financière pour aider nos clients à prendre des décisions éclairées.</p>
                <p>Notre approche combine :</p>
                <ul>
                    <li>Une analyse technique rigoureuse</li>
                    <li>Des critères fondamentaux stricts</li>
                    <li>Une veille informationnelle en temps réel</li>
                </ul>
                <p>Pour en savoir plus, visitez notre site : <a href="https://mlgcourtage.fr" target="_blank">mlgcourtage.fr</a></p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

    display_footer()

if __name__ == "__main__":
    main()
