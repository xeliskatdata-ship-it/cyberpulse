# _sidebar_css.py -- CSS sidebar Option B partage entre toutes les pages
# Usage dans chaque page : from _sidebar_css import inject_sidebar_css; inject_sidebar_css()

import streamlit as st

def inject_sidebar_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&display=swap');

    /* Sidebar background + gradient bar animee */
    [data-testid="stSidebar"] {
        background: #050a14 !important;
        border-right: 1px solid rgba(30,111,255,0.15) !important;
    }
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #3b82f6, #a855f7, #3b82f6);
        background-size: 200% 100%;
        animation: sidebar-gradient 4s linear infinite;
        z-index: 10;
    }
    @keyframes sidebar-gradient {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    [data-testid="stSidebar"] * { color: #7a9cc8 !important; }

    /* Nav links */
    a[data-testid="stSidebarNavLink"] {
        font-family: 'JetBrains Mono', 'Roboto Mono', monospace !important;
        font-size: 0.82rem !important;
        color: #7a9cc8 !important;
        padding: 10px 18px !important;
        margin: 1px 8px !important;
        border-radius: 0 !important;
        border-left: 3px solid transparent !important;
        position: relative !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
        display: block !important;
        background: transparent !important;
    }
    a[data-testid="stSidebarNavLink"]:hover {
        color: #e8f0fe !important;
        background: rgba(30,111,255,0.06) !important;
    }
    a[data-testid="stSidebarNavLink"][aria-current="page"] {
        color: #e8f0fe !important;
        background: linear-gradient(90deg, rgba(30,111,255,0.15), transparent) !important;
        border-left: 3px solid #a855f7 !important;
    }

    /* Masquer les icones svg */
    a[data-testid="stSidebarNavLink"] svg { display: none !important; }

    /* Separateurs */
    li:has(a[href*="Accueil"]) { border-bottom: 1px solid rgba(30,111,255,0.1) !important; padding-bottom: 8px !important; margin-bottom: 8px !important; }
    li:has(a[href*="Carte"]) { border-top: 1px solid rgba(30,111,255,0.1) !important; padding-top: 8px !important; margin-top: 8px !important; }
    </style>
    """, unsafe_allow_html=True)
