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
    page_title="MetalSense | Monitoramento Industrial",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Gerenciamento de Estado
# -----------------------------------------------------------------------------
if "maquina_ativa_id" not in st.session_state:
    st.session_state["maquina_ativa_id"] = None

if "busca_termo" not in st.session_state:
    st.session_state["busca_termo"] = ""

# -----------------------------------------------------------------------------
# Design Tokens (Extraídos com precisão de assistente/web-chat)
# -----------------------------------------------------------------------------
T = {
    # Viewport & Floating Window
    "background":       "#000000",                  # Fundo externo preto sólido
    "window_bg":        "#0E0E10",                  # Contêiner da janela flutuante
    "sidebar_bg":       "#121214",                  # Barra lateral esquerda (25-30%)
    "main_bg":          "#161618",                  # Área principal de trabalho (70-75%)
    "surface":          "#1C1C1E",                  # Superfície de base
    "surface_card":     "#1E1E20",                  # Grandes cartões e blocos
    "surface_card_alt": "#222224",                  # Variação interna de cartões e barras
    "surface_hover":    "#2A2A2E",                  # Hover suave
    "surface_elevated": "#2E2E32",                  # Elementos sobrepostos
    
    # Bordas e Linhas Ultrafinas
    "border":           "rgba(255, 255, 255, 0.07)",
    "border_subtle":    "rgba(255, 255, 255, 0.04)",
    "border_solid":     "#27272A",
    "border_active":    "rgba(255, 255, 255, 0.14)",
    
    # Tipografia Flat Monocromática
    "text_primary":     "#F2F2F3",                  # Branco puro suave
    "text_secondary":   "#9CA3AF",                  # Cinza-médio
    "text_muted":       "#6B7280",                  # Cinza atenuado
    "text_dim":         "#4B5563",                  # Cinza de baixo contraste para títulos caixa alta
    
    # Botões & Badges
    "btn_action_bg":    "#FFFFFF",                  # Botão de ação branco sólido alto contraste
    "btn_action_fg":    "#000000",                  # Texto preto no botão branco
    "pill_active_bg":   "rgba(255, 255, 255, 0.08)",# Pílula retangular arredondada translúcida ativa
    "pill_active_border": "rgba(255, 255, 255, 0.12)",
    "badge_bg":         "#1E1E20",                  # Marcador circular escuro
    "badge_border":     "rgba(255, 255, 255, 0.06)",
    "badge_fg":         "rgba(255, 255, 255, 0.70)",
    
    # Sinais Operacionais Industriais
    "success":          "#10B981",                  # Verde esmeralda (Operação normal)
    "warning":          "#F59E0B",                  # Âmbar (Atenção / Advertência)
    "danger":           "#EF4444",                  # Vermelho (Anomalia detectada)
    
    # Gráficos Plotly Flat
    "plot_paper":       "rgba(0, 0, 0, 0)",
    "plot_bg":          "#161618",
    "plot_grid":        "rgba(255, 255, 255, 0.04)",
    "plot_text":        "#9CA3AF",
    "hover_bg":         "#1E1E20",
}

# ---------------------------------------------------------------------------
# Biblioteca de Ícones SVG Lineares (Traço Fino 1.7px — Padrão Lucide/web-chat)
# ---------------------------------------------------------------------------
ICONS = {
    "panel-left-close": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><path d="M9 3v18"/><path d="m16 15-3-3 3-3"/></svg>',
    "panel-left": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><path d="M9 3v18"/><path d="m14 9 3 3-3 3"/></svg>',
    "chevron-down": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>',
    "chevron-right": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>',
    "search": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    "plus": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>',
    "settings": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
    "activity": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/></svg>',
    "server": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"/><rect width="20" height="8" x="2" y="14" rx="2" ry="2"/><line x1="6" x2="6.01" y1="6" y2="6"/><line x1="6" x2="6.01" y1="18" y2="18"/></svg>',
    "cpu": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>',
    "book-open": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
    "grid": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>',
    "check-circle-2": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>',
    "alert-circle": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>',
}


def get_icon(name: str, color: str = "currentColor", size: int = 16) -> str:
    """Gera string de ícone SVG inline com traço fino e preciso."""
    tmpl = ICONS.get(name, "")
    return tmpl.format(s=size, c=color)


# ---------------------------------------------------------------------------
# CSS Global — Réplica Estrita de assistente/web-chat adaptada a MetalSense
# ---------------------------------------------------------------------------
CSS_GLOBAL = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;450;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

/* ============== RESET & FUNDO EXTERNO PRETO SÓLIDO ============== */
html, body {{
    background-color: {T["background"]} !important;
    background: {T["background"]} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    color: {T["text_primary"]} !important;
    margin: 0 !important;
    padding: 0 !important;
    color-scheme: dark !important;
    overflow-x: hidden !important;
}}

.stApp {{
    background-color: {T["background"]} !important;
    background: {T["background"]} !important;
    color: {T["text_primary"]} !important;
}}

/* Header do Streamlit transparente e compacto */
header[data-testid="stHeader"] {{
    background: transparent !important;
    border: none !important;
    height: 32px !important;
}}

/* ============== JANELA FLUTUANTE (MAIN PANEL ~70-75%) ============== */
section.main {{
    background: {T["background"]} !important;
}}

