import streamlit as st
from datetime import datetime
import io
import csv
import textwrap
import pandas as pd
import plotly.graph_objects as go

from dados import carregar_dados
from maquinas import (
    criar_maquina,
    remover_maquina,
    simular_leitura,
    registrar_leitura,
    analisar_maquina,
)
from analytics import calcular_indice_saude, calcular_tendencia, calcular_estatisticas
from relatorios import gerar_relatorio_html, gerar_ordem_servico_texto
from simulador_iot import gerar_leitura_cenario, CENARIOS

# -----------------------------------------------------------------------------
# Configuração de Página & Identidade Visual
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MetalSense | Monitoramento Inteligente",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Gerenciador de Estado de Navegação
# -----------------------------------------------------------------------------
if "maquina_ativa_id" not in st.session_state:
    st.session_state["maquina_ativa_id"] = None

# ---------------------------------------------------------------------------
# Paleta de Cores — Dribbble Aesthetic (Glassmorphism + Neon Glow), apenas modo escuro
# ---------------------------------------------------------------------------
T = {
    # Backgrounds
    "app_bg":          "radial-gradient(ellipse at 10% 20%, #0d1527 0%, #060911 70%)",
    "surface":         "rgba(15, 23, 42, 0.72)",
    "surface_card":    "rgba(15, 23, 42, 0.65)",
    "surface_metric":  "rgba(30, 41, 59, 0.55)",
    "sidebar_bg":      "rgba(8, 12, 20, 0.95)",
    # Borders
    "border":          "rgba(255, 255, 255, 0.07)",
    "border_hover":    "rgba(56, 189, 248, 0.45)",
    # Inputs
    "input_bg":        "rgba(15, 23, 42, 0.85)",
    "input_border":    "rgba(255, 255, 255, 0.12)",
    # Text
    "text_main":       "#f1f5f9",
    "text_sub":        "#94a3b8",
    "text_muted":      "#64748b",
    # Buttons
    "btn_bg":          "rgba(15, 23, 42, 0.8)",
    "btn_border":      "rgba(255, 255, 255, 0.10)",
    "btn_hover_bg":    "rgba(56, 189, 248, 0.12)",
    # Accent palette (neon)
    "accent_cyan":     "#00e5ff",
    "accent_blue":     "#38bdf8",
    "accent_emerald":  "#34d399",
    "accent_amber":    "#fbbf24",
    "accent_rose":     "#fb7185",
    "accent_violet":   "#c084fc",
    # Plotly
    "plot_paper":      "rgba(0,0,0,0)",
    "plot_bg":         "rgba(15, 23, 42, 0.45)",
    "plot_grid":       "rgba(255, 255, 255, 0.04)",
    "plot_text":       "#94a3b8",
    "gauge_bg":        "rgba(30, 41, 59, 0.55)",
    # Glow helpers
    "card_shadow":     "0 8px 32px -8px rgba(0, 229, 255, 0.08)",
    "card_hover_shadow": "0 12px 40px -8px rgba(0, 229, 255, 0.18)",
}


# ---------------------------------------------------------------------------
# Biblioteca de Ícones SVG (Feather Icons — vetorizados, profissionais)
# ---------------------------------------------------------------------------
ICONS = {
    "cpu": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>',
    "activity": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
    "alert": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    "thermometer": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"></path></svg>',
    "zap": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>',
    "waves": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path></svg>',
    "server": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>',
    "arrow-right": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>',
}


def get_icon(name: str, color: str = "currentColor", size: int = 18) -> str:
    """Retorna o código SVG do ícone renderizado inline."""
    template = ICONS.get(name, "")
    return template.format(s=size, c=color)


# ---------------------------------------------------------------------------
# CSS Global — Cobertura TOTAL de Todos os Widgets Streamlit
# ---------------------------------------------------------------------------
CSS_GLOBAL = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');

/* ============== BASE RESET ============== */
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}}

/* ============== APP BACKGROUND ============== */
.stApp {{
    background: {T["app_bg"]} !important;
    color: {T["text_main"]} !important;
}}

/* Header transparente */
header[data-testid="stHeader"] {{
    background: transparent !important;
    backdrop-filter: none !important;
}}

/* ============== MAIN CONTENT AREA — previne fundo branco ============== */
section.main > div.block-container {{
    background: transparent !important;
    color: {T["text_main"]} !important;
}}
section.main {{
    background: transparent !important;
}}

/* ============== SIDEBAR ============== */
section[data-testid="stSidebar"] {{
    background: {T["sidebar_bg"]} !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1px solid {T["border"]} !important;
}}
section[data-testid="stSidebar"] * {{
    color: {T["text_main"]} !important;
}}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stMarkdown label {{
    color: {T["text_main"]} !important;
}}

/* ============== INPUTS / SELECTS / TEXTAREAS ============== */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="base-input"] > div,
div[data-baseweb="textarea"] > div,
input, textarea {{
    background-color: {T["input_bg"]} !important;
    color: {T["text_main"]} !important;
    border-color: {T["input_border"]} !important;
    border-radius: 10px !important;
    caret-color: {T["accent_cyan"]} !important;
}}
/* Select value text */
div[data-baseweb="select"] span {{
    color: {T["text_main"]} !important;
}}

