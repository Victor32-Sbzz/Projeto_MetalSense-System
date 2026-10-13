import streamlit as st
from datetime import datetime
import io
import csv
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
    page_title="MetalSense | Industrial Predictive OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Biblioteca de Ícones SVG Profissionais (Vetorizados, Minimalistas, Sem Emojis)
# -----------------------------------------------------------------------------
ICONS = {
    "cpu": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>',
    "activity": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
    "alert": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    "thermometer": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"></path></svg>',
    "zap": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>',
    "waves": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path></svg>',
    "server": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>',
    "file": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>',
    "refresh": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>',
    "brain": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"></path></svg>',
    "sun": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>',
    "moon": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>',
    "radio": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="2"></circle><path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"></path></svg>',
}


def get_icon(name: str, color: str = "currentColor", size: int = 18) -> str:
    """Retorna o código SVG do ícone renderizado inline."""
    template = ICONS.get(name, "")
    return template.format(s=size, c=color)


# -----------------------------------------------------------------------------
# Gerenciador de Temas (Dark Mode / Light Mode)
# -----------------------------------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"

# Botão de Tema no Topo da Barra Lateral
with st.sidebar:
    st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)
    c_t1, c_t2 = st.columns([1, 1])
    with c_t1:
        if st.button("Modo Escuro", use_container_width=True, type="primary" if st.session_state["theme_mode"] == "dark" else "secondary"):
            st.session_state["theme_mode"] = "dark"
            st.rerun()
    with c_t2:
        if st.button("Modo Claro", use_container_width=True, type="primary" if st.session_state["theme_mode"] == "light" else "secondary"):
            st.session_state["theme_mode"] = "light"
            st.rerun()

IS_DARK = st.session_state["theme_mode"] == "dark"

# Definição das Variáveis de Estilo para Cada Tema
if IS_DARK:
    T = {
        "app_bg": "radial-gradient(circle at 10% 20%, #0d1527 0%, #060911 85%)",
        "surface": "rgba(15, 23, 42, 0.75)",
        "surface_card": "rgba(15, 23, 42, 0.65)",
        "surface_metric": "rgba(15, 23, 42, 0.8)",
        "sidebar_bg": "#080c14",
        "border": "rgba(255, 255, 255, 0.08)",
        "border_hover": "rgba(56, 189, 248, 0.4)",
        "input_bg": "#0f172a",
        "input_border": "rgba(255, 255, 255, 0.12)",
        "text_main": "#f8fafc",
        "text_sub": "#94a3b8",
        "text_muted": "#64748b",
        "accent_cyan": "#00f2fe",
        "accent_blue": "#38bdf8",
        "accent_emerald": "#10b981",
        "accent_amber": "#f59e0b",
        "accent_rose": "#ef4444",
        "accent_violet": "#a855f7",
        "plot_paper": "rgba(0,0,0,0)",
        "plot_bg": "rgba(15, 23, 42, 0.45)",
        "plot_grid": "rgba(255, 255, 255, 0.05)",
        "plot_text": "#94a3b8",
        "gauge_bg": "rgba(30, 41, 59, 0.5)",
    }
else:
    T = {
        "app_bg": "linear-gradient(180deg, #f8fafc 0%, #eef2f6 100%)",
        "surface": "#ffffff",
        "surface_card": "#ffffff",
        "surface_metric": "#f8fafc",
        "sidebar_bg": "#ffffff",
        "border": "#e2e8f0",
        "border_hover": "#0284c7",
        "input_bg": "#ffffff",
        "input_border": "#cbd5e1",
        "text_main": "#0f172a",
        "text_sub": "#475569",
        "text_muted": "#94a3b8",
        "accent_cyan": "#0284c7",
        "accent_blue": "#0284c7",
        "accent_emerald": "#059669",
        "accent_amber": "#d97706",
        "accent_rose": "#dc2626",
        "accent_violet": "#7c3aed",
        "plot_paper": "rgba(0,0,0,0)",
        "plot_bg": "#ffffff",
        "plot_grid": "rgba(0, 0, 0, 0.06)",
        "plot_text": "#475569",
        "gauge_bg": "#f1f5f9",
    }

# -----------------------------------------------------------------------------
# CSS Dinâmico 100% Padronizado (Sem vazamento de partes brancas)
# -----------------------------------------------------------------------------
CSS_GLOBAL = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}}

/* Estilização da Aplicação */
.stApp {{
    background: {T["app_bg"]} !important;
    color: {T["text_main"]} !important;
}}

/* Sidebar Padronizada */
section[data-testid="stSidebar"] {{
    background-color: {T["sidebar_bg"]} !important;
    border-right: 1px solid {T["border"]} !important;
}}
section[data-testid="stSidebar"] * {{
    color: {T["text_main"]};
}}