section.main > div.block-container {{
    background-color: {T["main_bg"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 18px !important;
    margin: 12px 16px 16px 8px !important;
    padding: 0px 24px 28px 24px !important;
    max-width: 100% !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45) !important;
    overflow: hidden !important;
}}

/* ============== BARRA LATERAL (SIDEBAR ~25-30%) ============== */
section[data-testid="stSidebar"] {{
    background-color: {T["sidebar_bg"]} !important;
    border-right: 1px solid {T["border_subtle"]} !important;
    border-radius: 18px 0 0 18px !important;
    padding-top: 14px !important;
}}

section[data-testid="stSidebar"] > div:first-child {{
    padding-top: 10px !important;
}}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stMarkdown label {{
    color: {T["text_primary"]};
}}

section[data-testid="stSidebar"] hr {{
    display: none !important;
}}

/* ============== CABEÇALHO DA SIDEBAR ============== */
.sidebar-header-box {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    margin-bottom: 14px;
    background: transparent;
    border-radius: 12px;
    cursor: default;
}}
.sidebar-header-avatar {{
    width: 36px;
    height: 36px;
    background: #FFFFFF;
    color: #000000;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 15px;
    letter-spacing: -0.5px;
    flex-shrink: 0;
}}
.sidebar-header-info {{
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
}}
.sidebar-header-title {{
    font-size: 13px;
    font-weight: 600;
    letter-spacing: -0.2px;
    color: #FFFFFF;
    line-height: 1.1;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.sidebar-header-sub {{
    font-size: 11px;
    color: rgba(255, 255, 255, 0.45);
    line-height: 1.2;
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.sidebar-header-chevron {{
    color: rgba(255, 255, 255, 0.40);
    display: flex;
    align-items: center;
}}

/* ============== SEPARADORES DE SEÇÃO CAIXA ALTA ============== */
.sidebar-section-title {{
    padding: 12px 12px 6px 12px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.14em;
    color: rgba(255, 255, 255, 0.30);
    text-transform: uppercase;
    margin: 0;
}}

/* ============== ITENS DE NAVEGAÇÃO NA SIDEBAR ============== */
section[data-testid="stSidebar"] div.stButton > button {{
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    text-align: left !important;
    width: 100% !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;
    color: rgba(255, 255, 255, 0.55) !important;
    font-size: 13px !important;
    font-weight: 450 !important;
    padding: 8px 12px !important;
    margin-bottom: 2px !important;
    box-shadow: none !important;
    transition: all 0.14s ease !important;
}}

section[data-testid="stSidebar"] div.stButton > button:hover {{
    background: rgba(255, 255, 255, 0.04) !important;
    color: #FFFFFF !important;
    border-color: transparent !important;
}}

section[data-testid="stSidebar"] div.stButton > button div[data-testid="stMarkdownContainer"] {{
    width: 100% !important;
    text-align: left !important;
}}

section[data-testid="stSidebar"] div.stButton > button p {{
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    width: 100% !important;
    margin: 0 !important;
    font-size: 13px !important;
    font-weight: 450 !important;
}}

/* Elemento Selecionado na Sidebar: Pílula translúcida com texto em branco puro */
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
    background-color: {T["pill_active_bg"]} !important;
    border: 1px solid {T["pill_active_border"]} !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}}

section[data-testid="stSidebar"] div.stButton > button[kind="primary"] * {{
    color: #FFFFFF !important;
}}

section[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {{
    background-color: rgba(255, 255, 255, 0.12) !important;
    color: #FFFFFF !important;
}}

/* Botão de Ação Primária da Sidebar (Novo Ativo / Ação) */
section[data-testid="stSidebar"] div[data-testid="stFormSubmitButton"] > button {{
    background: #FFFFFF !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 9px 14px !important;
    justify-content: center !important;
    text-align: center !important;
}}

section[data-testid="stSidebar"] div[data-testid="stFormSubmitButton"] > button:hover {{
    background: rgba(255, 255, 255, 0.90) !important;
    color: #000000 !important;
}}

/* Rodapé da Sidebar */
.sidebar-footer-box {{
    margin-top: 24px;
    padding-top: 14px;
    border-top: 1px solid {T["border_subtle"]};
}}

.sidebar-user-pill {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 12px;
    margin-top: 6px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid {T["border_subtle"]};
}}

.sidebar-user-avatar {{
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #FFFFFF;
    color: #000000;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    flex-shrink: 0;
}}

/* ============== BARRA SUPERIOR (HEADER DA ÁREA PRINCIPAL) ============== */
.main-header-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 54px;
    border-bottom: 1px solid {T["border"]};
    padding: 12px 0 16px 0;
    margin-bottom: 18px;
}}

.main-header-left {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.collapse-box {{
    width: 32px;
    height: 32px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.07);
    background: rgba(255, 255, 255, 0.03);
    color: rgba(255, 255, 255, 0.60);
    display: flex;
    align-items: center;
    justify-content: center;
}}

.breadcrumbs-trail {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.35);
}}

.breadcrumbs-trail span.active {{
    color: #FFFFFF;
    font-weight: 550;
}}

.status-badge-inline {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 500;
    background: rgba(16, 185, 129, 0.10);
    border: 1px solid rgba(16, 185, 129, 0.20);
    color: #34D399;
    margin-left: 8px;
}}

.status-badge-inline.warn {{
    background: rgba(245, 158, 11, 0.10);
    border-color: rgba(245, 158, 11, 0.20);
    color: #FBBF24;
}}

.status-badge-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #34D399;
}}

.status-badge-dot.warn {{
    background: #FBBF24;
}}

.main-header-right {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.search-pill {{
    display: flex;
    align-items: center;
    gap: 8px;
    height: 36px;
    padding: 0 14px;
    border-radius: 9999px;
    background: #1E1E20;
    border: 1px solid rgba(255, 255, 255, 0.06);
    font-size: 13px;
    color: rgba(255, 255, 255, 0.40);
    min-width: 190px;
}}

.search-pill-shortcut {{
    margin-left: auto;
    font-size: 10px;
    font-family: monospace;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.40);
}}

.header-user-avatar {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.10);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #000000;
    font-size: 11px;
    font-weight: 700;
}}

