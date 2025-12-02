import streamlit as st
import base64

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

    .content-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: url('https://i.imgur.com/V0002.jpg') no-repeat center center;
        background-size: cover;
        opacity: 0.1;
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

# --- Logo en base64 ---
logo_base64 = """
iVBORw0KGgoAAAANSUhEUgAAASwAAACoCAMAAABt9SM9AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyhpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTExIDc5LjE2Njc5NywgMjAxNi8wOC8yMC0xMDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTcgKE1hY2ludG9zaCkiIHhtcDpDcmVhdG9yRGF0ZT0iMjAxNy0wMy0yMVAxMDoyMTo1MloiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6QjVEMkM5Qjg1M0UxMTFFMTk3RTk1M0IyMzQyMzZBQTAiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6QjVEMkM5Qjk1M0UxMTFFMTk3RTk1M0IyMzZBQTAiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDpCNUQyQzlCOUQzRTExMUUxOTdFOUUzQjIzRDIzNkFBQyIvPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDpCNUQyQzlCOTUzRTExMUUxOTdFOUUzQjIzRDIzNkFBQyIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/Pv/oZ1JAAAAYdEVYdENvdW50AAAAAQAAE0ZJTgAORklNA+0AAABUSURBVHja7d1NSsNAFIah93sDYWGYmW2QdqK0U7VopdBKFoqEoqFQq9VqKRdN0jZqo9FoNKirKysrKytrq9Vq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9Xq9
