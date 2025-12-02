import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import io
import csv
from datetime import datetime, time

# --- Configuration ---
st.set_page_config(
    page_title="MLG Screener Pro",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Constantes ---
NEWS_API_KEY = "51aa6af9-be5d-4f40-a853-bea7c8c6e5f0"

# --- CSS avec fond sombre ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
:root {
    --primary: #4f81bd;
    --secondary: #3b82f6;
    --valid: #10b981;
    --invalid: #ef4444;
    --warning: #f59e0b;
    --dark-bg: #1e293b;
    --dark-card: #334155;
    --text: #e2e8f0;
    --border: #475569;
}
body {font-family: 'Montserrat', sans-serif; background-color: var(--dark-bg) !important; color: var(--text) !important;}
[data-testid="stAppViewContainer"] {background-color: var(--dark-bg) !important;}
[data-testid="stHeader"] {background-color: rgba(0, 0, 0, 0) !important;}

.banner {display:flex;align-items:center;gap:20px;margin-bottom:30px;}
.banner img {width:180px;}
.title {color:var(--primary);font-size:24px;font-weight:600;}

.score-card {background:var(--dark-card);padding:20px;border-radius:8px;margin-bottom:20px;text-align:center;}
.score-number {font-size:32px;font-weight:700;color:var(--valid);}

.criteria-container {margin:20px 0;}
.criterion {
    display:flex;justify-content:space-between;align-items:center;
    padding:12px;background:var(--dark-card);border-radius:6px;
    border:1px solid var(--border);margin-bottom:8px;
}
.criterion.valid {border-left:4px solid var(--valid);}
.criterion.invalid {border-left:4px solid var(--invalid);}
.status-container {display:flex;flex-direction:column;align-items:flex-end;}
.status {font-weight:600;}
.status.valid {color:var(--valid);}
.status.invalid {color:var(--invalid);}
.value {font-size:12px;color:#9ca3af;margin-top:2px;}

.gf-section {background:var(--dark-card);padding:20px;border-radius:8px;margin-top:20px;}
.gf-item {display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);}
.gf-link {color:var(--primary);text-decoration:none;font-weight:600;}
.gf-link:hover {text-decoration:underline;}
.gf-button {background:var(--primary);color:white;padding:10px 20px;border:none;border-radius:5px;text-decoration:none;display:inline-block;margin-top:10px;}

.nav-buttons {display:flex;gap:20px;justify-content:center;margin:20px 0;}
.nav-button {background:var(--primary);color:white;padding:12px 24px;border:none;border-radius:6px;font-weight:600;text-decoration:none;}

.plan-section {background:var(--dark-card);padding:20px;border-radius:8px;margin-top:30px;}
.export-buttons {display:flex;gap:10px;justify-content:flex-end;margin-top:20px;}
.export-button {background:var(--primary);color:white;padding:8px 16px;border:none;border-radius:4px;text-decoration:none;}

.news-section {background:var(--dark-card);padding:20px;border-radius:8px;margin-top:30px;}
.news-item {border-bottom:1px solid var(--border);padding:15px 0;}
.news-title {color:var(--text);font-weight:600;margin-bottom:5px;}
.news-source {color:#9ca3af;font-size:12px;}

.institutional-holders {background:var(--dark-card);padding:20px;border-radius:8px;margin-top:20px;}
.holder-item {display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border);}

.footer {
    margin-top: 50px;
    padding: 20px;
    text-align: center;
    color: var(--text);
    font-size: 14px;
    border-top: 1px solid var(--border);
}
.footer-title {
    font-weight: 600;
    margin-bottom: 10px;
    color: var(--primary);
}
.company-info {
    margin: 15px 0;
    line-height: 1.5;
}
.company-info a {
    color: var(--primary);
    text-decoration: none;
}
.company-info a:hover {
    text-decoration: underline;
}
.disclaimer {
    font-size: 12px;
    color: #9ca3af;
    margin: 15px auto;
    line-height: 1.4;
    text-align: left;
    max-width: 800px;
}
.copyright {
    margin-top: 20px;
    font-size: 12px;
    color: #9ca3af;
}
</style>
""", unsafe_allow_html=True)

# [Toutes les fonctions restent identiques...]

# --- Pied de page professionnel et propre ---
st.markdown("""
<div class="footer">
    <div class="footer-title">MLG Screener - Outil d'analyse financière professionnel</div>

        Proposé gratuitement par <strong>EURL MLG Courtage
        Courtier en assurances agréé ORIAS n°24002055
        SIRET : 98324762800016
        www.mlgcourtage.fr
   

    
        MLG Screener est un outil d'analyse financière conçu pour aider les investisseurs à identifier des opportunités selon une méthodologie rigoureuse.
        Les informations présentées sont basées sur des données publiques et ne constituent en aucun cas un conseil en investissement.
        Tout investissement comporte des risques, y compris la perte en capital. Les performances passées ne préjugent pas des performances futures.
        Nous vous recommandons vivement de consulter un conseiller financier indépendant avant toute décision d'investissement.
    

    copyright
        © 2023 EURL MLG Courtage - Tous droits réservés
    
</div>
""", unsafe_allow_html=True)