/* ============== CORPO DA PÁGINA: BLOCOS SKELETON / CARDS FLAT ============== */
/* 1. Topo: Pequeno bloco retangular horizontal indicando a área de título */
.topo-title-card {{
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.topo-progress-stripe {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2.5px;
    background: rgba(255, 255, 255, 0.05);
}}

.topo-progress-fill {{
    height: 100%;
    background: {T["success"]};
    width: 100%;
    transition: width 0.3s ease;
}}

.topo-title-heading {{
    font-size: 14px;
    font-weight: 600;
    letter-spacing: -0.2px;
    color: {T["text_primary"]};
}}

.topo-title-desc {{
    font-size: 11px;
    color: {T["text_secondary"]};
    margin-top: 2px;
}}

.topo-title-meta {{
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    color: {T["text_secondary"]};
    display: flex;
    align-items: center;
    gap: 8px;
}}

/* Faixa de KPIs em 4 colunas planas */
.topo-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 20px;
    gap: 16px;
}}

.topo-kpi-col {{
    display: flex;
    flex-direction: column;
    border-right: 1px solid {T["border_subtle"]};
    padding-right: 12px;
}}

.topo-kpi-col:last-child {{
    border-right: none;
}}

.topo-kpi-label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {T["text_secondary"]};
    margin-bottom: 4px;
}}

.topo-kpi-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.55rem;
    font-weight: 700;
    color: {T["text_primary"]};
    line-height: 1.1;
}}

.topo-kpi-desc {{
    font-size: 11px;
    color: {T["text_muted"]};
    margin-top: 2px;
}}

/* 2. Linha Intermediária: Dois grandes cartões em proporções idênticas (50% / 50%) */
.mid-card {{
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 14px;
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: border-color 0.15s ease;
}}

.mid-card:hover {{
    border-color: rgba(255, 255, 255, 0.10);
}}

.mid-card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid {T["border_subtle"]};
}}

.mid-card-title {{
    font-size: 13px;
    font-weight: 600;
    letter-spacing: -0.2px;
    color: {T["text_primary"]};
}}

.mid-card-badge {{
    background: {T["surface_card_alt"]};
    border: 1px solid {T["border_solid"]};
    color: {T["text_secondary"]};
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
}}

/* 3. Base: Grande seção retangular com subtítulo e quatro barras horizontais longas empilhadas */
.base-section {{
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 14px;
    padding: 20px;
    margin-top: 20px;
}}

.base-section-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}}

.base-section-subtitle-bar {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid {T["border_subtle"]};
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {T["text_secondary"]};
}}

/* Quatro barras horizontais longas empilhadas verticalmente com espaçamento uniforme */
.telemetry-bar-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: {T["surface_card_alt"]};
    border: 1px solid {T["border_subtle"]};
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    transition: all 0.15s ease;
}}

.telemetry-bar-row:last-child {{
    margin-bottom: 0;
}}

.telemetry-bar-row:hover {{
    background: {T["surface_hover"]};
    border-color: rgba(255, 255, 255, 0.09);
}}

.telemetry-bar-left {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.telemetry-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: {T["success"]};
    flex-shrink: 0;
}}

.telemetry-dot.warn {{
    background: {T["warning"]};
}}

.telemetry-dot.danger {{
    background: {T["danger"]};
}}

.telemetry-bar-name {{
    font-size: 13px;
    font-weight: 600;
    color: {T["text_primary"]};
}}

.telemetry-bar-ts {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: {T["text_muted"]};
}}

.telemetry-bar-stats {{
    display: flex;
    align-items: center;
    gap: 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: {T["text_secondary"]};
}}

.telemetry-bar-stats strong {{
    color: {T["text_primary"]};
}}

/* ============== CONTROLES & INPUTS FLAT ============== */
div.stButton > button {{
    background: {T["surface_card_alt"]} !important;
    color: {T["text_primary"]} !important;
    border: 1px solid {T["border_solid"]} !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 7px 14px !important;
    box-shadow: none !important;
    transition: all 0.14s ease !important;
}}

div.stButton > button:hover {{
    background: {T["surface_hover"]} !important;
    border-color: rgba(255, 255, 255, 0.15) !important;
    color: #FFFFFF !important;
}}

div.stButton > button[kind="primary"] {{
    background: #FFFFFF !important;
    color: #000000 !important;
    border: none !important;
    font-weight: 600 !important;
}}

div.stButton > button[kind="primary"] * {{
    color: #000000 !important;
}}

div.stButton > button[kind="primary"]:hover {{
    background: rgba(255, 255, 255, 0.90) !important;
    color: #000000 !important;
}}

/* Inputs de Texto & Form */
div[data-baseweb="input"] > div,
input, textarea {{
    background-color: #1A1A1E !important;
    color: {T["text_primary"]} !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    box-shadow: none !important;
}}

input:focus, textarea:focus {{
    border-color: rgba(255, 255, 255, 0.15) !important;
}}

/* Selectbox Dropdown */
div[data-testid="stSelectbox"] > div > div {{
    background-color: {T["surface_card"]} !important;
    border: 1px solid {T["border_solid"]} !important;
    border-radius: 10px !important;
    color: {T["text_primary"]} !important;
}}

div[data-testid="stSelectboxVirtualDropdown"],
div[class*="e1fp86qc4"] {{
    background-color: {T["surface_card"]} !important;
    border: 1px solid {T["border_solid"]} !important;
    border-radius: 12px !important;
    color: {T["text_primary"]} !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5) !important;
}}

/* Tabs minimalistas */
div[data-testid="stTabs"] button {{
    color: {T["text_muted"]} !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    border-bottom: 2px solid transparent !important;
    padding: 8px 14px !important;
}}

div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: #FFFFFF !important;
    border-bottom: 2px solid #FFFFFF !important;
    font-weight: 600 !important;
}}

