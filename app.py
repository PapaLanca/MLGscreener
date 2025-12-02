import streamlit as st
import yfinance as yf
# import requests  # À décommenter si tu utilises Alpha Vantage

# --- Configuration de la page ---
st.set_page_config(
    page_title="MLG Screener",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS complet ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
:root {--primary-color: #1e3a8a;--secondary-color: #3b82f6;--text-color: #1f2937;}
body,[data-testid="stAppViewContainer"] {background-color: white !important;color: var(--text-color) !important;font-family: 'Montserrat', sans-serif !important;}
.stTextInput>div, .stTextArea>div, .stSelectbox>div {background-color: white !important;}
.stTextInput>div>div>input, .stTextArea>div>textarea {background-color: white !important;color: var(--text-color) !important;border: 1px solid #e5e7eb !important;border-radius: 4px !important;}
.stButton>button {background-color: var(--primary-color) !important;color: white !important;border-radius: 4px !important;border: none !important;}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {color: var(--primary-color) !important;}
.banner {background-color: white;padding: 20px;display: flex;align-items: center;justify-content: space-between;border-bottom: 1px solid #e5e7eb;margin-bottom: 30px;}
.banner-text {flex: 1;text-align: center;color: var(--primary-color);font-size: 20px;font-weight: 600;}
.nav-buttons {display: flex;gap: 20px;justify-content: center;margin-bottom: 30px;}
.nav-button {background-color: var(--primary-color);color: white !important;padding: 12px 24px;border: none;border-radius: 6px;font-weight: 600;text-decoration: none;display: inline-block;}
.content-section {background-color: white;padding: 30px;border-radius: 8px;box-shadow: 0 2px 4px rgba(0,0,0,0.05);margin-bottom: 30px;}
.footer {background-color: white;padding: 20px;text-align: center;border-top: 1px solid #e5e7eb;color: var(--text-color);font-size: 14px;margin-top: 40px;}
.footer a {color: var(--primary-color);text-decoration: none;}
.section-title {color: var(--primary-color);border-bottom: 1px solid #e5e7eb;padding-bottom: 10px;margin-bottom: 20px;}
.metric-card {background-color: #f8fafc;padding: 15px;border-radius: 8px;margin-bottom: 15px;border-left: 4px solid var(--primary-color);}
</style>
""", unsafe_allow_html=True)

# --- Bandeau ---
def display_banner():
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            st.image("https://raw.githubusercontent.com/PapaLanca/MLGscreener/master/logo_mlg_courtage.webp", width=180)
        except:
            st.error("Logo introuvable")
    with col2:
        st.markdown("<div class='banner-text'>MLG Courtage - Outil d'analyse financière</div>", unsafe_allow_html=True)

# --- Analyse d'entreprise (version optimisée) ---
def display_analyse_section():
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Analyse fondamentale</h2>', unsafe_allow_html=True)

    ticker = st.text_input("Entrez le ticker (ex: AAPL, GMED, MSFT)", "GMED").upper()

    if st.button("Analyser"):
        if ticker:
            with st.spinner(f"Analyse de {ticker}..."):
                try:
                    # --- Données YFinance ---
                    stock = yf.Ticker(ticker)
                    info = stock.info

                    # --- Affichage des données clés ---
                    st.subheader(f"📊 {ticker} - {info.get('longName', 'N/A')}")
                    st.write(f"**Secteur:** {info.get('sector', 'N/A')} | **Industrie:** {info.get('industry', 'N/A')}")

                    # Métriques financières
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <strong>Prix actuel:</strong> {info.get('currentPrice', 'N/A')} {info.get('currency', 'USD')}
                            <br><strong>Capitalisation:</strong> {info.get('marketCap', 'N/A'):,}
                            <br><strong>Volume moyen:</strong> {info.get('averageVolume', 'N/A'):,}
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <strong>P/E Ratio:</strong> {info.get('trailingPE', 'N/A')}
                            <br><strong>Bénéfice/Action:</strong> {info.get('trailingEps', 'N/A')}
                            <br><strong>Dividende:</strong> {info.get('dividendYield', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)

                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <strong>Beta (volatilité):</strong> {info.get('beta', 'N/A')}
                            <br><strong>Marges:</strong> {info.get('profitMargins', 'N/A')}
                            <br><strong>ROE:</strong> {info.get('returnOnEquity', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)

                    # --- Analyse technique basique ---
                    st.markdown("<h3 class='section-title'>Indicateurs techniques</h3>", unsafe_allow_html=True)
                    hist = stock.history(period="1d")
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        st.write(f"**Dernier cours:** {current_price:.2f}")

                    # --- Alpha Vantage (optionnel) ---
                    # alpha_vantage_data = get_alpha_vantage_data(ticker)  # Fonction à implémenter
                    # if alpha_vantage_data:
                    #     st.json(alpha_vantage_data)  # Ou affichage personnalisé

                except Exception as e:
                    st.error(f"Erreur: {str(e)}")
        else:
            st.warning("Veuillez entrer un ticker")

    st.markdown('</div>', unsafe_allow_html=True)

# --- Pied de page ---
def display_footer():
    st.markdown("""
    <div class="footer">
        <p><strong>EURL MLG Courtage</strong> - Courtier en assurances</p>
        <p>SIRET: 98324762800016 | ORIAS: 24002055</p>
        <p>12 La Garnaudière, 44310 La Limouzinière</p>
    </div>
    """, unsafe_allow_html=True)

# --- Application principale ---
def main():
    display_banner()
    display_analyse_section()
    display_footer()

if __name__ == "__main__":
    main()