/* ============== DROPDOWNS / POPOVERS ============== */
div[data-baseweb="popover"] {{
    background-color: {T["surface_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 12px !important;
    backdrop-filter: blur(20px) !important;
}}
ul[role="listbox"] {{
    background-color: {T["surface_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 12px !important;
}}
ul[role="listbox"] li {{
    color: {T["text_main"]} !important;
    background-color: transparent !important;
}}
ul[role="listbox"] li:hover {{
    background-color: {T["btn_hover_bg"]} !important;
}}

/* ============== EXPANDERS ============== */
div[data-testid="stExpander"] {{
    background: {T["surface_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 14px !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: none !important;
}}
div[data-testid="stExpander"] summary {{
    color: {T["text_main"]} !important;
    font-weight: 600 !important;
}}
div[data-testid="stExpander"] summary:hover {{
    color: {T["accent_cyan"]} !important;
}}
div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
    background: transparent !important;
}}
div[data-testid="stExpander"] p,
div[data-testid="stExpander"] span,
div[data-testid="stExpander"] label {{
    color: {T["text_main"]} !important;
}}

/* ============== FORMS ============== */
div[data-testid="stForm"] {{
    background: {T["surface_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 14px !important;
    backdrop-filter: blur(12px) !important;
}}

/* ============== BUTTONS ============== */
div.stButton > button {{
    background: {T["btn_bg"]} !important;
    color: {T["text_main"]} !important;
    border: 1px solid {T["btn_border"]} !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    backdrop-filter: blur(8px) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
div.stButton > button:hover {{
    border-color: {T["border_hover"]} !important;
    background: {T["btn_hover_bg"]} !important;
    transform: translateY(-1px) !important;
    box-shadow: {T["card_shadow"]} !important;
}}
div.stButton > button:active {{
    transform: translateY(0px) !important;
}}
/* Primary button */
div.stButton > button[kind="primary"],
button[kind="primary"] {{
    background: linear-gradient(135deg, {T["accent_cyan"]}, {T["accent_blue"]}) !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 700 !important;
}}
div.stButton > button[kind="primary"]:hover,
button[kind="primary"]:hover {{
    opacity: 0.9 !important;
    box-shadow: 0 4px 20px {T["accent_cyan"]}40 !important;
}}

/* Form submit buttons */
div[data-testid="stForm"] button[kind="secondaryFormSubmit"],
div[data-testid="stForm"] button[kind="primaryFormSubmit"] {{
    background: {T["btn_bg"]} !important;
    color: {T["text_main"]} !important;
    border: 1px solid {T["btn_border"]} !important;
    border-radius: 10px !important;
}}
div[data-testid="stForm"] button[kind="primaryFormSubmit"] {{
    background: linear-gradient(135deg, {T["accent_cyan"]}, {T["accent_blue"]}) !important;
    color: #ffffff !important;
    border: none !important;
}}

/* Download button */
div.stDownloadButton > button {{
    background: {T["btn_bg"]} !important;
    color: {T["text_main"]} !important;
    border: 1px solid {T["btn_border"]} !important;
    border-radius: 10px !important;
}}
div.stDownloadButton > button:hover {{
    border-color: {T["border_hover"]} !important;
    background: {T["btn_hover_bg"]} !important;
}}

/* ============== TABS ============== */
div[data-testid="stTabs"] {{
    background: transparent !important;
}}
div[data-testid="stTabs"] button {{
    color: {T["text_muted"]} !important;
    font-weight: 600 !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
    padding: 10px 18px !important;
    transition: all 0.2s ease !important;
}}
div[data-testid="stTabs"] button:hover {{
    color: {T["text_sub"]} !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {T["accent_cyan"]} !important;
    border-bottom: 2px solid {T["accent_cyan"]} !important;
}}

/* ============== ALERTS (st.info, st.success, st.warning, st.error) ============== */
div[data-testid="stAlert"] {{
    background: {T["surface_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 12px !important;
    color: {T["text_main"]} !important;
    backdrop-filter: blur(8px) !important;
}}
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {{
    color: {T["text_main"]} !important;
}}

/* ============== CODE BLOCKS ============== */
div[data-testid="stCode"],
code, pre {{
    background-color: {T["input_bg"]} !important;
    color: {T["text_main"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
}}

/* ============== CAPTION / MUTED TEXT ============== */
div[data-testid="stCaptionContainer"] p {{
    color: {T["text_muted"]} !important;
}}

/* ============== MARKDOWN TEXT ============== */
.stMarkdown p, .stMarkdown span, .stMarkdown li {{
    color: {T["text_main"]} !important;
}}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
    color: {T["text_main"]} !important;
}}

/* ============== CHECKBOX ============== */
div[data-testid="stCheckbox"] label span {{
    color: {T["text_main"]} !important;
}}

/* ============== METRIC (native) ============== */
div[data-testid="stMetric"] {{
    background: transparent !important;
}}
div[data-testid="stMetric"] label {{
    color: {T["text_sub"]} !important;
}}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    color: {T["text_main"]} !important;
}}

/* ============== TOAST ============== */
div[data-testid="stToast"] {{
    background: {T["surface_card"]} !important;
    border: 1px solid {T["border"]} !important;
    color: {T["text_main"]} !important;
    backdrop-filter: blur(16px) !important;
    border-radius: 12px !important;
}}

/* ============== DIVIDERS ============== */
hr {{
    border-color: {T["border"]} !important;
}}

/* ============== PLOTLY CONTAINER (prevent white wrapper) ============== */
div.stPlotlyChart {{
    background: transparent !important;
}}
div.stPlotlyChart > div {{
    background: transparent !important;
}}
iframe {{
    background: transparent !important;
}}

/* ============== SCROLLBARS (Dark theme polish) ============== */
::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
::-webkit-scrollbar-track {{
    background: transparent;
}}
::-webkit-scrollbar-thumb {{
    background: {T["text_muted"]}40;
    border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: {T["text_muted"]}80;
}}

/* ============== BOTTOM DECORATION / FOOTER ============== */
footer {{
    background: transparent !important;
    color: {T["text_muted"]} !important;
}}
footer a {{
    color: {T["text_muted"]} !important;
}}

/* ============== ANIMATIONS ============== */
@keyframes pulse-glow {{
    0%   {{ transform: scale(0.95); opacity: 0.7; }}
    50%  {{ transform: scale(1.2);  opacity: 1; }}
    100% {{ transform: scale(0.95); opacity: 0.7; }}
}}
@keyframes shimmer {{
    0%   {{ background-position: -200% 0; }}
    100% {{ background-position: 200% 0; }}
}}

/* ============== CUSTOM COMPONENT CLASSES ============== */

/* --- Navbar Glassmorphism --- */
.ms-navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: {T["surface"]};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid {T["border"]};
    border-radius: 18px;
    padding: 16px 28px;
    margin-bottom: 28px;
    box-shadow: {T["card_shadow"]};
}}
.ms-brand {{
    display: flex;
    align-items: center;
    gap: 14px;
}}
.ms-brand-icon {{
    background: linear-gradient(135deg, {T["accent_cyan"]}, {T["accent_blue"]});
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 20px {T["accent_cyan"]}35;
}}
.ms-brand-title {{
    margin: 0;
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: {T["text_main"]};
}}
.ms-brand-sub {{
    margin: 0;
    font-size: 0.72rem;
    color: {T["text_sub"]};
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}
.ms-live {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: {T["accent_emerald"]}15;
    border: 1px solid {T["accent_emerald"]}40;
    color: {T["accent_emerald"]};
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}}
.ms-live-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {T["accent_emerald"]};
    box-shadow: 0 0 10px {T["accent_emerald"]};
    animation: pulse-glow 2s ease-in-out infinite;
}}

/* --- KPI Cards --- */
.ms-kpi {{
    background: {T["surface_card"]};
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid {T["border"]};
    border-radius: 16px;
    padding: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: {T["card_shadow"]};
    position: relative;
    overflow: hidden;
}}
.ms-kpi::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
    opacity: 0;
    transition: opacity 0.3s ease;
}}
.ms-kpi:hover {{
    border-color: {T["border_hover"]};
    box-shadow: {T["card_hover_shadow"]};
    transform: translateY(-2px);
}}
.ms-kpi:hover::before {{
    opacity: 1;
}}
.ms-kpi-label {{
    font-size: 0.72rem;
    font-weight: 700;
    color: {T["text_sub"]};
    text-transform: uppercase;
    letter-spacing: 0.6px;
}}
.ms-kpi-value {{
    font-family: 'Space Grotesk', monospace;
    font-size: 2.3rem;
    font-weight: 700;
    color: {T["text_main"]};
    margin: 8px 0 4px 0;
    line-height: 1;
    font-feature-settings: 'tnum' 1, 'zero' 1;
}}
.ms-kpi-desc {{
    font-size: 0.74rem;
    color: {T["text_muted"]};
    font-weight: 500;
}}

/* --- Machine Cards --- */
.ms-machine {{
    background: {T["surface_card"]};
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid {T["border"]};
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 16px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: {T["card_shadow"]};
}}
.ms-machine:hover {{
    border-color: {T["border_hover"]};
    box-shadow: {T["card_hover_shadow"]};
    transform: translateY(-2px);
}}

/* --- Status Pills --- */
.ms-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}}
.ms-pill-ok {{
    background: {T["accent_emerald"]}15;
    border: 1px solid {T["accent_emerald"]}40;
    color: {T["accent_emerald"]};
}}
.ms-pill-warn {{
    background: {T["accent_rose"]}15;
    border: 1px solid {T["accent_rose"]}40;
    color: {T["accent_rose"]};
}}
.ms-pill-idle {{
    background: {T["text_muted"]}15;
    border: 1px solid {T["text_muted"]}35;
    color: {T["text_muted"]};
}}

