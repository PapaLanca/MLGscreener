import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# --- Configuration de la page ---
st.set_page_config(
    page_title="MLG Screener",
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)

# --- CSS personnalisé ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

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

    .banner {
        background-color: white;
        padding: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid var(--border-color);
    }

    .logo {
        height: 80px;
    }

    .banner-text {
        flex: 1;
        text-align: center;
        color: var(--primary-color);
        font-size: 20px;
        font-weight: 600;
    }

    .nav-buttons {
        display: flex;
        gap: 20px;
        margin: 20px auto;
        justify-content: center;
    }

    .nav-button {
        background-color: var(--primary-color);
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
    }

    .nav-button:hover {
        background-color: var(--secondary-color);
    }

    .content-section {
        background-color: white;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 20px;
        position: relative;
        overflow: hidden;
    }

    .content-text {
        position: relative;
        z-index: 1;
    }

    .footer {
        background-color: white;
        padding: 20px;
        text-align: center;
        border-top: 1px solid var(--border-color);
        color: var(--primary-color);
        font-size: 14px;
    }

    .footer a {
        color: var(--primary-color);
        text-decoration: none;
    }

    .footer a:hover {
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Fonction pour afficher le logo ---
def display_logo():
    logo_url = "https://raw.githubusercontent.com/PapaLanca/MLGscreener/main/logo_mlg_courtage.webp"
    st.markdown(
        f"""
        <div class="banner">
            <img class="logo" src="{logo_url}">
            <div class="banner-text">MLG Courtage vous propose MLG Screener pour vous aider à trouver des opportunités et générer un revenu complémentaire</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Fonction principale ---
def main():
    display_logo()

    st.markdown(
        """
        <div class="nav-buttons">
            <a class="nav-button" href="#analyse">Analyser une entreprise</a>
            <a class="nav-button" href="#planification">Planifier une analyse</a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="content-section" id="analyse">', unsafe_allow_html=True)
    st.markdown('<div class="content-text">', unsafe_allow_html=True)
    st.header("À propos de MLG Screener")
    st.write("""
    MLG Screener est un outil conçu pour vous aider à identifier des opportunités d'investissement.
    Notre objectif est de vous fournir des analyses techniques et fondamentales pour vous aider à prendre des décisions éclairées.
    """)
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="footer">
            <p>EURL MLG Courtage - votre courtier en assurances</p>
            <p>SIRET : 98324762800016 | ORIAS : 24002055</p>
            <p>12 La Garnaudière, 44310 La Limouzinière</p>
            <p><a href="https://mlgcourtage.fr" target="_blank">mlgcourtage.fr</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