/* Força Cores nos Elementos Streamlit Nativos (Inputs, Selects, Expanders) */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
input, textarea {{
    background-color: {T["input_bg"]} !important;
    color: {T["text_main"]} !important;
    border-color: {T["input_border"]} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    border-radius: 10px !important;
}}

/* Dropdowns e Menus Flutuantes */
div[data-baseweb="popover"],
ul[role="listbox"] {{
    background-color: {T["surface"]} !important;
    color: {T["text_main"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 12px !important;
}}
ul[role="listbox"] li {{
    color: {T["text_main"]} !important;
    background-color: transparent !important;
}}
ul[role="listbox"] li:hover {{
    background-color: {T["border"]} !important;
}}

/* Expander Padronizado */
div[data-testid="stExpander"] {{
    background: {T["surface_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 14px !important;
    box-shadow: none !important;
}}
div[data-testid="stExpander"] summary {{
    color: {T["text_main"]} !important;
    font-weight: 600 !important;
}}

/* Abas (Tabs) Padronizadas */
div[data-testid="stTabs"] button {{
    color: {T["text_sub"]} !important;
    font-weight: 600 !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 18px !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {T["accent_cyan"]} !important;
    border-bottom: 2px solid {T["accent_cyan"]} !important;
}}

/* Top Navbar */
.metalsense-navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: {T["surface"]};
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid {T["border"]};
    border-radius: 18px;
    padding: 16px 26px;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.2);
}}
.brand-group {{
    display: flex;
    align-items: center;
    gap: 14px;
}}
.brand-icon-wrap {{
    background: linear-gradient(135deg, {T["accent_cyan"]} 0%, #38bdf8 100%);
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 16px {T["accent_cyan"]}40;
}}
.brand-title {{
    margin: 0;
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: {T["text_main"]};
}}
.brand-sub {{
    margin: 0;
    font-size: 0.76rem;
    color: {T["text_sub"]};
    font-weight: 600;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}}
.live-pill {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: {T["accent_emerald"]}18;
    border: 1px solid {T["accent_emerald"]}45;
    color: {T["accent_emerald"]};
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.6px;
}}
.live-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: {T["accent_emerald"]};
    box-shadow: 0 0 8px {T["accent_emerald"]};
    animation: pulse-beacon 2s infinite;
}}
@keyframes pulse-beacon {{
    0% {{ transform: scale(0.95); opacity: 0.8; }}
    50% {{ transform: scale(1.15); opacity: 1; }}
    100% {{ transform: scale(0.95); opacity: 0.8; }}
}}

/* Cards de Métricas / KPI */
.kpi-deck-card {{
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 16px;
    padding: 20px 22px;
    transition: all 0.25s ease;
}}
.kpi-deck-card:hover {{
    border-color: {T["border_hover"]};
    transform: translateY(-2px);
}}
.kpi-top-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}}
.kpi-label {{
    font-size: 0.78rem;
    font-weight: 700;
    color: {T["text_sub"]};
    text-transform: uppercase;
    letter-spacing: 0.7px;
}}
.kpi-icon-pill {{
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.kpi-number {{
    font-family: 'Space Grotesk', monospace;
    font-size: 2.3rem;
    font-weight: 700;
    color: {T["text_main"]};
    line-height: 1;
    letter-spacing: -1px;
    font-feature-settings: 'tnum' 1, 'zero' 1;
}}
.kpi-desc {{
    font-size: 0.78rem;
    color: {T["text_muted"]};
    margin-top: 6px;
    font-weight: 500;
}}

/* Badges de Status Fluorescentes */
.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}}
.status-pill-normal {{
    background: {T["accent_emerald"]}18;
    border: 1px solid {T["accent_emerald"]}50;
    color: {T["accent_emerald"]};
}}
.status-pill-anomalia {{
    background: {T["accent_rose"]}18;
    border: 1px solid {T["accent_rose"]}55;
    color: {T["accent_rose"]};
    animation: pulse-danger 1.5s infinite;
}}
@keyframes pulse-danger {{
    0% {{ box-shadow: 0 0 0 0 {T["accent_rose"]}40; }}
    70% {{ box-shadow: 0 0 0 8px transparent; }}
    100% {{ box-shadow: 0 0 0 0 transparent; }}
}}
.status-pill-sem-dados {{
    background: {T["text_muted"]}15;
    border: 1px solid {T["text_muted"]}30;
    color: {T["text_muted"]};
}}

/* Card de Ativo no Parque */
.asset-grid-card {{
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 18px;
    transition: all 0.25s ease;
}}
.asset-grid-card:hover {{
    border-color: {T["border_hover"]};
    transform: translateY(-2px);
}}