/* --- Sensor Mini-cards --- */
.ms-sensor {{
    background: {T["surface_metric"]};
    backdrop-filter: blur(8px);
    border: 1px solid {T["border"]};
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}}
.ms-sensor-val {{
    font-family: 'Space Grotesk', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 6px 0;
    font-feature-settings: 'tnum' 1, 'zero' 1;
}}

/* --- Diagnostic Card --- */
.ms-diag {{
    background: {T["surface_card"]};
    backdrop-filter: blur(16px);
    border: 1px solid {T["accent_violet"]}30;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 0 24px {T["accent_violet"]}08;
}}

/* --- Info Banner --- */
.ms-info {{
    background: {T["surface_card"]};
    backdrop-filter: blur(12px);
    border: 1px solid {T["accent_cyan"]}25;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 24px;
    border-left: 3px solid {T["accent_cyan"]};
}}

</style>
"""
st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Componentes Visuais
# ---------------------------------------------------------------------------
def renderizar_topbar():
    """Barra superior glassmorphism com glow animado."""
    agora = datetime.now().strftime("%d/%m/%Y • %H:%M")
    ico = get_icon("cpu", color="#ffffff", size=22)

    html = f"""\
<div class="ms-navbar">
<div class="ms-brand">
<div class="ms-brand-icon">{ico}</div>
<div>
<h1 class="ms-brand-title">MetalSense</h1>
<p class="ms-brand-sub">Monitoramento Inteligente de Máquinas</p>
</div>
</div>
<div style="display: flex; align-items: center; gap: 18px;">
<span style="color: {T['text_sub']}; font-size: 0.82rem; font-family: 'Space Grotesk', monospace; font-weight: 600;">{agora}</span>
<span class="ms-live"><span class="ms-live-dot"></span> Online</span>
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def renderizar_kpis_topo(maquinas: list):
    """Métricas superiores com glassmorphism e glow."""
    total_maquinas = len(maquinas)
    total_anomalias = sum(1 for m in maquinas if m.get("status") == "anomalia")
    total_leituras = sum(len(m.get("historico", [])) for m in maquinas)

    scores = []
    for m in maquinas:
        hist = m.get("historico", [])
        if hist:
            scores.append(calcular_indice_saude(hist)["score"])
    media_saude = round(sum(scores) / len(scores), 1) if scores else 100.0

    c1, c2, c3, c4 = st.columns(4)

    kpi_data = [
        (c1, "server",   T["accent_cyan"],    "Máquinas",         f"{total_maquinas:02d}",  "Equipamentos cadastrados"),
        (c2, "shield",   T["accent_emerald"],  "Saúde Geral",     f"{media_saude}%",        "Média de funcionamento"),
        (c3, "alert",    T["accent_rose"] if total_anomalias > 0 else T["accent_emerald"],
                                              "Alertas",           f"{total_anomalias:02d}", f"{total_anomalias} precisam de atenção" if total_anomalias > 0 else "Tudo funcionando bem"),
        (c4, "activity", T["accent_violet"],  "Medições",          f"{total_leituras:,}",    "Leituras registradas"),
    ]

    for col, icon_name, accent, label, value, desc in kpi_data:
        with col:
            ico = get_icon(icon_name, color=accent, size=18)
            # Color the value specially for health and alerts
            val_color = T["text_main"]
            if label == "Saúde Geral":
                val_color = T["accent_emerald"] if media_saude >= 75 else (T["accent_amber"] if media_saude >= 50 else T["accent_rose"])
            elif label == "Alertas":
                val_color = accent

            html = f"""\
<div class="ms-kpi" style="border-top: 2px solid {accent}30;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="ms-kpi-label">{label}</span>
<span style="background: {accent}12; padding: 7px; border-radius: 10px; display: flex;">{ico}</span>
</div>
<div class="ms-kpi-value" style="color: {val_color};">{value}</div>
<div class="ms-kpi-desc">{desc}</div>
</div>"""
            st.markdown(html, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 28px;'></div>", unsafe_allow_html=True)


def criar_gauge_saude(score: float) -> go.Figure:
    """Velocímetro limpo com cores consistentes ao tema."""
    cor = T["accent_emerald"] if score >= 75 else (T["accent_amber"] if score >= 50 else T["accent_rose"])

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={
                'suffix': "%",
                'font': {'size': 42, 'color': T["text_main"], 'family': 'Space Grotesk, monospace'},
            },
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': T["text_muted"], 'nticks': 5,
                         'tickfont': {'color': T["text_muted"], 'size': 10}},
                'bar': {'color': cor, 'thickness': 0.28},
                'bgcolor': T["gauge_bg"],
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50],  'color': f"{T['accent_rose']}18"},
                    {'range': [50, 75], 'color': f"{T['accent_amber']}18"},
                    {'range': [75, 100],'color': f"{T['accent_emerald']}18"},
                ],
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=185,
        margin=dict(l=15, r=15, t=10, b=10),
        font={'color': T["text_main"]},
    )
    return fig


