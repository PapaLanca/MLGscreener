import streamlit as st

# --- Configuration de la page ---
st.set_page_config(
    page_title="MLG Screener",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS pour un design clair et professionnel ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

    :root {
        --primary-color: #1e3a8a;
        --secondary-color: #3b82f6;
        --text-color: #1f2937;
        --light-color: #ffffff;
        --border-color: #e5e7eb;
    }

    body, [data-testid="stAppViewContainer"] {
        background-color: var(--light-color) !important;
        color: var(--text-color) !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0) !important;
    }

    .banner {
        background-color: var(--light-color);
        padding: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 30px;
    }

    .logo-container {
        display: flex;
        align-items: center;
        width: 200px;
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
        justify-content: center;
        margin-bottom: 30px;
    }

    .nav-button {
        background-color: var(--primary-color);
        color: white !important;
        padding: 12px 24px;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        text-decoration: none;
        display: inline-block;
        transition: background-color 0.2s;
    }

    .nav-button:hover {
        background-color: var(--secondary-color);
    }

    .content-section {
        background-color: var(--light-color);
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 30px;
    }

    .footer {
        background-color: var(--light-color);
        padding: 20px;
        text-align: center;
        border-top: 1px solid var(--border-color);
        color: var(--text-color);
        font-size: 14px;
        margin-top: 40px;
    }

    .footer a {
        color: var(--primary-color);
        text-decoration: none;
    }

    .footer a:hover {
        text-decoration: underline;
    }

    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--primary-color) !important;
    }

    .stMarkdown, .stMarkdown p, .stMarkdown li {
        color: var(--text-color) !important;
    }

    .stButton>button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
    }

    a:not(.nav-button) {
        color: var(--primary-color) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Bandeau avec logo ---
def display_banner():
    logo_url = "https://raw.githubusercontent.com/PapaLanca/MLGscreener/master/logo_mlg_courtage.webp"

    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            st.image(logo_url, width=180)
        except:
            st.error("Logo introuvable. Vérifiez le nom du fichier et la branche.")
    with col2:
        st.markdown(
            """
            <div class="banner-text">
                MLG Courtage vous propose MLG Screener pour vous aider à trouver des opportunités et générer un revenu complémentaire
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Boutons de navigation ---
def display_nav_buttons():
    st.markdown(
        """
        <div class="nav-buttons">
            <a class="nav-button" href="#analyse">Analyser une entreprise</a>
            <a class="nav-button" href="#planification">Planifier une analyse</a>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Contenu principal ---
def display_main_content():
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.header("À propos de MLG Screener")
    st.write("""
    MLG Screener est un outil conçu pour vous aider à identifier des opportunités d'investissement.
    Notre objectif est de vous fournir des analyses techniques et fondamentales pour vous aider à prendre des décisions éclairées.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Pied de page ---
def display_footer():
    st.markdown(
        """
        <div class="footer">
            <p><strong>EURL MLG Courtage</strong> - votre courtier en assurances</p>
            <p>SIRET : 98324762800016 | ORIAS : 24002055</p>
            <p>12 La Garnaudière, 44310 La Limouzinière</p>
            <p><a href="https://mlgcourtage.fr" target="_blank">mlgcourtage.fr</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Application principale ---
def main():
    display_banner()
    display_nav_buttons()
    display_main_content()
    display_footer()

if __name__ == "__main__":
    main()