/* Painel de Diagnóstico */
.diag-panel {{
    background: {T["surface_card"]};
    border: 1px solid {T["accent_violet"]}45;
    border-radius: 18px;
    padding: 22px 26px;
    margin-bottom: 22px;
}}
.diag-panel-title {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.9rem;
    font-weight: 700;
    color: {T["accent_violet"]};
    text-transform: uppercase;
    letter-spacing: 0.7px;
    margin-bottom: 8px;
}}
.diag-panel-text {{
    font-size: 1.02rem;
    line-height: 1.6;
    color: {T["text_main"]};
}}

/* Sensor Metric Boxes */
.sensor-metric-card {{
    background: {T["surface_metric"]};
    border: 1px solid {T["border"]};
    border-radius: 14px;
    padding: 18px;
    text-align: center;
}}
.sensor-metric-label {{
    font-size: 0.75rem;
    color: {T["text_sub"]};
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.6px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}}
.sensor-metric-val {{
    font-family: 'Space Grotesk', monospace;
    font-size: 1.9rem;
    font-weight: 700;
    margin: 8px 0;
    letter-spacing: -0.5px;
    font-feature-settings: 'tnum' 1, 'zero' 1;
}}

/* Botões Customizados */
div.stButton > button:first-child {{
    border-radius: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
    border: 1px solid {T["border"]};
}}
</style>
"""
st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Componentes de Cabeçalho e Indicadores
# -----------------------------------------------------------------------------
def renderizar_topbar():
    """Barra superior com identidade visual corporativa e sem emojis."""
    agora = datetime.now().strftime("%d/%m/%Y • %H:%M:%S")
    icone_cpu = get_icon("cpu", color="#ffffff", size=22)
    icone_radio = get_icon("radio", color=T["accent_emerald"], size=14)

    st.markdown(
        f"""
        <div class="metalsense-navbar">
            <div class="brand-group">
                <div class="brand-icon-wrap">
                    {icone_cpu}
                </div>
                <div>
                    <h1 class="brand-title">METALSENSE</h1>
                    <p class="brand-sub">Sistema de Diagnóstico Preditivo e Telemetria</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="font-family: 'Space Grotesk', monospace; color: {T['text_sub']}; font-size: 0.85rem; font-weight: 600;">
                    {agora}
                </div>
                <div class="live-pill">
                    <span class="live-dot"></span>
                    <span>{icone_radio} GATEWAY ATIVO</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_kpis_topo(maquinas: list):
    """Renderiza deck de 4 KPIs com tipografia moderna Space Grotesk e SVGs."""
    total_maquinas = len(maquinas)
    total_normais = sum(1 for m in maquinas if m.get("status") == "normal")
    total_anomalias = sum(1 for m in maquinas if m.get("status") == "anomalia")
    total_leituras = sum(len(m.get("historico", [])) for m in maquinas)

    scores = []
    for m in maquinas:
        hist = m.get("historico", [])
        if hist:
            scores.append(calcular_indice_saude(hist)["score"])
    media_saude = round(sum(scores) / len(scores), 1) if scores else 100.0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        ico = get_icon("server", color=T["accent_cyan"], size=18)
        st.markdown(
            f"""
            <div class="kpi-deck-card">
                <div class="kpi-top-row">
                    <span class="kpi-label">Parque Fabril</span>
                    <div class="kpi-icon-pill" style="background: {T['accent_cyan']}18;">{ico}</div>
                </div>
                <div class="kpi-number">{total_maquinas:02d}</div>
                <div class="kpi-desc">Equipamentos em Monitoramento</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        ico = get_icon("shield", color=T["accent_emerald"], size=18)
        cor_score = T["accent_emerald"] if media_saude >= 75 else (T["accent_amber"] if media_saude >= 50 else T["accent_rose"])
        st.markdown(
            f"""
            <div class="kpi-deck-card">
                <div class="kpi-top-row">
                    <span class="kpi-label">Health Score Geral</span>
                    <div class="kpi-icon-pill" style="background: {T['accent_emerald']}18;">{ico}</div>
                </div>
                <div class="kpi-number" style="color: {cor_score};">{media_saude}%</div>
                <div class="kpi-desc">Integridade Média Operacional</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        ico = get_icon("alert", color=T["accent_rose"] if total_anomalias > 0 else T["accent_emerald"], size=18)
        cor_anomalia = T["accent_rose"] if total_anomalias > 0 else T["accent_emerald"]
        desc_anomalia = f"{total_anomalias:02d} Ativo(s) em Atenção" if total_anomalias > 0 else "Nenhum Alerta Crítico"
        st.markdown(
            f"""
            <div class="kpi-deck-card">
                <div class="kpi-top-row">
                    <span class="kpi-label">Alertas de Anomalia</span>
                    <div class="kpi-icon-pill" style="background: {cor_anomalia}18;">{ico}</div>
                </div>
                <div class="kpi-number" style="color: {cor_anomalia};">{total_anomalias:02d}</div>
                <div class="kpi-desc" style="color: {cor_anomalia}; font-weight: 600;">{desc_anomalia}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        ico = get_icon("activity", color=T["accent_violet"], size=18)
        st.markdown(
            f"""
            <div class="kpi-deck-card">
                <div class="kpi-top-row">
                    <span class="kpi-label">Amostras Ingeridas</span>
                    <div class="kpi-icon-pill" style="background: {T['accent_violet']}18;">{ico}</div>
                </div>
                <div class="kpi-number">{total_leituras:,}</div>
                <div class="kpi-desc">Ciclos de Telemetria Processados</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)


def criar_gauge_saude(score: float, classificacao: str) -> go.Figure:
    """Velocímetro/Gauge moderno em Plotly adaptado dinamicamente ao tema Dark/Light."""
    cor_barra = T["accent_emerald"] if score >= 75 else (T["accent_amber"] if score >= 50 else T["accent_rose"])

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={
                'suffix': "%",
                'font': {'size': 44, 'color': T["text_main"], 'family': 'Space Grotesk, monospace'},
            },
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': T["text_muted"], 'nticks': 6},
                'bar': {'color': cor_barra, 'thickness': 0.28},
                'bgcolor': T["gauge_bg"],
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': f"{T['accent_rose']}22"},
                    {'range': [50, 75], 'color': f"{T['accent_amber']}22"},
                    {'range': [75, 100], 'color': f"{T['accent_emerald']}22"},
                ],
                'threshold': {
                    'line': {'color': T["accent_rose"], 'width': 2},
                    'thickness': 0.75,
                    'value': 50,
                },
            },
        )
    )

    fig.update_layout(
        paper_bgcolor=T["plot_paper"],
        plot_bgcolor=T["plot_paper"],
        height=210,
        margin=dict(l=15, r=15, t=15, b=5),
        annotations=[
            dict(
                text=classificacao.upper(),
                x=0.5,
                y=0.15,
                showarrow=False,
                font=dict(size=12, color=cor_barra, family="Plus Jakarta Sans", weight=700),
            )
        ],
    )
    return fig