def criar_grafico_telemetria(
    df: pd.DataFrame, metrica: str, titulo: str, unidade: str, limite: float, cor_linha: str
) -> go.Figure:
    """Gráfico interativo com curva suave e linha de limite."""
    fig = go.Figure()

    fig.add_hline(
        y=limite,
        line_dash="dash",
        line_color=T["accent_rose"],
        line_width=1.5,
        annotation_text=f"Limite ({limite} {unidade})",
        annotation_position="top right",
        annotation_font=dict(color=T["accent_rose"], size=10, family="Space Grotesk"),
    )

    # Parse color for fill
    try:
        r = int(cor_linha[1:3], 16)
        g = int(cor_linha[3:5], 16)
        b = int(cor_linha[5:7], 16)
        fill_rgba = f"rgba({r}, {g}, {b}, 0.10)"
    except (ValueError, IndexError):
        fill_rgba = "rgba(0, 229, 255, 0.10)"

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"] if "timestamp" in df.columns else list(range(len(df))),
            y=df[metrica],
            mode="lines+markers",
            name=f"{titulo} ({unidade})",
            line=dict(color=cor_linha, width=2.5, shape="spline"),
            marker=dict(size=5, color=cor_linha, symbol="circle"),
            fill="tozeroy",
            fillcolor=fill_rgba,
            hovertemplate="<b>%{y:.2f} " + unidade + "</b><br>%{x}<extra></extra>",
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=T["plot_bg"],
        hovermode="x unified",
        margin=dict(l=10, r=10, t=30, b=10),
        height=300,
        xaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                   tickfont=dict(size=10, color=T["plot_text"])),
        yaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                   tickfont=dict(size=10, color=T["plot_text"])),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(color=T["text_sub"], size=11)),
        font={'color': T["text_main"]},
    )
    return fig


