import streamlit as st
import yfinance as yf
from datetime import datetime

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

    .stTextInput>div>div>input {
        border: 1px solid var(--border-color) !important;
        color: var(--text-color) !important;
    }

    a:not(.nav-button) {
        color: var(--primary-color) !important;
    }

    .section-title {
        color: var(--primary-color);
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 10px;
        margin-bottom: 20px;
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
            st.error("Logo introuvable")
    with col2:
        st.markdown(
            """
            <div class="banner-text">
                MLG Courtage vous propose MLG Screener pour vous aider à trouver des opportunités et générer un revenu complémentaire
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Section Analyse d'entreprise ---
def display_analyse_section():
    st.markdown('<div class="content-section" id="analyse">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Analyser une entreprise</h2>', unsafe_allow_html=True)

    ticker = st.text_input("Entrez le ticker de l'entreprise (ex: AAPL, MSFT, TSLA)", "AAPL")
    if st.button("Analyser"):
        if ticker:
            with st.spinner(f"Analyse de {ticker} en cours..."):
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    hist = stock.history(period="1y")

                    st.subheader(f"Informations sur {ticker} - {info.get('longName', ticker)}")
                    st.write(f"**Secteur:** {info.get('sector', 'N/A')} | **Industrie:** {info.get('industry', 'N/A')}")
                    st.write(f"**Prix actuel:** {info.get('currentPrice', 'N/A')} {info.get('currency', '')}")
                    st.write(f"**Capitalisation boursière:** {info.get('marketCap', 'N/A'):,}")

                    st.markdown("---")
                    st.subheader("Performance (1 an)")
                    st.line_chart(hist['Close'])

                    st.markdown("---")
                    st.subheader("Indicateurs clés")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("P/E Ratio", info.get('trailingPE', 'N/A'))
                        st.metric("Bénéfice par action", info.get('trailingEps', 'N/A'))
                    with col2:
                        st.metric("Dividende", info.get('dividendYield', 'N/A'))
                        st.metric("Volume moyen", f"{info.get('averageVolume', 'N/A'):,}")

                except Exception as e:
                    st.error(f"Erreur lors de l'analyse: {e}")
        else:
            st.warning("Veuillez entrer un ticker valide")

    st.markdown('</div>', unsafe_allow_html=True)

# --- Section Planification ---
def display_planification_section():
    st.markdown('<div class="content-section" id="planification">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Planifier une analyse</h2>', unsafe_allow_html=True)

    frequency = st.selectbox(
        "Fréquence d'analyse",
        ["Toutes les semaines", "Toutes les 2 semaines", "Toutes les 4 semaines", "Tous les mois"]
    )

    tickers = st.text_area("Liste des tickers à analyser (un par ligne)", "AAPL\nMSFT\nTSLA")

    if st.button("Programmer l'analyse"):
        st.success(f"Analyse programmée pour: {frequency}. Tickers: {tickers.replace('\n', ', ')}")
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

# --- Navigation ---
def display_navigation():
    st.markdown(
        """
        <div class="nav-buttons">
            <a class="nav-button" href="#analyse">Analyser une entreprise</a>
            <a class="nav-button" href="#planification">Planifier une analyse</a>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Application principale ---
def main():
    display_banner()
    display_navigation()
    display_analyse_section()
    display_planification_section()
    display_footer()

if __name__ == "__main__":
    main()