/* Expanders */
div[data-testid="stExpander"] {{
    background: {T["surface_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 12px !important;
}}

div[data-testid="stExpander"] summary {{
    color: {T["text_primary"]} !important;
    font-size: 13px !important;
}}

/* Scrollbar ultrafina monocromática */
::-webkit-scrollbar {{
    width: 4px;
    height: 4px;
}}
::-webkit-scrollbar-track {{
    background: transparent;
}}
::-webkit-scrollbar-thumb {{
    background: {T["border_solid"]};
    border-radius: 4px;
}}
</style>
"""
st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Gráficos Plotly — Estilo Flat Minimalista Monocromático
# ---------------------------------------------------------------------------
def criar_gauge_saude_flat(score: float) -> go.Figure:
    """Velocímetro minimalista com visual técnico monocromático."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={
                'suffix': "%",
                'font': {'size': 36, 'color': T["text_primary"], 'family': 'JetBrains Mono, monospace'},
            },
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': T["border_solid"], 'nticks': 5,
                         'tickfont': {'color': T["text_muted"], 'size': 9}},
                'bar': {'color': "#FFFFFF", 'thickness': 0.20},
                'bgcolor': T["surface_card_alt"],
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50],   'color': 'rgba(239, 68, 68, 0.15)'},
                    {'range': [50, 75],  'color': 'rgba(245, 158, 11, 0.15)'},
                    {'range': [75, 100], 'color': 'rgba(255, 255, 255, 0.08)'},
                ],
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=170,
        margin=dict(l=10, r=10, t=10, b=10),
        font={'color': T["text_primary"]},
    )
    return fig


def criar_grafico_telemetria_flat(
    df: pd.DataFrame, metrica: str, titulo: str, unidade: str, limite: float, cor_linha: str = "#F2F2F3"
) -> go.Figure:
    """Gráfico linear flat com grade de baixo contraste e linha de corte."""
    fig = go.Figure()

    fig.add_hline(
        y=limite,
        line_dash="dot",
        line_color=T["text_muted"],
        line_width=1.0,
        annotation_text=f"Limite ({limite} {unidade})",
        annotation_position="top right",
        annotation_font=dict(color=T["text_muted"], size=9, family="JetBrains Mono"),
    )

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"] if "timestamp" in df.columns else list(range(len(df))),
            y=df[metrica],
            mode="lines+markers",
            name=f"{titulo} ({unidade})",
            line=dict(color=cor_linha, width=1.7),
            marker=dict(size=4, color=cor_linha),
            hovertemplate="<b>%{y:.2f} " + unidade + "</b><br>%{x}<extra></extra>",
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=T["plot_bg"],
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=T["hover_bg"],
            font_size=11,
            font_color=T["text_primary"],
            font_family="Inter, sans-serif",
            bordercolor=T["border_solid"],
        ),
        margin=dict(l=10, r=10, t=25, b=10),
        height=270,
        xaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                   tickfont=dict(size=9, color=T["plot_text"])),
        yaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                   tickfont=dict(size=9, color=T["plot_text"])),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(color=T["text_secondary"], size=10)),
        font={'color': T["text_primary"]},
    )
    return fig