# ---------------------------------------------------------------------------
# Página 1 — Início
# ---------------------------------------------------------------------------
def renderizar_pagina_inicio(dados: dict, maquinas: list):
    """Página inicial limpa e interativa."""
    info_html = f"""\
<div class="ms-info">
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
{get_icon('info', color=T['accent_cyan'], size=18)}
<strong style="font-size: 0.95rem; color: {T['text_main']};">Como o MetalSense funciona?</strong>
</div>
<p style="margin: 0; font-size: 0.88rem; color: {T['text_sub']}; line-height: 1.6;">
O sistema monitora sensores das máquinas e detecta problemas <strong style="color: {T['text_main']};">antes que elas quebrem</strong>.
Se a temperatura, vibração ou consumo saírem do padrão, um alerta é emitido imediatamente.
</p>
</div>"""
    st.markdown(info_html, unsafe_allow_html=True)

    st.markdown(f"### Suas Máquinas")
    st.caption("Clique em qualquer máquina para ver gráficos e detalhes completos.")

    if not maquinas:
        st.info("Nenhuma máquina cadastrada ainda. Use a barra lateral para adicionar a primeira!")
        return

    cols = st.columns(2)
    for i, m in enumerate(maquinas):
        with cols[i % 2]:
            id_m = m["id"]
            nome_m = m["nome"]
            status_m = m.get("status", "sem dados").lower()
            hist = m.get("historico", [])
            saude = calcular_indice_saude(hist)
            score = saude["score"]

            if status_m == "normal":
                pill_cls = "ms-pill-ok"
                status_txt = "Normal"
            elif status_m == "anomalia":
                pill_cls = "ms-pill-warn"
                status_txt = "Atenção"
            else:
                pill_cls = "ms-pill-idle"
                status_txt = "Aguardando Dados"

            ult_temp = f"{hist[-1]['temperatura']}°C" if hist else "—"
            ult_vib  = f"{hist[-1]['vibracao']} mm/s" if hist else "—"
            ult_cons = f"{hist[-1]['consumo']} W" if hist else "—"

            cor_hp = T["accent_emerald"] if score >= 75 else (T["accent_amber"] if score >= 50 else T["accent_rose"])

            card_html = f"""\
<div class="ms-machine">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px;">
<div>
<span style="font-size: 0.72rem; font-weight: 700; color: {T['accent_cyan']}; letter-spacing: 0.5px;">MÁQUINA #{id_m:02d}</span>
<h3 style="margin: 3px 0 0 0; font-size: 1.2rem; font-weight: 700; color: {T['text_main']};">{nome_m}</h3>
</div>
<span class="ms-pill {pill_cls}">{status_txt}</span>
</div>
<div style="margin: 12px 0 10px 0;">
<div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 5px;">
<span style="color: {T['text_sub']};">Saúde</span>
<span style="color: {cor_hp}; font-weight: 700; font-family: 'Space Grotesk', monospace;">{score}%</span>
</div>
<div style="background: {T['border']}; height: 5px; border-radius: 9999px; overflow: hidden;">
<div style="background: linear-gradient(90deg, {cor_hp}, {cor_hp}cc); width: {score}%; height: 100%; border-radius: 9999px; box-shadow: 0 0 8px {cor_hp}50;"></div>
</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 14px;">
<div style="background: {T['surface_metric']}; border: 1px solid {T['border']}; padding: 8px; border-radius: 10px; text-align: center;">
<div style="font-size: 0.68rem; color: {T['text_muted']}; text-transform: uppercase; font-weight: 600;">Temp</div>
<div style="font-size: 0.92rem; font-weight: 700; color: {T['text_main']}; font-family: 'Space Grotesk', monospace;">{ult_temp}</div>
</div>
<div style="background: {T['surface_metric']}; border: 1px solid {T['border']}; padding: 8px; border-radius: 10px; text-align: center;">
<div style="font-size: 0.68rem; color: {T['text_muted']}; text-transform: uppercase; font-weight: 600;">Vibração</div>
<div style="font-size: 0.92rem; font-weight: 700; color: {T['text_main']}; font-family: 'Space Grotesk', monospace;">{ult_vib}</div>
</div>
<div style="background: {T['surface_metric']}; border: 1px solid {T['border']}; padding: 8px; border-radius: 10px; text-align: center;">
<div style="font-size: 0.68rem; color: {T['text_muted']}; text-transform: uppercase; font-weight: 600;">Consumo</div>
<div style="font-size: 0.92rem; font-weight: 700; color: {T['text_main']}; font-family: 'Space Grotesk', monospace;">{ult_cons}</div>
</div>
</div>
</div>"""
            st.markdown(card_html, unsafe_allow_html=True)

            if st.button(f"Inspecionar {nome_m} ➔", key=f"btn_ver_{id_m}", width='stretch'):
                st.session_state["maquina_ativa_id"] = id_m
                st.rerun()

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    if st.button("Coletar Leitura Normal para Todas as Máquinas", width='stretch'):
        for m in maquinas:
            registrar_leitura(dados, m["id"], gerar_anomalia=False)
        st.toast("Leituras registradas para todas as máquinas!", icon="✅")
        st.rerun()


