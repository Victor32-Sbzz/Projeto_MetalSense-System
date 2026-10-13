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
# Gerenciador de Estado de Navegação e Tema
# -----------------------------------------------------------------------------
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"

if "maquina_ativa_id" not in st.session_state:
    st.session_state["maquina_ativa_id"] = None

# Alternador de Tema na Barra Lateral
with st.sidebar:
    st.markdown("<p style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;'>Aparência do Sistema</p>", unsafe_allow_html=True)
    c_t1, c_t2 = st.columns(2)
    with c_t1:
        if st.button("Escuro", use_container_width=True, type="primary" if st.session_state["theme_mode"] == "dark" else "secondary"):
            st.session_state["theme_mode"] = "dark"
            st.rerun()
    with c_t2:
        if st.button("Claro", use_container_width=True, type="primary" if st.session_state["theme_mode"] == "light" else "secondary"):
            st.session_state["theme_mode"] = "light"
            st.rerun()

IS_DARK = st.session_state["theme_mode"] == "dark"

# Paleta de Cores 100% Padronizada para Ambos os Modos
if IS_DARK:
    T = {
        "app_bg": "radial-gradient(circle at 10% 20%, #0d1527 0%, #060911 85%)",
        "surface": "rgba(15, 23, 42, 0.75)",
        "surface_card": "#0f172a",
        "surface_metric": "rgba(30, 41, 59, 0.5)",
        "sidebar_bg": "#080c14",
        "border": "rgba(255, 255, 255, 0.08)",
        "border_subtle": "rgba(255, 255, 255, 0.05)",
        "border_hover": "#38bdf8",
        "input_bg": "#0f172a",
        "input_border": "rgba(255, 255, 255, 0.15)",
        "text_main": "#f8fafc",
        "text_sub": "#94a3b8",
        "text_muted": "#64748b",
        "btn_bg": "rgba(15, 23, 42, 0.8)",
        "btn_border": "rgba(255, 255, 255, 0.12)",
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
        "app_bg": "#f8fafc",
        "surface": "#ffffff",
        "surface_card": "#ffffff",
        "surface_metric": "#f1f5f9",
        "sidebar_bg": "#ffffff",
        "border": "#e2e8f0",
        "border_subtle": "#e2e8f0",
        "border_hover": "#0284c7",
        "input_bg": "#ffffff",
        "input_border": "#cbd5e1",
        "text_main": "#0f172a",
        "text_sub": "#475569",
        "text_muted": "#64748b",
        "btn_bg": "#ffffff",
        "btn_border": "#cbd5e1",
        "accent_cyan": "#0284c7",
        "accent_blue": "#0284c7",
        "accent_emerald": "#059669",
        "accent_amber": "#d97706",
        "accent_rose": "#dc2626",
        "accent_violet": "#7c3aed",
        "plot_paper": "rgba(0,0,0,0)",
        "plot_bg": "#ffffff",
        "plot_grid": "#e2e8f0",
        "plot_text": "#475569",
        "gauge_bg": "#e2e8f0",
    }

# -----------------------------------------------------------------------------
# Biblioteca de Ícones SVG Profissionais (Vetorizados, Limpos e Sem Emojis)
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
    "arrow-right": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>',
}


def get_icon(name: str, color: str = "currentColor", size: int = 18) -> str:
    """Retorna código SVG inline formatado com tamanho e cor."""
    template = ICONS.get(name, "")
    return template.format(s=size, c=color)


# -----------------------------------------------------------------------------
# CSS Global Dinâmico (Modo Escuro e Modo Claro 100% Blindados e Homogêneos)
# -----------------------------------------------------------------------------
CSS_GLOBAL = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}}

/* Cor de Fundo Geral */
.stApp {{
    background: {T["app_bg"]} !important;
    color: {T["text_main"]} !important;
}}

header[data-testid="stHeader"] {{
    background-color: transparent !important;
}}

/* Barra Lateral (Sidebar) */
section[data-testid="stSidebar"] {{
    background-color: {T["sidebar_bg"]} !important;
    border-right: 1px solid {T["border"]} !important;
}}
section[data-testid="stSidebar"] * {{
    color: {T["text_main"]} !important;
}}