# ---------------------------------------------------------------------------
# Componentes de Topo (Header da Área Principal & Titulo Skeleton)
# ---------------------------------------------------------------------------
def renderizar_main_header(maquina_selecionada=None):
    """Barra superior com breadcrumbs, campo de busca em pílula e avatar circular."""
    if maquina_selecionada is None:
        trail_html = '<span class="active">Visão Geral da Planta</span>'
        status_dot = '<span class="status-badge-inline"><span class="status-badge-dot"></span>Telemetria Ao Vivo</span>'
    else:
        m_id = maquina_selecionada["id"]
        m_nome = maquina_selecionada["nome"]
        trail_html = f'<span>Ativos</span> <span style="opacity:0.4;">/</span> <span class="active">#{m_id:02d} {m_nome}</span>'
        has_anomalia = (maquina_selecionada.get("status") == "anomalia")
        status_dot = (
            '<span class="status-badge-inline warn"><span class="status-badge-dot warn"></span>Alerta Operacional</span>'
            if has_anomalia
            else '<span class="status-badge-inline"><span class="status-badge-dot"></span>Operação Normal</span>'
        )

    collapse_ico = get_icon("panel-left-close", color="rgba(255,255,255,0.6)", size=15)
    search_ico = get_icon("search", color="rgba(255,255,255,0.35)", size=13)

    html = f"""
    <div class="main-header-bar">
      <div class="main-header-left">
        <div class="collapse-box">{collapse_ico}</div>
        <nav class="breadcrumbs-trail">
          <span>Workspace</span>
          <span style="opacity:0.3;">/</span>
          <span>MetalSense</span>
          <span style="opacity:0.3;">/</span>
          {trail_html}
        </nav>
        {status_dot}
      </div>
      <div class="main-header-right">
        <div class="search-pill">
          {search_ico}
          <span>Buscar ativos...</span>
          <span class="search-pill-shortcut">⌘K</span>
        </div>
        <div class="header-user-avatar">TF</div>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def renderizar_topo_title_card(titulo: str, subtitulo: str, meta_info: str = "Taxa: 120 req/min"):
    """Topo: Pequeno bloco retangular horizontal indicando a área de título."""
    html = f"""
    <div class="topo-title-card">
      <div class="topo-progress-stripe">
        <div class="topo-progress-fill"></div>
      </div>
      <div>
        <div class="topo-title-heading">{titulo}</div>
        <div class="topo-title-desc">{subtitulo}</div>
      </div>
      <div class="topo-title-meta">
        <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:{T['success']};"></span>
        <span>{meta_info}</span>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def renderizar_kpis_topo_minimalista(maquinas: list):
    """Área retangular horizontal com 4 blocos limpos de KPIs."""
    total_maquinas = len(maquinas)
    total_anomalias = sum(1 for m in maquinas if m.get("status") == "anomalia")
    total_leituras = sum(len(m.get("historico", [])) for m in maquinas)

    scores = []
    for m in maquinas:
        hist = m.get("historico", [])
        if hist:
            scores.append(calcular_indice_saude(hist)["score"])
    media_saude = round(sum(scores) / len(scores), 1) if scores else 100.0

    html = f"""
    <div class="topo-kpi-grid">
      <div class="topo-kpi-col">
        <span class="topo-kpi-label">Ativos Conectados</span>
        <span class="topo-kpi-value">{total_maquinas:02d}</span>
        <span class="topo-kpi-desc">Linhas industriais ativas</span>
      </div>
      <div class="topo-kpi-col">
        <span class="topo-kpi-label">Saúde Geral da Planta</span>
        <span class="topo-kpi-value">{media_saude}%</span>
        <span class="topo-kpi-desc">Classificação ponderada</span>
      </div>
      <div class="topo-kpi-col">
        <span class="topo-kpi-label">Alertas Preditivos</span>
        <span class="topo-kpi-value">{total_anomalias:02d}</span>
        <span class="topo-kpi-desc">{"Atenção imediata requerida" if total_anomalias > 0 else "Operação normal"}</span>
      </div>
      <div class="topo-kpi-col">
        <span class="topo-kpi-label">Medições Ingeridas</span>
        <span class="topo-kpi-value">{total_leituras:,}</span>
        <span class="topo-kpi-desc">Amostragens IoT em tempo real</span>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Página 1 — Visão Geral (Dois Cards Centrais + Tabela Inferior Empilhada)
# ---------------------------------------------------------------------------
def renderizar_pagina_inicio(dados: dict, maquinas: list):
    """Layout modular: dois cards 50%/50% e tabela inferior com 4 barras empilhadas."""
    c_left, c_right = st.columns(2)

    with c_left:
        # Card Esquerdo (50%) — Inventário de Ativos
        st.markdown(
            f"""
            <div class="mid-card">
              <div class="mid-card-header">
                <span class="mid-card-title">Inventário de Ativos em Operação</span>
                <span class="mid-card-badge">{len(maquinas)} máquinas</span>
              </div>
            """,
            unsafe_allow_html=True,
        )

        if not maquinas:
            st.info("Nenhuma máquina cadastrada. Adicione pela barra lateral.")
        else:
            for m in maquinas:
                m_id = m["id"]
                m_nome = m["nome"]
                status_m = m.get("status", "sem dados").lower()
                hist = m.get("historico", [])
                saude = calcular_indice_saude(hist)
                score = saude["score"]
                is_warn = (status_m == "anomalia")

                col_btn, col_info = st.columns([3, 1])
                with col_btn:
                    if st.button(f"#{m_id:02d} {m_nome}", key=f"sel_m_{m_id}", use_container_width=True):
                        st.session_state["maquina_ativa_id"] = m_id
                        st.rerun()
                with col_info:
                    dot_cls = "danger" if is_warn else ""
                    st.markdown(
                        f"""
                        <div style="display:flex; align-items:center; justify-content:flex-end; gap:8px; height:100%; padding-top:6px;">
                          <span style="font-family:'JetBrains Mono', monospace; font-size:13px; color:{T['text_primary']};">{score}%</span>
                          <span class="telemetry-dot {dot_cls}"></span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        # Card Direito (50%) — Diagnóstico Preditivo Global & Ingestão
        st.markdown(
            f"""
            <div class="mid-card">
              <div class="mid-card-header">
                <span class="mid-card-title">Diagnóstico Preditivo Global</span>
                <span class="mid-card-badge">TechForge AI Engine</span>
              </div>
              <div style="font-size:13px; color:{T['text_secondary']}; line-height:1.6; margin-bottom:16px;">
                O motor preditivo MetalSense processa variações contínuas de gradiente térmico (dT/dt), picos de aceleração mecânica e flutuações de potência para prevenir paradas críticas não planejadas.
              </div>
              <div style="background:{T['surface_card_alt']}; border:1px solid {T['border_subtle']}; border-radius:10px; padding:12px; margin-bottom:16px;">
                <div style="font-size:10px; font-weight:700; text-transform:uppercase; color:{T['text_muted']}; letter-spacing:0.08em; margin-bottom:4px;">Pipeline de Ingestão</div>
                <div style="font-size:12px; font-family:'JetBrains Mono', monospace; color:{T['text_primary']};">Gateway IoT • Rate Limiter: 120 req/min • Auth: X-API-Key • SQLite WAL</div>
              </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Coletar Amostragem em Todas as Máquinas", use_container_width=True):
            for m in maquinas:
                registrar_leitura(dados, m["id"], gerar_anomalia=False)
            st.toast("Amostragens coletadas em tempo real!", icon="✅")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # Base: Grande seção retangular contendo subtítulo e 4 barras horizontais longas empilhadas
    todas_leituras = []
    for m in maquinas:
        for r in m.get("historico", []):
            todas_leituras.append({**r, "maquina_nome": m["nome"], "maquina_id": m["id"]})
    todas_leituras = sorted(todas_leituras, key=lambda x: x.get("timestamp", ""), reverse=True)

    st.markdown(
        f"""
        <div class="base-section">
          <div class="base-section-header">
            <span class="base-section-subtitle-bar">Fluxo de Telemetria Industrial Recente</span>
            <span style="font-size:11px; color:{T['text_muted']}; font-family:'JetBrains Mono', monospace;">Buffer: {len(todas_leituras)} eventos</span>
          </div>
        """,
        unsafe_allow_html=True,
    )

    # Garante a exibição estrita de 4 barras horizontais uniformemente empilhadas
    itens_exibir = list(todas_leituras[:4])
    while len(itens_exibir) < 4:
        slot = len(itens_exibir) + 1
        itens_exibir.append({
            "maquina_nome": f"Linha Operacional {slot:02d} — Standby",
            "timestamp": "Ciclo programado em espera",
            "temperatura": 52.0,
            "vibracao": 1.9,
            "consumo": 265.0,
            "is_placeholder": True,
        })

    for item in itens_exibir:
        is_anomalo = (item.get("temperatura", 0) > 85.0 or item.get("vibracao", 0) > 8.0 or item.get("consumo", 0) > 500.0)
        dot_cls = "danger" if is_anomalo else ""
        ts = item.get("timestamp", "—")
        t_val = item.get("temperatura", 0.0)
        v_val = item.get("vibracao", 0.0)
        c_val = item.get("consumo", 0.0)
        nome_m = item.get("maquina_nome", "Ativo")

        st.markdown(
            f"""
            <div class="telemetry-bar-row">
              <div class="telemetry-bar-left">
                <span class="telemetry-dot {dot_cls}"></span>
                <span class="telemetry-bar-name">{nome_m}</span>
                <span class="telemetry-bar-ts">{ts}</span>
              </div>
              <div class="telemetry-bar-stats">
                <span>Temp: <strong>{t_val:.1f}°C</strong></span>
                <span>Vib: <strong>{v_val:.2f} mm/s</strong></span>
                <span>Pot: <strong>{c_val:.0f} W</strong></span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Página 2 — Detalhes da Máquina Selecionada
# ---------------------------------------------------------------------------
def renderizar_detalhes_maquina(dados: dict, maquina: dict):
    """Visualização detalhada com 2 grandes cards intermediários e histórico."""
    id_m = maquina["id"]
    nome_m = maquina["nome"]
    historico = maquina.get("historico", [])
    status_m = maquina.get("status", "sem dados").lower()

    diagnostico_texto = analisar_maquina(dados, id_m)
    saude = calcular_indice_saude(historico)
    score = saude["score"]

    # Botão minimalista de retorno à visão consolidada
    if st.button("← Voltar para Visão Geral", use_container_width=False):
        st.session_state["maquina_ativa_id"] = None
        st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # Linha Intermediária: Dois Grandes Cartões (50% / 50%)
    col_card1, col_card2 = st.columns(2)

    with col_card1:
        # Card 1 (50%): Saúde Operacional & Diagnóstico Preditivo
        st.markdown(
            f"""
            <div class="mid-card">
              <div class="mid-card-header">
                <span class="mid-card-title">Saúde Operacional & Diagnóstico</span>
                <span class="mid-card-badge">Ativo #{id_m:02d}</span>
              </div>
            """,
            unsafe_allow_html=True,
        )

        st.plotly_chart(criar_gauge_saude_flat(score), use_container_width=True)

        st.markdown(
            f"""
            <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:{T['text_muted']}; margin-top:10px; margin-bottom:4px; letter-spacing:0.06em;">
              Análise Preditiva de Falhas
            </div>
            <div style="font-size:13px; line-height:1.55; color:{T['text_primary']};">
              {diagnostico_texto}
            </div>
            """,
            unsafe_allow_html=True,
        )

        tend = saude.get("tendencias", {})
        st.markdown(
            f"""
            <div style="display:flex; gap:16px; margin-top:14px; padding-top:10px; border-top:1px solid {T['border_subtle']}; font-size:12px; color:{T['text_muted']}; font-family:'JetBrains Mono', monospace;">
              <div>Temp: <strong style="color:{T['text_primary']};">{tend.get('temperatura', 'Estável')}</strong></div>
              <div>Vib: <strong style="color:{T['text_primary']};">{tend.get('vibracao', 'Estável')}</strong></div>
              <div>Consumo: <strong style="color:{T['text_primary']};">{tend.get('consumo', 'Estável')}</strong></div>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_card2:
        # Card 2 (50%): Leituras em Tempo Real & Injeção de Falhas
        st.markdown(
            f"""
            <div class="mid-card">
              <div class="mid-card-header">
                <span class="mid-card-title">Telemetria & Injeção de Cenários</span>
                <span class="mid-card-badge">{len(historico)} amostras</span>
              </div>
            """,
            unsafe_allow_html=True,
        )

        if historico:
            ult = historico[-1]
            t_val = ult.get("temperatura", 0.0)
            v_val = ult.get("vibracao", 0.0)
            c_val = ult.get("consumo", 0.0)

            c_s1, c_s2, c_s3 = st.columns(3)
            with c_s1:
                st.markdown(
                    f"""
                    <div style="background:{T['surface_card_alt']}; border:1px solid {T['border_subtle']}; border-radius:10px; padding:12px; text-align:center;">
                      <div style="font-size:10px; font-weight:700; text-transform:uppercase; color:{T['text_muted']}; letter-spacing:0.06em;">Temperatura</div>
                      <div style="font-family:'JetBrains Mono', monospace; font-size:1.25rem; font-weight:700; color:{T['text_primary']}; margin-top:4px;">{t_val:.1f}°C</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_s2:
                st.markdown(
                    f"""
                    <div style="background:{T['surface_card_alt']}; border:1px solid {T['border_subtle']}; border-radius:10px; padding:12px; text-align:center;">
                      <div style="font-size:10px; font-weight:700; text-transform:uppercase; color:{T['text_muted']}; letter-spacing:0.06em;">Vibração</div>
                      <div style="font-family:'JetBrains Mono', monospace; font-size:1.25rem; font-weight:700; color:{T['text_primary']}; margin-top:4px;">{v_val:.2f} mm/s</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_s3:
                st.markdown(
                    f"""
                    <div style="background:{T['surface_card_alt']}; border:1px solid {T['border_subtle']}; border-radius:10px; padding:12px; text-align:center;">
                      <div style="font-size:10px; font-weight:700; text-transform:uppercase; color:{T['text_muted']}; letter-spacing:0.06em;">Consumo</div>
                      <div style="font-family:'JetBrains Mono', monospace; font-size:1.25rem; font-weight:700; color:{T['text_primary']}; margin-top:4px;">{c_val:.0f} W</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if st.button("+ Leitura Normal", use_container_width=True):
                registrar_leitura(dados, id_m, gerar_anomalia=False)
                st.toast("Leitura registrada com sucesso!", icon="✅")
                st.rerun()
        with b_col2:
            if st.button("Simular Falha Genérica", type="primary", use_container_width=True):
                registrar_leitura(dados, id_m, gerar_anomalia=True)
                st.toast("Falha simulada injetada!", icon="🚨")
                st.rerun()

        with st.expander("Injetar Cenários Específicos de Falha", expanded=False):
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                if st.button("Rolamento", use_container_width=True):
                    leit = gerar_leitura_cenario("rolamento", ciclo=len(historico) + 1)
                    registrar_leitura(dados, id_m, leitura=leit)
                    st.toast("Cenário de Desgaste de Rolamento!", icon="⚙️")
                    st.rerun()
            with f_col2:
                if st.button("Aquecimento", use_container_width=True):
                    leit = gerar_leitura_cenario("aquecimento", ciclo=len(historico) + 1)
                    registrar_leitura(dados, id_m, leitura=leit)
                    st.toast("Superaquecimento Térmico!", icon="🔥")
                    st.rerun()
            with f_col3:
                if st.button("Sobrecarga", use_container_width=True):
                    leit = gerar_leitura_cenario("sobrecarga", ciclo=len(historico) + 1)
                    registrar_leitura(dados, id_m, leitura=leit)
                    st.toast("Sobrecarga Elétrica!", icon="⚡")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # Base: Grande seção retangular com subtítulo e 4 barras horizontais longas empilhadas
    st.markdown(
        f"""
        <div class="base-section">
          <div class="base-section-header">
            <span class="base-section-subtitle-bar">Últimas 4 Amostragens de Linha</span>
            <span style="font-size:11px; color:{T['text_muted']}; font-family:'JetBrains Mono', monospace;">Ativo #{id_m:02d}</span>
          </div>
        """,
        unsafe_allow_html=True,
    )

    amostras = list(reversed(historico[-4:]))
    while len(amostras) < 4:
        slot = len(amostras) + 1
        amostras.append({
            "timestamp": "Standby — Amostragem programada",
            "temperatura": 55.0,
            "vibracao": 2.0,
            "consumo": 275.0,
            "is_placeholder": True,
        })

    for item in amostras:
        is_anomalo = (item.get("temperatura", 0) > 85.0 or item.get("vibracao", 0) > 8.0 or item.get("consumo", 0) > 500.0)
        dot_cls = "danger" if is_anomalo else ""
        ts = item.get("timestamp", "—")
        t_val = item.get("temperatura", 0.0)
        v_val = item.get("vibracao", 0.0)
        c_val = item.get("consumo", 0.0)

        st.markdown(
            f"""
            <div class="telemetry-bar-row">
              <div class="telemetry-bar-left">
                <span class="telemetry-dot {dot_cls}"></span>
                <span class="telemetry-bar-name">{nome_m}</span>
                <span class="telemetry-bar-ts">{ts}</span>
              </div>
              <div class="telemetry-bar-stats">
                <span>Temp: <strong>{t_val:.1f}°C</strong></span>
                <span>Vib: <strong>{v_val:.2f} mm/s</strong></span>
                <span>Pot: <strong>{c_val:.0f} W</strong></span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Seção de Gráficos e Exportações
    if len(historico) >= 2:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        df_hist = pd.DataFrame(historico)
        tab1, tab2, tab3, tab4 = st.tabs(["Temperatura", "Vibração", "Consumo", "Multi-eixo"])

        with tab1:
            st.plotly_chart(
                criar_grafico_telemetria_flat(df_hist, "temperatura", "Temperatura", "°C", 85.0, "#F2F2F3"),
                use_container_width=True,
            )
        with tab2:
            st.plotly_chart(
                criar_grafico_telemetria_flat(df_hist, "vibracao", "Vibração", "mm/s", 8.0, "#9CA3AF"),
                use_container_width=True,
            )
        with tab3:
            st.plotly_chart(
                criar_grafico_telemetria_flat(df_hist, "consumo", "Consumo", "W", 500.0, "#6B7280"),
                use_container_width=True,
            )
        with tab4:
            fig_multi = go.Figure()
            for col_name, cor, nome in [
                ("temperatura", "#F2F2F3", "Temperatura (°C)"),
                ("vibracao",    "#9CA3AF", "Vibração (mm/s)"),
                ("consumo",     "#6B7280", "Consumo (W)"),
            ]:
                fig_multi.add_trace(
                    go.Scatter(x=df_hist["timestamp"], y=df_hist[col_name], mode="lines",
                               name=nome, line=dict(color=cor, width=1.7))
                )
            fig_multi.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor=T["plot_bg"],
                hovermode="x unified",
                hoverlabel=dict(
                    bgcolor=T["hover_bg"],
                    font_size=11,
                    font_color=T["text_primary"],
                    font_family="Inter, sans-serif",
                    bordercolor=T["border_solid"],
                ),
                margin=dict(l=10, r=10, t=25, b=10),
                height=270,
                xaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                           tickfont=dict(color=T["plot_text"], size=9)),
                yaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                           tickfont=dict(color=T["plot_text"], size=9)),
                legend=dict(font=dict(color=T["text_secondary"], size=10)),
                font={'color': T["text_primary"]},
            )
            st.plotly_chart(fig_multi, use_container_width=True)

    with st.expander("Exportar Laudo Técnico e Relatórios", expanded=False):
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
                label="Baixar Histórico (CSV)",
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

        st.markdown("##### Ordem de Serviço Emitida:")
        st.code(gerar_ordem_servico_texto(maquina), language="text")


# ---------------------------------------------------------------------------
# Fluxo Principal & Barra Lateral (Sidebar)
# ---------------------------------------------------------------------------
def main():
    dados = carregar_dados()
    maquinas = dados.get("maquinas", [])

    # Barra Lateral
    with st.sidebar:
        # 1. Cabeçalho: Avatar quadrado em branco sólido + texto em 2 níveis + chevron down
        chevron_down_ico = get_icon("chevron-down", color="rgba(255,255,255,0.4)", size=14)
        st.markdown(
            f"""
            <div class="sidebar-header-box">
              <div class="sidebar-header-avatar">M</div>
              <div class="sidebar-header-info">
                <span class="sidebar-header-title">
                  MetalSense
                  {chevron_down_ico}
                </span>
                <span class="sidebar-header-sub">TechForge • Indústria 4.0</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Separador de Seção Caixa Alta: NAVEGAÇÃO
        st.markdown("<div class='sidebar-section-title'>NAVEGAÇÃO</div>", unsafe_allow_html=True)

        is_all_selected = (st.session_state["maquina_ativa_id"] is None)
        total_anomalias = sum(1 for m in maquinas if m.get("status") == "anomalia")

        if st.button("Visão Geral da Planta", key="btn_nav_all", icon=":material/grid_view:", use_container_width=True,
                     type="primary" if is_all_selected else "secondary"):
            st.session_state["maquina_ativa_id"] = None
            st.rerun()

        # 3. Separador de Seção: ATIVOS EM OPERAÇÃO
        st.markdown("<div class='sidebar-section-title'>ATIVOS EM OPERAÇÃO</div>", unsafe_allow_html=True)

        opcoes = ["Visão Geral (Todas)"]
        mapa_ids = {"Visão Geral (Todas)": None}
        idx_sel = 0

        for i, m in enumerate(maquinas):
            label = f"[#{m['id']:02d}] {m['nome']}"
            opcoes.append(label)
            mapa_ids[label] = m["id"]
            if st.session_state["maquina_ativa_id"] == m["id"]:
                idx_sel = i + 1

        escolha = st.selectbox("Seletor de Máquina:", options=opcoes, index=idx_sel, label_visibility="collapsed")
        novo_id = mapa_ids.get(escolha)
        if novo_id != st.session_state["maquina_ativa_id"]:
            st.session_state["maquina_ativa_id"] = novo_id
            st.rerun()

        # Lista de atalhos rápidos com chevrons e badge circular no item com alerta
        for m in maquinas:
            m_id = m["id"]
            m_nome = m["nome"]
            is_active = (st.session_state["maquina_ativa_id"] == m_id)
            has_alert = (m.get("status") == "anomalia")
            
            # Um dos itens exibe um marcador (badge) circular escuro à direita.
            # Pequenas setas angulares (chevrons) apontam para a direita em itens expansíveis.
            indicador = "●" if has_alert else "›"
            btn_label = f"#{m_id:02d} {m_nome}    {indicador}"
            if st.button(btn_label, key=f"sb_m_{m_id}", icon=":material/precision_manufacturing:", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state["maquina_ativa_id"] = m_id
                st.rerun()

        # 4. Separador: GESTÃO DE ATIVOS
        st.markdown("<div class='sidebar-section-title'>GESTÃO DE ATIVOS</div>", unsafe_allow_html=True)

        with st.form("form_nova_maquina", clear_on_submit=True):
            nome_input = st.text_input("Cadastrar Máquina:", placeholder="Nome do novo ativo...", label_visibility="collapsed")
            btn_add = st.form_submit_button("+ Cadastrar Ativo", use_container_width=True)

            if btn_add:
                nome_limpo = nome_input.strip()
                if not nome_limpo:
                    st.error("Digite um nome válido.")
                else:
                    try:
                        nova = criar_maquina(dados, nome_limpo)
                        st.toast(f"Máquina '{nova['nome']}' cadastrada!", icon="✅")
                        st.session_state["maquina_ativa_id"] = nova["id"]
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

        # Opção de exclusão segura
        if st.session_state["maquina_ativa_id"] is not None:
            maq_atual = next((m for m in maquinas if m["id"] == st.session_state["maquina_ativa_id"]), None)
            if maq_atual:
                with st.expander("Excluir este ativo", expanded=False):
                    confirm = st.checkbox("Confirmar remoção", key=f"del_{maq_atual['id']}")
                    if st.button("Remover Máquina", type="primary", disabled=not confirm, use_container_width=True):
                        if remover_maquina(dados, maq_atual["id"]):
                            st.toast("Ativo removido!", icon="🗑️")
                            st.session_state["maquina_ativa_id"] = None
                            st.rerun()

        # 5. Rodapé da Sidebar: Dois itens alinhados à base + perfil
        st.markdown("<div class='sidebar-footer-box'>", unsafe_allow_html=True)
        st.button("Configurações do Sistema", key="btn_footer_settings", icon=":material/settings:", use_container_width=True, type="secondary")
        st.button("Documentação & API", key="btn_footer_docs", icon=":material/menu_book:", use_container_width=True, type="secondary")
        
        st.markdown(
            f"""
            <div class="sidebar-user-pill">
              <div class="sidebar-user-avatar">TF</div>
              <div style="flex:1; min-width:0;">
                <div style="font-size:12px; font-weight:500; color:{T['text_primary']}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">Operador Confiabilidade</div>
                <div style="font-size:10px; color:{T['text_muted']};">TechForge Industrial</div>
              </div>
              <span style="width:6px; height:6px; border-radius:50%; background:{T['success']};"></span>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Renderização da Área Principal (Main Panel)
    maquina_selecionada = None
    if st.session_state["maquina_ativa_id"] is not None:
        maquina_selecionada = next((m for m in maquinas if m["id"] == st.session_state["maquina_ativa_id"]), None)

    # 1. Barra Superior (Header)
    renderizar_main_header(maquina_selecionada)

    # 2. Topo: Pequeno bloco retangular horizontal indicando a área de título
    if maquina_selecionada is None:
        renderizar_topo_title_card("Visão Geral da Planta Fabril", "Telemetria & Diagnóstico Preditivo em Tempo Real", "Gateway IoT • Rate Limiter: 120 req/min")
    else:
        renderizar_topo_title_card(f"Ativo #{maquina_selecionada['id']:02d} — {maquina_selecionada['nome']}", "Análise Operacional de Linha de Produção", "Taxa de Ingestão Nominal")

    # 3. Topo: Área de KPIs em 4 colunas planas
    renderizar_kpis_topo_minimalista(maquinas)

    # 4. Conteúdo Central (Linha intermediária 50%/50%) e Base (4 barras uniformes)
    if maquina_selecionada is None:
        renderizar_pagina_inicio(dados, maquinas)
    else:
        renderizar_detalhes_maquina(dados, maquina_selecionada)


if __name__ == "__main__":
    main()