# ---------------------------------------------------------------------------
# Página 2 — Detalhes da Máquina
# ---------------------------------------------------------------------------
def renderizar_detalhes_maquina(dados: dict, maquina: dict):
    """Tela detalhada de uma máquina."""
    id_m = maquina["id"]
    nome_m = maquina["nome"]
    historico = maquina.get("historico", [])
    status_m = maquina.get("status", "sem dados").lower()

    diagnostico_texto = analisar_maquina(dados, id_m)
    saude = calcular_indice_saude(historico)
    score = saude["score"]

    # Voltar
    if st.button("⬅ Voltar para Todas as Máquinas", width='content'):
        st.session_state["maquina_ativa_id"] = None
        st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    if status_m == "normal":
        pill_cls = "ms-pill-ok"
        status_txt = "Operação Normal"
    elif status_m == "anomalia":
        pill_cls = "ms-pill-warn"
        status_txt = "Falha Detectada"
    else:
        pill_cls = "ms-pill-idle"
        status_txt = "Aguardando Dados"

    # Header
    c_h1, c_h2 = st.columns([3, 1])
    with c_h1:
        hdr = f"""\
<div>
<span style="font-size: 0.76rem; font-weight: 700; color: {T['accent_cyan']}; letter-spacing: 0.5px;">ATIVO #{id_m:02d}</span>
<h1 style="margin: 3px 0 0 0; font-size: 2rem; font-weight: 800; color: {T['text_main']};">{nome_m}</h1>
<p style="margin: 5px 0 0 0; color: {T['text_sub']}; font-size: 0.88rem;">{len(historico)} medições registradas</p>
</div>"""
        st.markdown(hdr, unsafe_allow_html=True)
    with c_h2:
        st.markdown(
            f'<div style="text-align: right; margin-top: 16px;"><span class="ms-pill {pill_cls}">{status_txt}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Gauge + Diagnóstico
    col_gauge, col_ai = st.columns([1, 2])

    with col_gauge:
        gauge_wrap = f"""\
<div style="background: {T['surface_card']}; backdrop-filter: blur(16px); border: 1px solid {T['border']}; border-radius: 16px; padding: 16px; text-align: center; box-shadow: {T['card_shadow']};">
<span style="font-size: 0.72rem; font-weight: 700; color: {T['text_sub']}; text-transform: uppercase; letter-spacing: 0.5px;">Saúde do Ativo</span>"""
        st.markdown(gauge_wrap, unsafe_allow_html=True)
        st.plotly_chart(criar_gauge_saude(score), width='stretch')
        # Status abaixo do gauge
        st.markdown(
            f'<div style="margin-top: -15px; margin-bottom: 8px;"><span class="ms-pill {pill_cls}">{saude["classificacao"].upper()}</span></div></div>',
            unsafe_allow_html=True,
        )

    with col_ai:
        diag_html = f"""\
<div class="ms-diag">
<div style="font-size: 0.82rem; font-weight: 700; color: {T['accent_violet']}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px;">
Diagnóstico Automático
</div>
<div style="font-size: 1.02rem; line-height: 1.6; color: {T['text_main']};">
{diagnostico_texto}
</div>"""
        st.markdown(diag_html, unsafe_allow_html=True)

        if saude.get("hipoteses"):
            st.markdown("<div style='margin-top: 12px;'>", unsafe_allow_html=True)
            for hip in saude["hipoteses"]:
                hip_html = f"""\
<span style="display: inline-flex; align-items: center; gap: 6px; background: {T['accent_rose']}12; border: 1px solid {T['accent_rose']}35; color: {T['accent_rose']}; padding: 5px 14px; border-radius: 8px; font-size: 0.78rem; font-weight: 600; margin-right: 6px; margin-top: 6px;">
{get_icon('alert', color=T['accent_rose'], size=13)} {hip}
</span>"""
                st.markdown(hip_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        tend = saude.get("tendencias", {})
        tend_html = f"""\
<div style="display: flex; gap: 20px; margin-top: 18px; font-size: 0.84rem; color: {T['text_sub']}; border-top: 1px solid {T['border']}; padding-top: 14px;">
<div>Temperatura: <strong style="color: {T['text_main']};">{tend.get('temperatura', 'Estável')}</strong></div>
<div>Vibração: <strong style="color: {T['text_main']};">{tend.get('vibracao', 'Estável')}</strong></div>
<div>Consumo: <strong style="color: {T['text_main']};">{tend.get('consumo', 'Estável')}</strong></div>
</div>
</div>"""
        st.markdown(tend_html, unsafe_allow_html=True)

    # Sensores da última leitura
    if historico:
        ult = historico[-1]
        t_val = ult.get("temperatura", 0.0)
        v_val = ult.get("vibracao", 0.0)
        c_val = ult.get("consumo", 0.0)
        hora = ult.get("timestamp", "—")

        sc1, sc2, sc3, sc4 = st.columns(4)
        sensor_data = [
            (sc1, "Temperatura", t_val, "°C", t_val > 85.0, "Muito quente" if t_val > 85.0 else "Normal"),
            (sc2, "Vibração",    v_val, "mm/s", v_val > 8.0, "Alta" if v_val > 8.0 else "Normal"),
            (sc3, "Consumo",     c_val, "W",   c_val > 500.0, "Sobrecarga" if c_val > 500.0 else "Normal"),
        ]
        for col, nome, val, unit, is_alert, txt in sensor_data:
            with col:
                cor = T["accent_rose"] if is_alert else T["accent_emerald"]
                html = f"""\
<div class="ms-sensor">
<div style="font-size: 0.72rem; color: {T['text_sub']}; font-weight: 700; text-transform: uppercase;">{nome}</div>
<div class="ms-sensor-val" style="color: {cor};">{val} <span style="font-size: 1rem;">{unit}</span></div>
<span style="font-size: 0.7rem; font-weight: 700; color: {cor};">{txt}</span>
</div>"""
                st.markdown(html, unsafe_allow_html=True)
        with sc4:
            html = f"""\
<div class="ms-sensor">
<div style="font-size: 0.72rem; color: {T['text_sub']}; font-weight: 700; text-transform: uppercase;">Última Leitura</div>
<div class="ms-sensor-val" style="color: {T['accent_cyan']}; font-size: 1.3rem; margin-top: 10px;">{hora.split(' ')[-1] if ' ' in hora else hora}</div>
<span style="font-size: 0.7rem; font-weight: 600; color: {T['text_muted']};">{hora.split(' ')[0] if ' ' in hora else 'Hoje'}</span>
</div>"""
            st.markdown(html, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Ações
    st.markdown("#### Ações")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("+ Leitura Normal", width='stretch'):
            registrar_leitura(dados, id_m, gerar_anomalia=False)
            st.toast("Leitura normal registrada!", icon="✅")
            st.rerun()
    with b2:
        if st.button("Simular Falha", type="primary", width='stretch'):
            registrar_leitura(dados, id_m, gerar_anomalia=True)
            st.toast("Falha simulada!", icon="🚨")
            st.rerun()
    with b3:
        if st.button("Atualizar Análise", width='stretch'):
            analisar_maquina(dados, id_m)
            st.toast("Análise atualizada!", icon="🔄")
            st.rerun()

    with st.expander("Simular Falhas Específicas", expanded=False):
        st.caption("Escolha um cenário:")
        sb1, sb2, sb3 = st.columns(3)
        with sb1:
            if st.button("Desgaste de Rolamento", width='stretch'):
                leit = gerar_leitura_cenario("rolamento", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Cenário de Rolamento injetado!", icon="⚙️")
                st.rerun()
        with sb2:
            if st.button("Superaquecimento", width='stretch'):
                leit = gerar_leitura_cenario("aquecimento", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Superaquecimento injetado!", icon="🔥")
                st.rerun()
        with sb3:
            if st.button("Sobrecarga Elétrica", width='stretch'):
                leit = gerar_leitura_cenario("sobrecarga", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Sobrecarga injetada!", icon="⚡")
                st.rerun()

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Gráficos
    st.markdown("#### Histórico em Gráficos")

    if len(historico) < 2:
        st.info("Poucas leituras (mínimo 2). Clique em '+ Leitura Normal' para gerar dados.")
    else:
        df_hist = pd.DataFrame(historico)

        tab1, tab2, tab3, tab4 = st.tabs(["Temperatura", "Vibração", "Consumo", "Todos Juntos"])

        with tab1:
            st.plotly_chart(
                criar_grafico_telemetria(df_hist, "temperatura", "Temperatura", "°C", 85.0, T["accent_cyan"]),
                width='stretch',
            )
        with tab2:
            st.plotly_chart(
                criar_grafico_telemetria(df_hist, "vibracao", "Vibração", "mm/s", 8.0, T["accent_amber"]),
                width='stretch',
            )
        with tab3:
            st.plotly_chart(
                criar_grafico_telemetria(df_hist, "consumo", "Consumo", "W", 500.0, T["accent_violet"]),
                width='stretch',
            )
        with tab4:
            fig_multi = go.Figure()
            for col_name, cor, nome in [
                ("temperatura", T["accent_cyan"],   "Temp (°C)"),
                ("vibracao",    T["accent_amber"],  "Vibração (mm/s)"),
                ("consumo",     T["accent_violet"], "Consumo (W)"),
            ]:
                fig_multi.add_trace(
                    go.Scatter(x=df_hist["timestamp"], y=df_hist[col_name], mode="lines",
                               name=nome, line=dict(color=cor, width=2.5))
                )
            fig_multi.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor=T["plot_bg"],
                hovermode="x unified",
                margin=dict(l=10, r=10, t=30, b=10),
                height=320,
                xaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                           tickfont=dict(color=T["plot_text"])),
                yaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                           tickfont=dict(color=T["plot_text"])),
                legend=dict(font=dict(color=T["text_sub"])),
                font={'color': T["text_main"]},
            )
            st.plotly_chart(fig_multi, width='stretch')

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Exportar
    st.markdown("#### Baixar Relatórios")
    if historico:
        with st.expander("Baixar Histórico em Planilha ou Laudo Técnico", expanded=False):
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                csv_buf = io.StringIO()
                w = csv.DictWriter(csv_buf, fieldnames=["timestamp", "temperatura", "vibracao", "consumo"])
                w.writeheader()
                for r in historico:
                    w.writerow({
                        "timestamp": r.get("timestamp", ""),
                        "temperatura": r.get("temperatura", 0.0),
                        "vibracao": r.get("vibracao", 0.0),
                        "consumo": r.get("consumo", 0.0),
                    })
                st.download_button(
                    label="Baixar Planilha (CSV)",
                    data=csv_buf.getvalue(),
                    file_name=f"historico_maquina_{id_m}.csv",
                    mime="text/csv",
                    width='stretch',
                )
            with t_col2:
                caminho_html = gerar_relatorio_html(maquina)
                with open(caminho_html, "r", encoding="utf-8") as f_html:
                    html_data = f_html.read()
                st.download_button(
                    label="Baixar Laudo Técnico (HTML)",
                    data=html_data,
                    file_name=f"laudo_maquina_{id_m}.html",
                    mime="text/html",
                    width='stretch',
                )

            st.markdown("##### Ordem de Serviço:")
            st.code(gerar_ordem_servico_texto(maquina), language="text")


# ---------------------------------------------------------------------------
# Fluxo Principal & Barra Lateral
# ---------------------------------------------------------------------------
def main():
    dados = carregar_dados()
    maquinas = dados.get("maquinas", [])

    renderizar_topbar()
    renderizar_kpis_topo(maquinas)

    # Sidebar
    with st.sidebar:
        st.markdown(
            f"<p style='font-size: 0.72rem; font-weight: 700; text-transform: uppercase; margin-top: 10px; margin-bottom: 6px; letter-spacing: 0.6px; color: {T['text_sub']};'>Navegação</p>",
            unsafe_allow_html=True,
        )

        opcoes = ["Todas as Máquinas"]
        mapa_ids = {"Todas as Máquinas": None}
        idx_sel = 0

        for i, m in enumerate(maquinas):
            label = f"[#{m['id']:02d}] {m['nome']}"
            opcoes.append(label)
            mapa_ids[label] = m["id"]
            if st.session_state["maquina_ativa_id"] == m["id"]:
                idx_sel = i + 1

        escolha = st.selectbox("Ver máquina:", options=opcoes, index=idx_sel, label_visibility="collapsed")

        novo_id = mapa_ids.get(escolha)
        if novo_id != st.session_state["maquina_ativa_id"]:
            st.session_state["maquina_ativa_id"] = novo_id
            st.rerun()

        st.markdown("---")

        st.markdown(
            f"<p style='font-size: 0.72rem; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.6px; color: {T['text_sub']};'>Nova Máquina</p>",
            unsafe_allow_html=True,
        )
        with st.form("form_nova_maquina", clear_on_submit=True):
            nome_input = st.text_input("Nome da Máquina:", placeholder="Ex: Torno CNC 03", label_visibility="collapsed")
            btn_add = st.form_submit_button("+ Cadastrar", width='stretch')

            if btn_add:
                nome_limpo = nome_input.strip()
                if not nome_limpo:
                    st.error("Digite um nome para a máquina.")
                else:
                    try:
                        nova = criar_maquina(dados, nome_limpo)
                        st.toast(f"Máquina '{nova['nome']}' cadastrada!", icon="✅")
                        st.session_state["maquina_ativa_id"] = nova["id"]
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

        # Excluir
        if st.session_state["maquina_ativa_id"] is not None:
            maq_atual = next((m for m in maquinas if m["id"] == st.session_state["maquina_ativa_id"]), None)
            if maq_atual:
                st.markdown("---")
                st.markdown(
                    f"<p style='font-size: 0.72rem; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.6px; color: {T['text_sub']};'>Excluir Máquina</p>",
                    unsafe_allow_html=True,
                )
                with st.expander("Apagar esta máquina", expanded=False):
                    st.caption(f"Remove '{maq_atual['nome']}' e todo o histórico.")
                    confirm = st.checkbox("Sim, quero apagar", key=f"del_{maq_atual['id']}")
                    if st.button("Confirmar Exclusão", type="primary", disabled=not confirm, width='stretch'):
                        if remover_maquina(dados, maq_atual["id"]):
                            st.toast("Máquina removida!", icon="🗑️")
                            st.session_state["maquina_ativa_id"] = None
                            st.rerun()

        st.markdown("---")
        st.caption("MetalSense • Projeto TechForge")

    # Render
    maquina_selecionada = None
    if st.session_state["maquina_ativa_id"] is not None:
        maquina_selecionada = next((m for m in maquinas if m["id"] == st.session_state["maquina_ativa_id"]), None)

    if maquina_selecionada is None:
        renderizar_pagina_inicio(dados, maquinas)
    else:
        renderizar_detalhes_maquina(dados, maquina_selecionada)


if __name__ == "__main__":
    main()