/* Forçar Campos de Entrada e Selects */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
input, textarea {{
    background-color: {T["input_bg"]} !important;
    color: {T["text_main"]} !important;
    border-color: {T["input_border"]} !important;
    border-radius: 10px !important;
}}

/* Menus de Dropdown / Popover */
div[data-baseweb="popover"],
ul[role="listbox"] {{
    background-color: {T["surface"]} !important;
    color: {T["text_main"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 12px !important;
}}
ul[role="listbox"] li {{
    color: {T["text_main"]} !important;
}}
ul[role="listbox"] li:hover {{
    background-color: {T["border"]} !important;
}}

/* Expander */
div[data-testid="stExpander"] {{
    background: {T["surface_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 14px !important;
}}
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] p {{
    color: {T["text_main"]} !important;
}}

/* Formulários */
div[data-testid="stForm"] {{
    background: {T["surface_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 14px !important;
}}

/* Botões */
div.stButton > button {{
    background-color: {T["btn_bg"]} !important;
    color: {T["text_main"]} !important;
    border: 1px solid {T["btn_border"]} !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}}
div.stButton > button:hover {{
    border-color: {T["border_hover"]} !important;
    transform: translateY(-1px) !important;
}}
div.stButton > button[kind="primary"] {{
    background: {T["accent_rose"]} !important;
    color: #ffffff !important;
    border: none !important;
}}

/* Abas */
div[data-testid="stTabs"] button {{
    color: {T["text_sub"]} !important;
    font-weight: 600 !important;
    border-bottom: 2px solid transparent !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {T["accent_cyan"]} !important;
    border-bottom: 2px solid {T["accent_cyan"]} !important;
}}

/* Top Navbar */
.top-navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: {T["surface"]};
    border: 1px solid {T["border"]};
    border-radius: 16px;
    padding: 16px 24px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px -4px rgba(0, 0, 0, 0.08);
}}
.brand-title {{
    font-size: 1.3rem;
    font-weight: 800;
    color: {T["text_main"]};
    margin: 0;
}}
.brand-sub {{
    font-size: 0.78rem;
    font-weight: 600;
    color: {T["text_sub"]};
    margin: 0;
    text-transform: uppercase;
}}

/* Card de KPI Superior */
.kpi-card {{
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 16px;
    padding: 18px 20px;
    transition: all 0.2s ease;
}}
.kpi-card:hover {{
    border-color: {T["border_hover"]};
}}
.kpi-title {{
    font-size: 0.76rem;
    font-weight: 700;
    color: {T["text_sub"]};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.kpi-number {{
    font-family: 'Space Grotesk', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: {T["text_main"]};
    margin: 6px 0 2px 0;
    line-height: 1;
    font-feature-settings: 'tnum' 1, 'zero' 1;
}}
.kpi-desc {{
    font-size: 0.75rem;
    color: {T["text_muted"]};
}}

/* Card de Máquina na Página Inicial */
.machine-home-card {{
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    transition: all 0.2s ease;
}}
.machine-home-card:hover {{
    border-color: {T["border_hover"]};
    box-shadow: 0 8px 24px -8px rgba(0, 0, 0, 0.12);
}}

/* Badges de Status */
.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}
.status-pill-normal {{
    background: {T["accent_emerald"]}18;
    border: 1px solid {T["accent_emerald"]}45;
    color: {T["accent_emerald"]};
}}
.status-pill-anomalia {{
    background: {T["accent_rose"]}18;
    border: 1px solid {T["accent_rose"]}50;
    color: {T["accent_rose"]};
}}
.status-pill-sem-dados {{
    background: {T["text_muted"]}18;
    border: 1px solid {T["text_muted"]}35;
    color: {T["text_muted"]};
}}

/* Painel de Diagnóstico */
.diag-card {{
    background: {T["surface_card"]};
    border: 1px solid {T["accent_violet"]}40;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 20px;
}}

/* Mini Box de Sensores */
.sensor-box {{
    background: {T["surface_metric"]};
    border: 1px solid {T["border"]};
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}}
.sensor-val {{
    font-family: 'Space Grotesk', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 6px 0;
    font-feature-settings: 'tnum' 1, 'zero' 1;
}}
</style>
"""
st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Componentes Visuais
# -----------------------------------------------------------------------------
def renderizar_topbar():
    """Barra superior limpa e moderna."""
    agora = datetime.now().strftime("%d/%m/%Y • %H:%M")
    ico_cpu = get_icon("cpu", color=T["accent_cyan"], size=20)

    html = f"""
    <div class="top-navbar">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: {T['accent_cyan']}18; padding: 10px; border-radius: 12px; display: flex;">
                {ico_cpu}
            </div>
            <div>
                <h1 class="brand-title">MetalSense</h1>
                <p class="brand-sub">Sistema de Monitoramento e Manutenção Preditiva</p>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="color: {T['text_sub']}; font-size: 0.82rem; font-family: 'Space Grotesk', monospace; font-weight: 600;">
                {agora}
            </div>
            <span class="status-pill status-pill-normal">
                {get_icon('check', color=T['accent_emerald'], size=12)} Sistema Online
            </span>
        </div>
    </div>
    """
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


def renderizar_kpis_topo(maquinas: list):
    """Métricas superiores com nomes simples e diretos."""
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
        html = f"""
        <div class="kpi-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="kpi-title">Máquinas no Sistema</span>
                <span style="background: {T['accent_cyan']}18; padding: 6px; border-radius: 8px;">{ico}</span>
            </div>
            <div class="kpi-number">{total_maquinas:02d}</div>
            <div class="kpi-desc">Equipamentos cadastrados</div>
        </div>
        """
        st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

    with c2:
        ico = get_icon("shield", color=T["accent_emerald"], size=18)
        cor_score = T["accent_emerald"] if media_saude >= 75 else (T["accent_amber"] if media_saude >= 50 else T["accent_rose"])
        html = f"""
        <div class="kpi-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="kpi-title">Saúde das Máquinas</span>
                <span style="background: {T['accent_emerald']}18; padding: 6px; border-radius: 8px;">{ico}</span>
            </div>
            <div class="kpi-number" style="color: {cor_score};">{media_saude}%</div>
            <div class="kpi-desc">Média de bom funcionamento</div>
        </div>
        """
        st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

    with c3:
        ico = get_icon("alert", color=T["accent_rose"] if total_anomalias > 0 else T["accent_emerald"], size=18)
        cor_alerta = T["accent_rose"] if total_anomalias > 0 else T["accent_emerald"]
        txt_alerta = f"{total_anomalias} precisam de atenção" if total_anomalias > 0 else "Nenhum problema detectado"
        html = f"""
        <div class="kpi-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="kpi-title">Alertas de Falha</span>
                <span style="background: {cor_alerta}18; padding: 6px; border-radius: 8px;">{ico}</span>
            </div>
            <div class="kpi-number" style="color: {cor_alerta};">{total_anomalias:02d}</div>
            <div class="kpi-desc" style="color: {cor_alerta}; font-weight: 600;">{txt_alerta}</div>
        </div>
        """
        st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

    with c4:
        ico = get_icon("activity", color=T["accent_violet"], size=18)
        html = f"""
        <div class="kpi-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="kpi-title">Medições Feitas</span>
                <span style="background: {T['accent_violet']}18; padding: 6px; border-radius: 8px;">{ico}</span>
            </div>
            <div class="kpi-number">{total_leituras:,}</div>
            <div class="kpi-desc">Total de leituras registradas</div>
        </div>
        """
        st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)


def criar_gauge_saude(score: float) -> go.Figure:
    """Velocímetro limpo sem textos sobrepostos na agulha."""
    cor_barra = T["accent_emerald"] if score >= 75 else (T["accent_amber"] if score >= 50 else T["accent_rose"])

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
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': T["text_muted"], 'nticks': 5},
                'bar': {'color': cor_barra, 'thickness': 0.28},
                'bgcolor': T["gauge_bg"],
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': f"{T['accent_rose']}20"},
                    {'range': [50, 75], 'color': f"{T['accent_amber']}20"},
                    {'range': [75, 100], 'color': f"{T['accent_emerald']}20"},
                ],
            },
        )
    )

    fig.update_layout(
        paper_bgcolor=T["plot_paper"],
        plot_bgcolor=T["plot_paper"],
        height=180,
        margin=dict(l=15, r=15, t=10, b=10),
    )
    return fig


def criar_grafico_telemetria(
    df: pd.DataFrame, metrica: str, titulo: str, unidade: str, limite: float, cor_linha: str
) -> go.Figure:
    """Gráfico interativo com curva suave e linha de limite de segurança."""
    fig = go.Figure()

    fig.add_hline(
        y=limite,
        line_dash="dash",
        line_color=T["accent_rose"],
        line_width=1.5,
        annotation_text=f"Limite de Segurança ({limite} {unidade})",
        annotation_position="top right",
        annotation_font=dict(color=T["accent_rose"], size=10, family="Space Grotesk"),
    )

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
        height=300,
        xaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"], tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"], tickfont=dict(size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=T["text_sub"], size=11)),
    )
    return fig


# -----------------------------------------------------------------------------
# Página 1: Início (Limpa, Sem Linhas de Código, Muito Intuitiva)
# -----------------------------------------------------------------------------
def renderizar_pagina_inicio(dados: dict, maquinas: list):
    """Página inicial simples, acolhedora e interativa."""
    # Guia Rápido Intuitivo
    info_html = f"""
    <div style="background: {T['surface_card']}; border: 1px solid {T['border']}; border-radius: 16px; padding: 20px 24px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            {get_icon('info', color=T['accent_cyan'], size=18)}
            <strong style="font-size: 0.95rem; color: {T['text_main']};">Como o MetalSense ajuda você?</strong>
        </div>
        <p style="margin: 0; font-size: 0.88rem; color: {T['text_sub']}; line-height: 1.5;">
            O sistema analisa os sensores das máquinas para descobrir problemas <strong>antes que elas quebrem</strong>. 
            Se a temperatura, vibração ou consumo elétrico saírem do padrão da máquina, um alerta é emitido imediatamente.
        </p>
    </div>
    """
    st.markdown(textwrap.dedent(info_html), unsafe_allow_html=True)

    st.markdown("### Suas Máquinas Cadastradas")
    st.caption("Clique em qualquer máquina abaixo para ver os gráficos e detalhes completos.")

    if not maquinas:
        st.info("Você ainda não tem nenhuma máquina cadastrada. Digite o nome de uma máquina na barra lateral esquerda para começar!")
        return

    # Grid Limpo com Botão Direto em Cada Máquina
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
                status_txt = "Normal"
            elif status_m == "anomalia":
                pill_class = "status-pill-anomalia"
                status_txt = "Atenção (Possível Falha)"
            else:
                pill_class = "status-pill-sem-dados"
                status_txt = "Aguardando Leituras"

            ult_temp = f"{hist[-1]['temperatura']}°C" if hist else "—"
            ult_vib = f"{hist[-1]['vibracao']} mm/s" if hist else "—"
            ult_cons = f"{hist[-1]['consumo']} W" if hist else "—"

            cor_prog = T["accent_emerald"] if score >= 75 else (T["accent_amber"] if score >= 50 else T["accent_rose"])

            card_html = f"""
            <div class="machine-home-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                    <div>
                        <span style="font-size: 0.75rem; font-weight: 700; color: {T['accent_cyan']};">MÁQUINA #{id_m:02d}</span>
                        <h3 style="margin: 2px 0 0 0; font-size: 1.25rem; font-weight: 700; color: {T['text_main']};">{nome_m}</h3>
                    </div>
                    <span class="status-pill {pill_class}">{status_txt}</span>
                </div>

                <div style="margin: 14px 0 10px 0;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                        <span style="color: {T['text_sub']};">Saúde da Máquina</span>
                        <span style="color: {cor_prog}; font-weight: 700; font-family: 'Space Grotesk', monospace;">{score}% ({saude['classificacao']})</span>
                    </div>
                    <div style="background: {T['border']}; height: 6px; border-radius: 9999px; overflow: hidden;">
                        <div style="background: {cor_prog}; width: {score}%; height: 100%; border-radius: 9999px;"></div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 14px; text-align: center;">
                    <div style="background: {T['surface_metric']}; border: 1px solid {T['border']}; padding: 8px; border-radius: 8px;">
                        <div style="font-size: 0.7rem; color: {T['text_muted']}; text-transform: uppercase;">Temperatura</div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: {T['text_main']}; font-family: 'Space Grotesk', monospace;">{ult_temp}</div>
                    </div>
                    <div style="background: {T['surface_metric']}; border: 1px solid {T['border']}; padding: 8px; border-radius: 8px;">
                        <div style="font-size: 0.7rem; color: {T['text_muted']}; text-transform: uppercase;">Vibração</div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: {T['text_main']}; font-family: 'Space Grotesk', monospace;">{ult_vib}</div>
                    </div>
                    <div style="background: {T['surface_metric']}; border: 1px solid {T['border']}; padding: 8px; border-radius: 8px;">
                        <div style="font-size: 0.7rem; color: {T['text_muted']}; text-transform: uppercase;">Consumo</div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: {T['text_main']}; font-family: 'Space Grotesk', monospace;">{ult_cons}</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(textwrap.dedent(card_html), unsafe_allow_html=True)

            # Botão Direto para Abrir a Máquina
            if st.button(f"Inspecionar {nome_m} ➔", key=f"btn_ver_{id_m}", use_container_width=True):
                st.session_state["maquina_ativa_id"] = id_m
                st.rerun()

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    if st.button("Coletar uma Leitura Normal para Todas as Máquinas", use_container_width=True):
        for m in maquinas:
            registrar_leitura(dados, m["id"], gerar_anomalia=False)
        st.toast("Leituras registradas para todas as máquinas!", icon="✅")
        st.rerun()


# -----------------------------------------------------------------------------
# Página 2: Detalhes da Máquina (Interativa, Simples e Amigável)
# -----------------------------------------------------------------------------
def renderizar_detalhes_maquina(dados: dict, maquina: dict):
    """Tela detalhada de uma máquina com navegação fácil."""
    id_m = maquina["id"]
    nome_m = maquina["nome"]
    historico = maquina.get("historico", [])
    status_m = maquina.get("status", "sem dados").lower()

    diagnostico_texto = analisar_maquina(dados, id_m)
    saude = calcular_indice_saude(historico)
    score = saude["score"]

    # Botão para voltar à página inicial
    if st.button("⬅ Voltar para Todas as Máquinas", use_container_width=False):
        st.session_state["maquina_ativa_id"] = None
        st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    if status_m == "normal":
        pill_class = "status-pill-normal"
        status_txt = "Operação Normal"
    elif status_m == "anomalia":
        pill_class = "status-pill-anomalia"
        status_txt = "Atenção (Falha Detectada)"
    else:
        pill_class = "status-pill-sem-dados"
        status_txt = "Aguardando Leituras"

    # Header da Máquina
    c_h1, c_h2 = st.columns([3, 1])
    with c_h1:
        st.markdown(
            f"""
            <div>
                <span style="font-size: 0.78rem; font-weight: 700; color: {T['accent_cyan']};">MONITORANDO ATIVO #{id_m:02d}</span>
                <h1 style="margin: 2px 0 0 0; font-size: 2.1rem; font-weight: 800; color: {T['text_main']};">{nome_m}</h1>
                <p style="margin: 4px 0 0 0; color: {T['text_sub']}; font-size: 0.88rem;">Total de medições salvas: <strong>{len(historico)} registros</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_h2:
        st.markdown(
            f"""
            <div style="text-align: right; margin-top: 14px;">
                <span class="status-pill {pill_class}">{status_txt}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Velocímetro (Gauge) + Diagnóstico Simples
    col_gauge, col_ai = st.columns([1, 2])

    with col_gauge:
        st.markdown(
            f"""
            <div style="background: {T['surface_card']}; border: 1px solid {T['border']}; border-radius: 16px; padding: 14px; text-align: center;">
                <span style="font-size: 0.75rem; font-weight: 700; color: {T['text_sub']}; text-transform: uppercase;">Saúde do Ativo</span>
            """,
            unsafe_allow_html=True,
        )
        # Velocímetro Limpo
        st.plotly_chart(criar_gauge_saude(score), use_container_width=True)

        # Mensagem de estado colocada ABAIXO do velocímetro (Sem sobreposição!)
        st.markdown(
            f"""
                <div style="margin-top: -15px; margin-bottom: 6px;">
                    <span class="status-pill {pill_class}">{saude['classificacao'].upper()}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_ai:
        diag_html = f"""
        <div class="diag-card">
            <div style="font-size: 0.85rem; font-weight: 700; color: {T['accent_violet']}; text-transform: uppercase; margin-bottom: 8px;">
                Diagnóstico Automático
            </div>
            <div style="font-size: 1.05rem; line-height: 1.5; color: {T['text_main']};">
                {diagnostico_texto}
            </div>
        """
        st.markdown(textwrap.dedent(diag_html), unsafe_allow_html=True)

        # Hipóteses em formato simples
        if saude.get("hipoteses"):
            st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
            for hip in saude["hipoteses"]:
                hip_html = f"""
                <span style="display: inline-flex; align-items: center; gap: 6px; background: {T['accent_rose']}18; border: 1px solid {T['accent_rose']}40; color: {T['accent_rose']}; padding: 4px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 600; margin-right: 6px; margin-top: 6px;">
                    {get_icon('alert', color=T['accent_rose'], size=14)} {hip}
                </span>
                """
                st.markdown(textwrap.dedent(hip_html), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        tend = saude.get("tendencias", {})
        tend_html = f"""
            <div style="display: flex; gap: 20px; margin-top: 16px; font-size: 0.85rem; color: {T['text_sub']}; border-top: 1px solid {T['border']}; padding-top: 12px;">
                <div>Temperatura: <strong style="color: {T['text_main']};">{tend.get('temperatura', 'Estável')}</strong></div>
                <div>Vibração: <strong style="color: {T['text_main']};">{tend.get('vibracao', 'Estável')}</strong></div>
                <div>Consumo: <strong style="color: {T['text_main']};">{tend.get('consumo', 'Estável')}</strong></div>
            </div>
        </div>
        """
        st.markdown(textwrap.dedent(tend_html), unsafe_allow_html=True)

    # Valores da Última Medição
    if historico:
        ult = historico[-1]
        t_val = ult.get("temperatura", 0.0)
        v_val = ult.get("vibracao", 0.0)
        c_val = ult.get("consumo", 0.0)
        hora = ult.get("timestamp", "—")

        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            t_cor = T["accent_rose"] if t_val > 85.0 else T["accent_emerald"]
            t_txt = "Muito Quente (>85°C)" if t_val > 85.0 else "Normal (abaixo de 85°C)"
            html = f"""
            <div class="sensor-box">
                <div style="font-size: 0.75rem; color: {T['text_sub']}; font-weight: 700; text-transform: uppercase;">Temperatura</div>
                <div class="sensor-val" style="color: {t_cor};">{t_val} <span style="font-size: 1rem;">°C</span></div>
                <span style="font-size: 0.72rem; font-weight: 700; color: {t_cor};">{t_txt}</span>
            </div>
            """
            st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

        with sc2:
            v_cor = T["accent_rose"] if v_val > 8.0 else T["accent_emerald"]
            v_txt = "Trepidação Alta (>8.0)" if v_val > 8.0 else "Normal (abaixo de 8.0)"
            html = f"""
            <div class="sensor-box">
                <div style="font-size: 0.75rem; color: {T['text_sub']}; font-weight: 700; text-transform: uppercase;">Vibração</div>
                <div class="sensor-val" style="color: {v_cor};">{v_val} <span style="font-size: 1rem;">mm/s</span></div>
                <span style="font-size: 0.72rem; font-weight: 700; color: {v_cor};">{v_txt}</span>
            </div>
            """
            st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

        with sc3:
            c_cor = T["accent_rose"] if c_val > 500.0 else T["accent_emerald"]
            c_txt = "Sobrecarga (>500W)" if c_val > 500.0 else "Normal (abaixo de 500W)"
            html = f"""
            <div class="sensor-box">
                <div style="font-size: 0.75rem; color: {T['text_sub']}; font-weight: 700; text-transform: uppercase;">Consumo Elétrico</div>
                <div class="sensor-val" style="color: {c_cor};">{c_val} <span style="font-size: 1rem;">W</span></div>
                <span style="font-size: 0.72rem; font-weight: 700; color: {c_cor};">{c_txt}</span>
            </div>
            """
            st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

        with sc4:
            html = f"""
            <div class="sensor-box">
                <div style="font-size: 0.75rem; color: {T['text_sub']}; font-weight: 700; text-transform: uppercase;">Horário da Leitura</div>
                <div class="sensor-val" style="color: {T['accent_cyan']}; font-size: 1.4rem; margin-top: 10px;">{hora.split(' ')[-1] if ' ' in hora else hora}</div>
                <span style="font-size: 0.72rem; font-weight: 600; color: {T['text_muted']};">{hora.split(' ')[0] if ' ' in hora else 'Hoje'}</span>
            </div>
            """
            st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Botões Interativos Fáceis
    st.markdown("#### Ações com Esta Máquina")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("+ Adicionar Leitura Normal", use_container_width=True):
            registrar_leitura(dados, id_m, gerar_anomalia=False)
            st.toast("Leitura normal registrada com sucesso!", icon="✅")
            st.rerun()
    with b2:
        if st.button("Simular Falha de Teste", type="primary", use_container_width=True):
            registrar_leitura(dados, id_m, gerar_anomalia=True)
            st.toast("Falha simulada para teste de detecção!", icon="🚨")
            st.rerun()
    with b3:
        if st.button("Atualizar Análise", use_container_width=True):
            analisar_maquina(dados, id_m)
            st.toast("Análise atualizada!", icon="🔄")
            st.rerun()

    with st.expander("Testar Outros Tipos Específicos de Falha", expanded=False):
        st.caption("Escolha uma falha específica para simular:")
        sb1, sb2, sb3 = st.columns(3)
        with sb1:
            if st.button("Simular: Desgaste de Rolamento", use_container_width=True):
                leit = gerar_leitura_cenario("rolamento", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Cenário de Rolamento injetado!", icon="⚙️")
                st.rerun()
        with sb2:
            if st.button("Simular: Superaquecimento", use_container_width=True):
                leit = gerar_leitura_cenario("aquecimento", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Superaquecimento injetado!", icon="🔥")
                st.rerun()
        with sb3:
            if st.button("Simular: Sobrecarga Elétrica", use_container_width=True):
                leit = gerar_leitura_cenario("sobrecarga", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Sobrecarga injetada!", icon="⚡")
                st.rerun()

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Gráficos Simples e Claros
    st.markdown("#### Histórico em Gráficos")

    if len(historico) < 2:
        st.info("Ainda há poucas leituras salvas (mínimo de 2). Clique em '+ Adicionar Leitura Normal' acima para gerar dados.")
    else:
        df_hist = pd.DataFrame(historico)

        tab1, tab2, tab3, tab4 = st.tabs([
            "Temperatura",
            "Vibração",
            "Consumo",
            "Todos Juntos",
        ])

        with tab1:
            st.plotly_chart(
                criar_grafico_telemetria(df_hist, "temperatura", "Temperatura", "°C", 85.0, T["accent_cyan"]),
                use_container_width=True,
            )
        with tab2:
            st.plotly_chart(
                criar_grafico_telemetria(df_hist, "vibracao", "Vibração", "mm/s", 8.0, T["accent_amber"]),
                use_container_width=True,
            )
        with tab3:
            st.plotly_chart(
                criar_grafico_telemetria(df_hist, "consumo", "Consumo", "W", 500.0, T["accent_violet"]),
                use_container_width=True,
            )
        with tab4:
            fig_multi = go.Figure()
            for col, cor, nome in [
                ("temperatura", T["accent_cyan"], "Temp (°C)"),
                ("vibracao", T["accent_amber"], "Vibração (mm/s)"),
                ("consumo", T["accent_violet"], "Consumo (W)"),
            ]:
                fig_multi.add_trace(
                    go.Scatter(x=df_hist["timestamp"], y=df_hist[col], mode="lines", name=nome, line=dict(color=cor, width=2.5))
                )
            fig_multi.update_layout(
                paper_bgcolor=T["plot_paper"],
                plot_bgcolor=T["plot_bg"],
                hovermode="x unified",
                margin=dict(l=10, r=10, t=30, b=10),
                height=320,
                xaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"]),
                yaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"]),
                legend=dict(font=dict(color=T["text_sub"])),
            )
            st.plotly_chart(fig_multi, use_container_width=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Exportar Arquivos
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
                    use_container_width=True,
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
                    use_container_width=True,
                )

            st.markdown("##### Ordem de Serviço:")
            st.code(gerar_ordem_servico_texto(maquina), language="text")


# -----------------------------------------------------------------------------
# Fluxo Principal & Barra Lateral Sincronizada
# -----------------------------------------------------------------------------
def main():
    dados = carregar_dados()
    maquinas = dados.get("maquinas", [])

    # Topo
    renderizar_topbar()
    renderizar_kpis_topo(maquinas)

    # Barra Lateral
    with st.sidebar:
        st.markdown("<p style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-top: 10px; margin-bottom: 6px; letter-spacing: 0.5px;'>Navegação Rápida</p>", unsafe_allow_html=True)

        opcoes = ["Todas as Máquinas (Início)"]
        mapa_ids = {"Todas as Máquinas (Início)": None}
        idx_selecionado = 0

        for i, m in enumerate(maquinas):
            label = f"[#{m['id']:02d}] {m['nome']}"
            opcoes.append(label)
            mapa_ids[label] = m["id"]
            if st.session_state["maquina_ativa_id"] == m["id"]:
                idx_selecionado = i + 1

        escolha = st.selectbox(
            "Ver máquina:",
            options=opcoes,
            index=idx_selecionado,
            label_visibility="collapsed",
        )

        # Atualiza a seleção de navegação
        novo_id = mapa_ids.get(escolha)
        if novo_id != st.session_state["maquina_ativa_id"]:
            st.session_state["maquina_ativa_id"] = novo_id
            st.rerun()

        st.markdown("---")

        # Formulário Simples de Nova Máquina
        st.markdown("<p style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;'>Cadastrar Nova Máquina</p>", unsafe_allow_html=True)
        with st.form("form_nova_maquina", clear_on_submit=True):
            nome_input = st.text_input("Nome da Máquina:", placeholder="Ex: Torno CNC 03", label_visibility="collapsed")
            btn_add = st.form_submit_button("+ Cadastrar Máquina", use_container_width=True)

            if btn_add:
                nome_limpo = nome_input.strip()
                if not nome_limpo:
                    st.error("Digite um nome para a máquina.")
                else:
                    try:
                        nova = criar_maquina(dados, nome_limpo)
                        st.toast(f"Máquina '{nova['nome']}' cadastrada com sucesso!", icon="✅")
                        st.session_state["maquina_ativa_id"] = nova["id"]
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

        # Excluir Máquina
        if st.session_state["maquina_ativa_id"] is not None:
            maq_atual = next((m for m in maquinas if m["id"] == st.session_state["maquina_ativa_id"]), None)
            if maq_atual:
                st.markdown("---")
                st.markdown("<p style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;'>Excluir Máquina</p>", unsafe_allow_html=True)
                with st.expander("Apagar esta máquina", expanded=False):
                    st.caption(f"Atenção: removerá '{maq_atual['nome']}' e todo o seu histórico.")
                    confirm = st.checkbox("Sim, quero apagar", key=f"del_{maq_atual['id']}")
                    if st.button("Confirmar Exclusão", type="primary", disabled=not confirm, use_container_width=True):
                        if remover_maquina(dados, maq_atual["id"]):
                            st.toast("Máquina removida!", icon="🗑️")
                            st.session_state["maquina_ativa_id"] = None
                            st.rerun()

        st.markdown("---")
        st.caption("MetalSense • Projeto TechForge")

    # Renderização da Tela Ativa
    maquina_selecionada = None
    if st.session_state["maquina_ativa_id"] is not None:
        maquina_selecionada = next((m for m in maquinas if m["id"] == st.session_state["maquina_ativa_id"]), None)

    if maquina_selecionada is None:
        renderizar_pagina_inicio(dados, maquinas)
    else:
        renderizar_detalhes_maquina(dados, maquina_selecionada)


if __name__ == "__main__":
    main()
