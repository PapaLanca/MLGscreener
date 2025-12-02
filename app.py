import streamlit as st
import base64
from io import BytesIO
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
        --primary-color: #1a365d;   /* Bleu foncé du logo MLG */
        --secondary-color: #8bb8e8; /* Bleu clair */
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

    .logo {
        width: 80px;
        height: auto;
        margin-right: 15px;
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

# --- Logo MLG Courtage encodé en base64 (intégré directement) ---
LOGO_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAAJAAAACQCAYAAADJy6v/AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4QkUEQwXzq5q0gAAABl0RVh0Q29tbWVudABDcmVhdG9yZSBJbWFnZUxpbmUgcHJvZmlsZSBzY3JlZW4gU2FsdGVkIFJlZ2lvdXMgU2FsdGVkIElERU05ODMzNTU0NzUAAABiSURBVHja7dXBSsIwEIXhq7sDYWGYmW2QdqK0U7VopdBKFoqEoqFQq9VqKRdN0jZqo9FoNKirKysrKytrq9Vq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9