def criar_grafico_telemetria(
    df: pd.DataFrame, metrica: str, titulo: str, unidade: str, limite: float, cor_linha: str
) -> go.Figure:
    """Gráfico de telemetria Plotly com curvas splines, gradientes e threshold."""
    fig = go.Figure()

    # Linha tracejada do Limite Crítico
    fig.add_hline(
        y=limite,
        line_dash="dash",
        line_color=T["accent_rose"],
        line_width=1.5,
        annotation_text=f"Limite Máximo: {limite} {unidade}",
        annotation_position="top right",
        annotation_font=dict(color=T["accent_rose"], size=10, family="Space Grotesk"),
    )

    # Conversão de cor para preenchimento sombreado
    r = int(cor_linha[1:3], 16)
    g = int(cor_linha[3:5], 16)
    b = int(cor_linha[5:7], 16)
    fill_rgba = f"rgba({r}, {g}, {b}, 0.12)"

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"] if "timestamp" in df.columns else list(range(len(df))),
            y=df[metrica],
            mode="lines+markers",
            name=f"{titulo} ({unidade})",
            line=dict(color=cor_linha, width=3, shape="spline"),
            marker=dict(size=6, color=cor_linha, symbol="circle"),
            fill="tozeroy",
            fillcolor=fill_rgba,
            hovertemplate="<b>%{y:.2f} " + unidade + "</b><br>%{x}<extra></extra>",
        )
    )

    fig.update_layout(
        paper_bgcolor=T["plot_paper"],
        plot_bgcolor=T["plot_bg"],
        hovermode="x unified",
        margin=dict(l=10, r=10, t=30, b=10),
        height=320,
        xaxis=dict(
            showgrid=True,
            gridcolor=T["plot_grid"],
            color=T["plot_text"],
            tickfont=dict(size=10, family="Space Grotesk"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=T["plot_grid"],
            color=T["plot_text"],
            tickfont=dict(size=10, family="Space Grotesk"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=T["text_sub"], size=11),
        ),
    )
    return fig


# -----------------------------------------------------------------------------
# Visão 1: Parque Fabril Consolidado
# -----------------------------------------------------------------------------
def renderizar_visao_parque(dados: dict, maquinas: list):
    """Grid de ativos fabris com visual corporativo."""
    st.markdown("### Ativos Industriais em Monitoramento")
    st.caption("Visão consolidada da integridade física e operacional de todas as máquinas conectadas.")

    if not maquinas:
        st.info("Nenhuma máquina cadastrada no sistema. Utilize o formulário na barra lateral para adicionar um ativo.")
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
                pill_class = "status-pill-normal"
                status_txt = "OPERAÇÃO NORMAL"
            elif status_m == "anomalia":
                pill_class = "status-pill-anomalia"
                status_txt = "ANOMALIA DETECTADA"
            else:
                pill_class = "status-pill-sem-dados"
                status_txt = "AGUARDANDO LEITURA"

            ult_temp = f"{hist[-1]['temperatura']}°C" if hist else "—"
            ult_vib = f"{hist[-1]['vibracao']} mm/s" if hist else "—"
            ult_cons = f"{hist[-1]['consumo']} W" if hist else "—"

            cor_prog = T["accent_emerald"] if score >= 75 else (T["accent_amber"] if score >= 50 else T["accent_rose"])

            st.markdown(
                f"""
                <div class="asset-grid-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <div>
                            <span style="font-size: 0.75rem; font-weight: 700; color: {T['accent_cyan']}; text-transform: uppercase;">ID #{id_m:02d}</span>
                            <h3 style="margin: 2px 0 0 0; font-size: 1.25rem; font-weight: 700; color: {T['text_main']};">{nome_m}</h3>
                        </div>
                        <span class="status-pill {pill_class}">{status_txt}</span>
                    </div>

                    <div style="margin: 14px 0 10px 0;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                            <span style="color: {T['text_sub']}; font-weight: 600;">Health Score</span>
                            <span style="color: {cor_prog}; font-weight: 700; font-family: 'Space Grotesk', monospace;">{score}% ({saude['classificacao']})</span>
                        </div>
                        <div style="background: {T['border']}; height: 6px; border-radius: 9999px; overflow: hidden;">
                            <div style="background: {cor_prog}; width: {score}%; height: 100%; border-radius: 9999px;"></div>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 14px; text-align: center;">
                        <div style="background: {T['surface_metric']}; border: 1px solid {T['border']}; padding: 8px; border-radius: 8px;">
                            <div style="font-size: 0.7rem; color: {T['text_muted']}; text-transform: uppercase; font-weight: 600;">Temperatura</div>
                            <div style="font-size: 0.95rem; font-weight: 700; color: {T['text_main']}; font-family: 'Space Grotesk', monospace;">{ult_temp}</div>
                        </div>
                        <div style="background: {T['surface_metric']}; border: 1px solid {T['border']}; padding: 8px; border-radius: 8px;">
                            <div style="font-size: 0.7rem; color: {T['text_muted']}; text-transform: uppercase; font-weight: 600;">Vibração</div>
                            <div style="font-size: 0.95rem; font-weight: 700; color: {T['text_main']}; font-family: 'Space Grotesk', monospace;">{ult_vib}</div>
                        </div>
                        <div style="background: {T['surface_metric']}; border: 1px solid {T['border']}; padding: 8px; border-radius: 8px;">
                            <div style="font-size: 0.7rem; color: {T['text_muted']}; text-transform: uppercase; font-weight: 600;">Carga</div>
                            <div style="font-size: 0.95rem; font-weight: 700; color: {T['text_main']}; font-family: 'Space Grotesk', monospace;">{ult_cons}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Ações Globais de Telemetria")
    c_btn, c_txt = st.columns([1, 2])
    with c_btn:
        if st.button("Disparar Ciclo Geral de Coleta", use_container_width=True):
            for m in maquinas:
                registrar_leitura(dados, m["id"], gerar_anomalia=False)
            st.toast("Ciclo de medição concluído para todo o parque!", icon="✅")
            st.rerun()
    with c_txt:
        st.caption("Executa um ciclo síncrono de medição e análise para todos os ativos cadastrados no banco.")


# -----------------------------------------------------------------------------
# Visão 2: Detalhes Aprofundados da Máquina Selecionada
# -----------------------------------------------------------------------------
def renderizar_detalhes_maquina(dados: dict, maquina: dict):
    """Visualização analítica completa de uma máquina específica."""
    id_m = maquina["id"]
    nome_m = maquina["nome"]
    historico = maquina.get("historico", [])
    status_m = maquina.get("status", "sem dados").lower()

    diagnostico_texto = analisar_maquina(dados, id_m)
    saude = calcular_indice_saude(historico)
    score = saude["score"]

    if status_m == "normal":
        pill_class = "status-pill-normal"
        status_txt = "OPERAÇÃO NORMAL"
    elif status_m == "anomalia":
        pill_class = "status-pill-anomalia"
        status_txt = "ANOMALIA DETECTADA"
    else:
        pill_class = "status-pill-sem-dados"
        status_txt = "AGUARDANDO LEITURA"

    # Header da Máquina
    c_h1, c_h2 = st.columns([3, 1])
    with c_h1:
        st.markdown(
            f"""
            <div style="margin-bottom: 8px;">
                <span style="font-size: 0.78rem; font-weight: 700; color: {T['accent_cyan']}; text-transform: uppercase;">MONITORAMENTO INDIVIDUAL DE ATIVO</span>
                <h1 style="margin: 2px 0 0 0; font-size: 2.1rem; font-weight: 800; color: {T['text_main']};">{nome_m} <span style="font-size: 1.2rem; color: {T['text_muted']}; font-family: 'Space Grotesk', monospace;">[ID #{id_m:02d}]</span></h1>
                <p style="margin: 4px 0 0 0; color: {T['text_sub']}; font-size: 0.88rem;">Série temporal contínua • Volume acumulado: <strong>{len(historico)} registros</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_h2:
        st.markdown(
            f"""
            <div style="text-align: right; margin-top: 18px;">
                <span class="status-pill {pill_class}">{status_txt}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # HERO: Velocímetro (Gauge) + Diagnóstico AI Preditivo
    col_gauge, col_ai = st.columns([1, 2])

    with col_gauge:
        st.markdown(
            f"""
            <div style="background: {T['surface_card']}; border: 1px solid {T['border']}; border-radius: 18px; padding: 12px; text-align: center;">
                <div style="font-size: 0.78rem; font-weight: 700; color: {T['text_sub']}; text-transform: uppercase; letter-spacing: 0.7px; margin-top: 6px;">Integridade do Ativo</div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(criar_gauge_saude(score, saude["classificacao"]), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_ai:
        ico_brain = get_icon("brain", color=T["accent_violet"], size=20)
        st.markdown(
            f"""
            <div class="diag-panel">
                <div class="diag-panel-title">
                    <span>{ico_brain}</span>
                    <span>Diagnóstico Preditivo MetalSense • Análise de Campo</span>
                </div>
                <div class="diag-panel-text">{diagnostico_texto}</div>
            """,
            unsafe_allow_html=True,
        )

        # Hipóteses Fisiomecânicas
        if saude.get("hipoteses"):
            st.markdown("<div style='margin-top: 12px;'>", unsafe_allow_html=True)
            for hip in saude["hipoteses"]:
                st.markdown(
                    f"""
                    <span style="display: inline-flex; align-items: center; gap: 6px; background: {T['accent_rose']}18; border: 1px solid {T['accent_rose']}40; color: {T['accent_rose']}; padding: 4px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 600; margin-right: 6px; margin-top: 6px;">
                        {get_icon('alert', color=T['accent_rose'], size=14)} {hip}
                    </span>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Tendências Discretas
        tend = saude.get("tendencias", {})
        st.markdown(
            f"""
            <div style="display: flex; gap: 20px; margin-top: 16px; font-size: 0.85rem; color: {T['text_sub']}; border-top: 1px solid {T['border']}; padding-top: 12px;">
                <div>Temperatura: <strong style="color: {T['text_main']};">{tend.get('temperatura', 'Estável')}</strong></div>
                <div>Vibração: <strong style="color: {T['text_main']};">{tend.get('vibracao', 'Estável')}</strong></div>
                <div>Carga: <strong style="color: {T['text_main']};">{tend.get('consumo', 'Estável')}</strong></div>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ÚLTIMA MEDIÇÃO EM CARDS
    if historico:
        ult = historico[-1]
        t_val = ult.get("temperatura", 0.0)
        v_val = ult.get("vibracao", 0.0)
        c_val = ult.get("consumo", 0.0)
        hora = ult.get("timestamp", "—")

        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            t_cor = T["accent_rose"] if t_val > 85.0 else T["accent_emerald"]
            t_txt = "Crítico (>85°C)" if t_val > 85.0 else "Normal (55-68°C)"
            ico_temp = get_icon("thermometer", color=t_cor, size=16)
            st.markdown(
                f"""
                <div class="sensor-metric-card">
                    <div class="sensor-metric-label">{ico_temp} Temperatura</div>
                    <div class="sensor-metric-val" style="color: {t_cor};">{t_val} <span style="font-size: 1.1rem;">°C</span></div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: {t_cor};">{t_txt}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sc2:
            v_cor = T["accent_rose"] if v_val > 8.0 else T["accent_emerald"]
            v_txt = "Crítica (>8.0 mm/s)" if v_val > 8.0 else "Normal (2-4.5 mm/s)"
            ico_vib = get_icon("waves", color=v_cor, size=16)
            st.markdown(
                f"""
                <div class="sensor-metric-card">
                    <div class="sensor-metric-label">{ico_vib} Vibração Mecânica</div>
                    <div class="sensor-metric-val" style="color: {v_cor};">{v_val} <span style="font-size: 1.1rem;">mm/s</span></div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: {v_cor};">{v_txt}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sc3:
            c_cor = T["accent_rose"] if c_val > 500.0 else T["accent_emerald"]
            c_txt = "Sobrecarga (>500W)" if c_val > 500.0 else "Normal (250-380W)"
            ico_zap = get_icon("zap", color=c_cor, size=16)
            st.markdown(
                f"""
                <div class="sensor-metric-card">
                    <div class="sensor-metric-label">{ico_zap} Carga Elétrica</div>
                    <div class="sensor-metric-val" style="color: {c_cor};">{c_val} <span style="font-size: 1.1rem;">W</span></div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: {c_cor};">{c_txt}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sc4:
            ico_act = get_icon("activity", color=T["accent_cyan"], size=16)
            st.markdown(
                f"""
                <div class="sensor-metric-card">
                    <div class="sensor-metric-label">{ico_act} Último Registro</div>
                    <div class="sensor-metric-val" style="color: {T['accent_cyan']}; font-size: 1.4rem; margin-top: 14px;">{hora.split(' ')[-1] if ' ' in hora else hora}</div>
                    <span style="font-size: 0.72rem; font-weight: 600; color: {T['text_muted']};">{hora.split(' ')[0] if ' ' in hora else 'Hoje'}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # PAINEL DE CONTROLE E SIMULAÇÃO
    st.markdown("#### Console Operacional de Telemetria")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Amostragem Operacional Normal", use_container_width=True):
            registrar_leitura(dados, id_m, gerar_anomalia=False)
            st.toast("Amostragem normal registrada com sucesso!", icon="✅")
            st.rerun()
    with b2:
        if st.button("Injetar Disparo Anômalo", type="primary", use_container_width=True):
            registrar_leitura(dados, id_m, gerar_anomalia=True)
            st.toast("Disparo anômalo simulado!", icon="🚨")
            st.rerun()
    with b3:
        if st.button("Recalcular Matriz Preditiva", use_container_width=True):
            analisar_maquina(dados, id_m)
            st.toast("Inferência preditiva atualizada!", icon="🔄")
            st.rerun()

    with st.expander("Estúdio de Injeção de Falhas Físicas", expanded=False):
        st.caption("Cenários físicos parametrizados para testes de diagnóstico e validação técnica:")
        sb1, sb2, sb3 = st.columns(3)
        with sb1:
            if st.button("Cenário: Desgaste de Rolamento", use_container_width=True):
                leit = gerar_leitura_cenario("rolamento", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Cenário de Desgaste de Rolamento injetado!", icon="⚙️")
                st.rerun()
        with sb2:
            if st.button("Cenário: Falha de Arrefecimento", use_container_width=True):
                leit = gerar_leitura_cenario("aquecimento", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Cenário de Superaquecimento injetado!", icon="🔥")
                st.rerun()
        with sb3:
            if st.button("Cenário: Sobrecarga de Motor", use_container_width=True):
                leit = gerar_leitura_cenario("sobrecarga", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Cenário de Sobrecarga injetado!", icon="⚡")
                st.rerun()

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # GRÁFICOS INTERATIVOS
    st.markdown("#### Monitoramento Temporal das Grandezas")

    if len(historico) < 2:
        st.info("Série temporal com dados insuficientes (mínimo de 2 leituras). Utilize o console acima para registrar medições.")
    else:
        df_hist = pd.DataFrame(historico)

        tab1, tab2, tab3, tab4 = st.tabs([
            "Temperatura (°C)",
            "Vibração (mm/s)",
            "Consumo Elétrico (W)",
            "Espectro Multivariado",
        ])

        with tab1:
            st.plotly_chart(
                criar_grafico_telemetria(
                    df_hist, "temperatura", "Temperatura", "°C", 85.0, T["accent_cyan"]
                ),
                use_container_width=True,
            )
        with tab2:
            st.plotly_chart(
                criar_grafico_telemetria(
                    df_hist, "vibracao", "Vibração Mecânica", "mm/s", 8.0, T["accent_amber"]
                ),
                use_container_width=True,
            )
        with tab3:
            st.plotly_chart(
                criar_grafico_telemetria(
                    df_hist, "consumo", "Carga Elétrica", "W", 500.0, T["accent_violet"]
                ),
                use_container_width=True,
            )
        with tab4:
            fig_multi = go.Figure()
            for col, cor, nome in [
                ("temperatura", T["accent_cyan"], "Temp (°C)"),
                ("vibracao", T["accent_amber"], "Vibração (mm/s)"),
                ("consumo", T["accent_violet"], "Carga (W)"),
            ]:
                fig_multi.add_trace(
                    go.Scatter(
                        x=df_hist["timestamp"],
                        y=df_hist[col],
                        mode="lines",
                        name=nome,
                        line=dict(color=cor, width=2.5),
                    )
                )
            fig_multi.update_layout(
                paper_bgcolor=T["plot_paper"],
                plot_bgcolor=T["plot_bg"],
                hovermode="x unified",
                margin=dict(l=10, r=10, t=30, b=10),
                height=340,
                xaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"]),
                yaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"]),
                legend=dict(font=dict(color=T["text_sub"])),
            )
            st.plotly_chart(fig_multi, use_container_width=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # AUDITORIA & EXPORTAÇÃO
    st.markdown("#### Histórico de Telemetria e Emissão de Laudos")
    if historico:
        with st.expander("Visualizar Tabela de Registros e Emitir Documentação Técnica", expanded=False):
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
                    label="Baixar Telemetria Completa (CSV)",
                    data=csv_buf.getvalue(),
                    file_name=f"telemetria_metalsense_asset_{id_m}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with t_col2:
                caminho_html = gerar_relatorio_html(maquina)
                with open(caminho_html, "r", encoding="utf-8") as f_html:
                    html_data = f_html.read()
                st.download_button(
                    label="Baixar Laudo Técnico de Perícia (HTML)",
                    data=html_data,
                    file_name=f"laudo_metalsense_asset_{id_m}.html",
                    mime="text/html",
                    use_container_width=True,
                )

            st.markdown("##### Ordem de Serviço de Engenharia Preditiva")
            st.code(gerar_ordem_servico_texto(maquina), language="text")


# -----------------------------------------------------------------------------
# Fluxo Principal & Barra Lateral
# -----------------------------------------------------------------------------
def main():
    dados = carregar_dados()
    maquinas = dados.get("maquinas", [])

    # Top Navbar Corporativa
    renderizar_topbar()

    # Deck de KPIs
    renderizar_kpis_topo(maquinas)

    # SIDEBAR
    with st.sidebar:
        st.markdown(
            f"""
            <div style="font-size: 0.72rem; color: {T['text_muted']}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.7px; margin-top: 14px; margin-bottom: 6px;">
                NAVEGAÇÃO DE ATIVOS
            </div>
            """,
            unsafe_allow_html=True,
        )

        opcoes = ["Visão Geral de Todo o Parque"]
        mapa = {}
        for m in maquinas:
            tag = f"[#{m['id']:02d}] {m['nome']}"
            opcoes.append(tag)
            mapa[tag] = m

        escolha = st.selectbox(
            "Selecione o Ativo:",
            options=opcoes,
            index=0,
            help="Alterne entre o panorama consolidado do parque e a telemetria detalhada de uma máquina.",
        )

        st.markdown("---")

        # Cadastro de Novo Ativo
        st.markdown(
            f"""
            <div style="font-size: 0.72rem; color: {T['text_muted']}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.7px; margin-bottom: 6px;">
                CADASTRAR NOVO EQUIPAMENTO
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("form_novo_ativo", clear_on_submit=True):
            nome_input = st.text_input("Identificador do Ativo:", placeholder="Ex: Fresadora CNC Haas 02")
            btn_add = st.form_submit_button("Cadastrar Ativo", use_container_width=True)

            if btn_add:
                nome_limpo = nome_input.strip()
                if not nome_limpo:
                    st.error("O identificador não pode ser vazio.")
                else:
                    try:
                        nova = criar_maquina(dados, nome_limpo)
                        st.toast(f"Máquina '{nova['nome']}' cadastrada com sucesso!", icon="✅")
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

        # Descomissionamento
        maquina_ativa = mapa.get(escolha)
        if maquina_ativa:
            st.markdown("---")
            st.markdown(
                f"""
                <div style="font-size: 0.72rem; color: {T['text_muted']}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.7px; margin-bottom: 6px;">
                    DESCOMISSIONAMENTO
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("Remover Ativo Selecionado", expanded=False):
                st.caption(f"Atenção: A remoção de '{maquina_ativa['nome']}' apagará todo o histórico de telemetria.")
                confirm = st.checkbox("Confirmo o descomissionamento", key=f"del_{maquina_ativa['id']}")
                if st.button("Remover Definitivamente", type="primary", disabled=not confirm, use_container_width=True):
                    if remover_maquina(dados, maquina_ativa["id"]):
                        st.toast("Ativo descomissionado com sucesso!", icon="🗑️")
                        st.rerun()

        st.markdown("---")
        st.caption("MetalSense Pro v2.4 • TechForge Industrial")

    # Renderização da Área Principal
    if escolha == "Visão Geral de Todo o Parque" or not maquina_ativa:
        renderizar_visao_parque(dados, maquinas)
    else:
        renderizar_detalhes_maquina(dados, maquina_ativa)


if __name__ == "__main__":
    main()
