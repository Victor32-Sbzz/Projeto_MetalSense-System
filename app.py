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
# Estado de Navegação e Seleção
# -----------------------------------------------------------------------------
if "maquina_ativa_id" not in st.session_state:
    st.session_state["maquina_ativa_id"] = None

if "busca_termo" not in st.session_state:
    st.session_state["busca_termo"] = ""

# -----------------------------------------------------------------------------
# Paleta de Cores Monocromática Minimalista (Dark Mode Grafite/Preto Profundo)
# -----------------------------------------------------------------------------
T = {
    # Backgrounds e Janela Flutuante
    "viewport_bg":        "#000000",       # Fundo externo preto sólido
    "window_bg":          "#0a0a0c",       # Corpo da janela flutuante
    "sidebar_bg":         "#09090b",       # Barra lateral esquerda (25-30%)
    "main_bg":            "#0c0c0e",       # Área principal de trabalho (70-75%)
    "surface_card":       "#131317",       # Blocos e cartões principais
    "surface_card_alt":   "#17171c",       # Variação sutil de profundidade
    "surface_metric":     "#1b1b22",       # Mini-cards e skeleton blocks
    "surface_hover":      "#202027",       # Hover de linhas e cartões
    
    # Navegação e Seleção
    "pill_selected":      "rgba(255, 255, 255, 0.08)", # Pílula retangular arredondada ativa
    "pill_border":        "rgba(255, 255, 255, 0.12)",
    "badge_bg":           "#1f1f24",                   # Marcador circular escuro
    "badge_border":       "rgba(255, 255, 255, 0.10)",
    
    # Linhas Divisórias e Bordas Ultrafinas
    "border":             "rgba(255, 255, 255, 0.07)",
    "border_solid":       "#222228",
    "border_subtle":      "rgba(255, 255, 255, 0.04)",
    
    # Tipografia Monocromática de Precisão
    "text_main":          "#fafafa",       # Branco puro suave
    "text_sub":           "#a1a1aa",       # Cinza-médio
    "text_muted":         "#71717a",       # Cinza atenuado
    "text_dim":           "#52525b",       # Cinza escuro para separadores caixa alta
    
    # Inputs & Controles Flat
    "input_bg":           "#131317",
    "input_border":       "#27272a",
    "placeholder_color":  "#71717a",
    "btn_bg":             "#17171c",
    "btn_border":         "#27272a",
    "btn_hover_bg":       "#22222a",
    "btn_primary_bg":     "#ffffff",       # Branco sólido de alto contraste
    "btn_primary_fg":     "#09090b",       # Texto preto no botão branco
    
    # Sinais Operacionais Industriais (Flat, sem gradientes chamativos)
    "accent_white":       "#ffffff",
    "status_ok":          "#22c55e",       # Ponto verde sutil
    "status_warn":        "#ef4444",       # Ponto vermelho alerta
    "status_amber":       "#f59e0b",       # Ponto âmbar atenção
    "status_idle":        "#71717a",       # Ponto cinza
    
    # Plotly Flat
    "plot_paper":         "rgba(0,0,0,0)",
    "plot_bg":            "#131317",
    "plot_grid":          "rgba(255, 255, 255, 0.04)",
    "plot_text":          "#a1a1aa",
    "hover_bg":           "#18181d",
}

# ---------------------------------------------------------------------------
# Biblioteca de Ícones SVG Lineares (Traço Fino e Preciso — 1.75px)
# ---------------------------------------------------------------------------
ICONS = {
    "sidebar-toggle": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3" ry="3"></rect><line x1="9" y1="3" x2="9" y2="21"></line><path d="m14 9-3 3 3 3"></path></svg>',
    "chevron-down": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>',
    "chevron-right": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>',
    "search": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
    "user": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="7" r="4"></circle><path d="M5.5 21a8.5 8.5 0 0 1 13 0"></path></svg>',
    "server": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>',
    "activity": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>',
    "shield": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
    "alert": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    "settings": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>',
    "book-open": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>',
    "grid": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>',
    "thermometer": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"></path></svg>',
    "waves": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path></svg>',
    "zap": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>',
}


def get_icon(name: str, color: str = "currentColor", size: int = 16) -> str:
    """Retorna código SVG inline estritamente formatado com traço fino."""
    template = ICONS.get(name, "")
    return template.format(s=size, c=color)


# ---------------------------------------------------------------------------
# CSS Global — Estética Minimalista Flat Monocromática (Dark Mode Industrial)
# ---------------------------------------------------------------------------
CSS_GLOBAL = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

/* ============== FUNDO EXTERNO PRETO SÓLIDO & RESET ============== */
html, body {{
    background-color: {T["viewport_bg"]} !important;
    background: {T["viewport_bg"]} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: {T["text_main"]} !important;
    margin: 0 !important;
    padding: 0 !important;
    color-scheme: dark !important;
}}

/* ============== JANELA GLOBAL FLUTUANTE COM CANTOS ARREDONDADOS ============== */
.stApp {{
    background-color: {T["viewport_bg"]} !important;
    background: {T["viewport_bg"]} !important;
    color: {T["text_main"]} !important;
}}

/* Header do Streamlit transparente */
header[data-testid="stHeader"] {{
    background: transparent !important;
    border: none !important;
    height: 38px !important;
}}

/* ============== ÁREA PRINCIPAL DE TRABALHO (MAIN PANEL ~70-75%) ============== */
section.main {{
    background: {T["viewport_bg"]} !important;
}}
section.main > div.block-container {{
    background-color: {T["main_bg"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 14px !important;
    margin: 12px 16px 16px 8px !important;
    padding: 0px 24px 28px 24px !important;
    max-width: 100% !important;
    box-shadow: none !important;
}}

/* ============== BARRA LATERAL (SIDEBAR ~25-30%) ============== */
section[data-testid="stSidebar"] {{
    background-color: {T["sidebar_bg"]} !important;
    border-right: 1px solid {T["border"]} !important;
    border-radius: 14px 0 0 14px !important;
    padding-top: 12px !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding-top: 10px !important;
}}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stMarkdown label {{
    color: {T["text_main"]};
}}
section[data-testid="stSidebar"] hr {{
    display: none !important;
}}

/* ============== COMPONENTES DA SIDEBAR ============== */
.sidebar-header-box {{
    display: flex;
    align-items: center;
    padding: 10px 12px;
    margin-bottom: 16px;
    background: transparent;
    border-radius: 10px;
    transition: background 0.15s ease;
    cursor: default;
}}
.sidebar-header-avatar {{
    width: 32px;
    height: 32px;
    background: {T["btn_primary_bg"]};
    color: {T["btn_primary_fg"]};
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 14px;
    letter-spacing: -0.5px;
    flex-shrink: 0;
}}
.sidebar-header-text {{
    margin-left: 10px;
    flex: 1;
    display: flex;
    flex-direction: column;
}}
.sidebar-header-title {{
    font-size: 0.90rem;
    font-weight: 600;
    color: {T["text_main"]};
    line-height: 1.2;
}}
.sidebar-header-sub {{
    font-size: 0.72rem;
    color: {T["text_muted"]};
    font-weight: 500;
}}
.sidebar-header-chevron {{
    color: {T["text_muted"]};
    display: flex;
    align-items: center;
}}

/* Separadores de Seção Caixa Alta */
.sidebar-section-label {{
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {T["text_dim"]};
    padding: 14px 10px 6px 10px;
    margin: 0;
}}

/* Itens de Navegação na Sidebar */
/* Alinhamento estrito à esquerda, combinando ícones lineares com traço fino e rótulos de texto */
section[data-testid="stSidebar"] div.stButton > button {{
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    text-align: left !important;
    width: 100% !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    color: {T["text_sub"]} !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    padding: 8px 12px !important;
    margin-bottom: 2px !important;
    box-shadow: none !important;
    transition: all 0.12s ease !important;
}}
section[data-testid="stSidebar"] div.stButton > button:hover {{
    background: rgba(255, 255, 255, 0.04) !important;
    border-color: rgba(255, 255, 255, 0.06) !important;
    color: #ffffff !important;
}}
section[data-testid="stSidebar"] div.stButton > button div[data-testid="stMarkdownContainer"] {{
    width: 100% !important;
    text-align: left !important;
}}
section[data-testid="stSidebar"] div.stButton > button p {{
    text-align: left !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    width: 100% !important;
    margin: 0 !important;
    font-size: 0.83rem !important;
}}
/* O elemento atualmente selecionado é evidenciado por um contêiner em formato de pílula retangular arredondada com preenchimento cinza-médio translúcido e texto/ícone em branco puro */
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
    background: {T["pill_selected"]} !important;
    background-color: {T["pill_selected"]} !important;
    border: 1px solid {T["pill_border"]} !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] * {{
    color: #ffffff !important;
}}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {{
    background-color: rgba(255, 255, 255, 0.12) !important;
    border-color: rgba(255, 255, 255, 0.18) !important;
    color: #ffffff !important;
}}
/* Botão de formulário de cadastro na barra lateral */
section[data-testid="stSidebar"] div[data-testid="stFormSubmitButton"] > button {{
    background: {T["btn_primary_bg"]} !important;
    color: {T["btn_primary_fg"]} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    justify-content: center !important;
    text-align: center !important;
}}

.sidebar-nav-pill {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 8px 10px;
    border-radius: 8px;
    margin-bottom: 2px;
    text-decoration: none;
    color: {T["text_sub"]};
    font-size: 0.84rem;
    font-weight: 500;
    transition: all 0.12s ease;
    border: 1px solid transparent;
}}
.sidebar-nav-pill.selected {{
    background-color: {T["pill_selected"]};
    border-color: {T["pill_border"]};
    color: {T["text_main"]};
    font-weight: 600;
}}
.sidebar-nav-left {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.sidebar-nav-badge {{
    background: {T["badge_bg"]};
    border: 1px solid {T["badge_border"]};
    color: {T["text_sub"]};
    border-radius: 9999px;
    padding: 1px 7px;
    font-size: 0.70rem;
    font-family: 'Space Grotesk', monospace;
    font-weight: 600;
}}

/* Rodapé da Sidebar */
.sidebar-footer-group {{
    margin-top: 24px;
    padding-top: 14px;
    border-top: 1px solid {T["border_subtle"]};
}}

/* ============== BARRA SUPERIOR (HEADER DA ÁREA PRINCIPAL) ============== */
.main-header-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 0 16px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid {T["border"]};
}}
.main-header-left {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.main-collapse-box {{
    width: 28px;
    height: 28px;
    border-radius: 6px;
    border: 1px solid {T["border_solid"]};
    background: {T["surface_card"]};
    display: flex;
    align-items: center;
    justify-content: center;
    color: {T["text_muted"]};
}}
.main-breadcrumbs {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    color: {T["text_muted"]};
    font-weight: 500;
}}
.main-breadcrumbs span.active {{
    color: {T["text_main"]};
    font-weight: 600;
}}
.main-header-right {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.search-pill-box {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: {T["surface_card"]};
    border: 1px solid {T["border_solid"]};
    border-radius: 9999px;
    padding: 5px 14px;
    font-size: 0.78rem;
    color: {T["text_muted"]};
    font-family: 'Inter', sans-serif;
    min-width: 170px;
}}
.search-pill-shortcut {{
    margin-left: auto;
    font-size: 0.68rem;
    background: {T["surface_metric"]};
    border: 1px solid {T["border_solid"]};
    padding: 2px 6px;
    border-radius: 4px;
    color: {T["text_muted"]};
    font-family: monospace;
}}
.user-avatar-circle {{
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: {T["surface_metric"]};
    border: 1px solid {T["border_solid"]};
    display: flex;
    align-items: center;
    justify-content: center;
    color: {T["text_sub"]};
    font-size: 0.76rem;
    font-weight: 600;
}}

/* ============== BLOCOS FLAT & SKELETON / PLACEHOLDERS ============== */
/* Topo: Pequeno bloco retangular horizontal indicando a área de título */
.topo-title-block {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 12px;
}}
.topo-title-left {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.topo-title-indicator {{
    width: 7px;
    height: 7px;
    border-radius: 2px;
    background: {T["text_main"]};
}}
.topo-title-text {{
    font-size: 0.88rem;
    font-weight: 600;
    color: {T["text_main"]};
    letter-spacing: -0.2px;
}}
.topo-title-sub {{
    font-size: 0.72rem;
    color: {T["text_muted"]};
}}
.topo-title-badge {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: {T["surface_metric"]};
    border: 1px solid {T["border_solid"]};
    border-radius: 9999px;
    padding: 2px 10px;
    font-size: 0.68rem;
    font-weight: 600;
    color: {T["text_sub"]};
    text-transform: uppercase;
    letter-spacing: 0.04em;
}}
.topo-title-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: {T["status_ok"]};
}}

/* Topo: Pequeno bloco retangular horizontal (Área de KPIs) */
.topo-kpi-bar {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 20px;
    gap: 16px;
}}
.topo-kpi-col {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-right: 1px solid {T["border_subtle"]};
    padding-right: 12px;
}}
.topo-kpi-col:last-child {{
    border-right: none;
}}
.topo-kpi-label {{
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {T["text_muted"]};
    margin-bottom: 4px;
}}
.topo-kpi-value {{
    font-family: 'Space Grotesk', monospace;
    font-size: 1.55rem;
    font-weight: 700;
    color: {T["text_main"]};
    line-height: 1.1;
}}
.topo-kpi-sub {{
    font-size: 0.72rem;
    color: {T["text_muted"]};
    margin-top: 2px;
}}

/* Linha Intermediária: Dois grandes cartões em proporções idênticas (50% / 50%) */
.mid-card {{
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 12px;
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
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
    font-size: 0.92rem;
    font-weight: 600;
    color: {T["text_main"]};
    letter-spacing: -0.2px;
}}
.mid-card-badge {{
    background: {T["surface_metric"]};
    border: 1px solid {T["border_solid"]};
    color: {T["text_sub"]};
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.70rem;
    font-weight: 600;
    text-transform: uppercase;
}}

/* Base: Grande seção retangular contendo subtítulo e 4 barras horizontais longas */
.base-section {{
    background: {T["surface_card"]};
    border: 1px solid {T["border"]};
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
}}
.base-section-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}}
.base-section-subtitle {{
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {T["text_muted"]};
}}
.base-section-subtitle-bar {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: {T["surface_metric"]};
    border: 1px solid {T["border_solid"]};
    border-radius: 6px;
    padding: 3px 9px;
    font-size: 0.70rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {T["text_sub"]};
}}

/* Barras horizontais empilhadas uniformemente */
.telemetry-row-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: {T["surface_card_alt"]};
    border: 1px solid {T["border_subtle"]};
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    transition: background 0.15s ease;
}}
.telemetry-row-bar:last-child {{
    margin-bottom: 0;
}}
.telemetry-row-bar:hover {{
    background: {T["surface_hover"]};
    border-color: {T["border_solid"]};
}}
.telemetry-col-main {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.telemetry-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: {T["status_ok"]};
}}
.telemetry-dot.warn {{
    background: {T["status_warn"]};
}}
.telemetry-timestamp {{
    font-family: 'Space Grotesk', monospace;
    font-size: 0.78rem;
    color: {T["text_muted"]};
}}
.telemetry-stats {{
    display: flex;
    align-items: center;
    gap: 18px;
    font-family: 'Space Grotesk', monospace;
    font-size: 0.82rem;
    color: {T["text_sub"]};
}}
.telemetry-stats strong {{
    color: {T["text_main"]};
}}

/* ============== BOTÕES & CONTROLES FLAT ============== */
div.stButton > button {{
    background: {T["btn_bg"]} !important;
    color: {T["text_main"]} !important;
    border: 1px solid {T["btn_border"]} !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: none !important;
    padding: 6px 14px !important;
    font-size: 0.84rem !important;
    transition: all 0.15s ease !important;
}}
div.stButton > button:hover {{
    background: {T["btn_hover_bg"]} !important;
    border-color: {T["text_muted"]} !important;
    color: #ffffff !important;
}}
div.stButton > button[kind="primary"],
button[kind="primary"] {{
    background: {T["btn_primary_bg"]} !important;
    color: {T["btn_primary_fg"]} !important;
    border: none !important;
    font-weight: 600 !important;
}}
div.stButton > button[kind="primary"] *,
button[kind="primary"] * {{
    color: {T["btn_primary_fg"]} !important;
}}
div.stButton > button[kind="primary"]:hover,
button[kind="primary"]:hover {{
    opacity: 0.90 !important;
    color: {T["btn_primary_fg"]} !important;
}}

/* Form inputs */
div[data-baseweb="input"] > div,
input, textarea {{
    background-color: {T["input_bg"]} !important;
    color: {T["text_main"]} !important;
    border: 1px solid {T["input_border"]} !important;
    border-radius: 8px !important;
    font-size: 0.84rem !important;
    box-shadow: none !important;
}}
input::placeholder {{
    color: {T["placeholder_color"]} !important;
}}

/* Selectbox Dropdown */
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stSelectbox"] [class*="e1fp86qc0"] {{
    background-color: {T["surface_card"]} !important;
    border: 1px solid {T["border_solid"]} !important;
    border-radius: 8px !important;
    color: {T["text_main"]} !important;
}}
div[data-testid="stSelectboxVirtualDropdown"],
div[class*="e1fp86qc4"] {{
    background-color: {T["surface_card"]} !important;
    border: 1px solid {T["border_solid"]} !important;
    border-radius: 10px !important;
    color: {T["text_main"]} !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
}}
div[data-testid="stSelectboxVirtualDropdown"] [data-item-hl] {{
    color: {T["text_main"]} !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
}}
div[data-testid="stSelectboxVirtualDropdown"] li:hover [data-item-hl],
div[data-testid="stSelectboxVirtualDropdown"] li[data-hovered] [data-item-hl] {{
    background-color: {T["pill_selected"]} !important;
    color: #ffffff !important;
}}

/* Tabs minimalistas */
div[data-testid="stTabs"] button {{
    color: {T["text_muted"]} !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    border-bottom: 2px solid transparent !important;
    padding: 8px 14px !important;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {T["text_main"]} !important;
    border-bottom: 2px solid {T["accent_white"]} !important;
    font-weight: 600 !important;
}}

/* Expanders */
div[data-testid="stExpander"] {{
    background: {T["surface_card"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 10px !important;
}}
div[data-testid="stExpander"] summary {{
    color: {T["text_main"]} !important;
    font-size: 0.84rem !important;
}}

/* Code block */
div[data-testid="stCode"], code, pre {{
    background-color: {T["surface_metric"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 8px !important;
    color: {T["text_sub"]} !important;
}}

/* Scrollbar fina monocromática */
::-webkit-scrollbar {{
    width: 5px;
    height: 5px;
}}
::-webkit-scrollbar-track {{
    background: transparent;
}}
::-webkit-scrollbar-thumb {{
    background: {T["border_solid"]};
    border-radius: 3px;
}}
</style>
"""
st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Componentes de Topo (Header da Área Principal & KPIs)
# ---------------------------------------------------------------------------
def renderizar_main_header(maquina_selecionada=None):
    """Barra superior minimalista com breadcrumbs, campo de busca e avatar."""
    if maquina_selecionada is None:
        breadcrumb_html = """
        <span class="active">Visão Geral</span>
        """
    else:
        m_id = maquina_selecionada["id"]
        m_nome = maquina_selecionada["nome"]
        breadcrumb_html = f"""
        <span>Ativos</span>
        <span>/</span>
        <span class="active">#{m_id:02d} {m_nome}</span>
        """

    collapse_ico = get_icon("sidebar-toggle", color=T["text_muted"], size=15)
    search_ico = get_icon("search", color=T["text_muted"], size=13)

    html = f"""
    <div class="main-header-bar">
      <div class="main-header-left">
        <div class="main-collapse-box">{collapse_ico}</div>
        <div class="main-breadcrumbs">
          <span>MetalSense</span>
          <span>/</span>
          {breadcrumb_html}
        </div>
      </div>
      <div class="main-header-right">
        <div class="search-pill-box">
          {search_ico}
          <span>Buscar ativos...</span>
          <span class="search-pill-shortcut">⌘K</span>
        </div>
        <div class="user-avatar-circle">TF</div>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def renderizar_bloco_titulo_topo(titulo: str, subtitulo: str = "Painel de Controle Industrial"):
    """Topo: Pequeno bloco retangular horizontal indicando a área de título."""
    html = f"""
    <div class="topo-title-block">
      <div class="topo-title-left">
        <div class="topo-title-indicator"></div>
        <span class="topo-title-text">{titulo}</span>
        <span class="topo-title-sub">• {subtitulo}</span>
      </div>
      <div class="topo-title-badge">
        <span class="topo-title-dot"></span>
        <span>Telemetria Ativa</span>
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
    <div class="topo-kpi-bar">
      <div class="topo-kpi-col">
        <span class="topo-kpi-label">Ativos Conectados</span>
        <span class="topo-kpi-value">{total_maquinas:02d}</span>
        <span class="topo-kpi-sub">Linhas industriais ativas</span>
      </div>
      <div class="topo-kpi-col">
        <span class="topo-kpi-label">Saúde Geral da Planta</span>
        <span class="topo-kpi-value">{media_saude}%</span>
        <span class="topo-kpi-sub">Classificação ponderada</span>
      </div>
      <div class="topo-kpi-col">
        <span class="topo-kpi-label">Alertas Preditivos</span>
        <span class="topo-kpi-value">{total_anomalias:02d}</span>
        <span class="topo-kpi-sub">{"Atenção requerida" if total_anomalias > 0 else "Operação normal"}</span>
      </div>
      <div class="topo-kpi-col">
        <span class="topo-kpi-label">Medições Ingeridas</span>
        <span class="topo-kpi-value">{total_leituras:,}</span>
        <span class="topo-kpi-sub">Amostragens em tempo real</span>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Gráficos Plotly — Estilo Flat Minimalista Monocromático
# ---------------------------------------------------------------------------
def criar_gauge_saude_flat(score: float) -> go.Figure:
    """Velocímetro minimalista monocromático com arco flat de alta precisão."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={
                'suffix': "%",
                'font': {'size': 38, 'color': T["text_main"], 'family': 'Space Grotesk, monospace'},
            },
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': T["border_solid"], 'nticks': 5,
                         'tickfont': {'color': T["text_muted"], 'size': 9}},
                'bar': {'color': T["accent_white"], 'thickness': 0.22},
                'bgcolor': T["surface_metric"],
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
        height=175,
        margin=dict(l=10, r=10, t=10, b=10),
        font={'color': T["text_main"]},
    )
    return fig


def criar_grafico_telemetria_flat(
    df: pd.DataFrame, metrica: str, titulo: str, unidade: str, limite: float, cor_linha: str = "#fafafa"
) -> go.Figure:
    """Gráfico linear flat com grade sutil e linha de corte discreta."""
    fig = go.Figure()

    fig.add_hline(
        y=limite,
        line_dash="dot",
        line_color=T["text_muted"],
        line_width=1.0,
        annotation_text=f"Limite ({limite} {unidade})",
        annotation_position="top right",
        annotation_font=dict(color=T["text_muted"], size=9, family="Space Grotesk"),
    )

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"] if "timestamp" in df.columns else list(range(len(df))),
            y=df[metrica],
            mode="lines+markers",
            name=f"{titulo} ({unidade})",
            line=dict(color=cor_linha, width=1.75),
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
            font_color=T["text_main"],
            font_family="Inter, sans-serif",
            bordercolor=T["border_solid"],
        ),
        margin=dict(l=10, r=10, t=25, b=10),
        height=280,
        xaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                   tickfont=dict(size=9, color=T["plot_text"])),
        yaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                   tickfont=dict(size=9, color=T["plot_text"])),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(color=T["text_sub"], size=10)),
        font={'color': T["text_main"]},
    )
    return fig


# ---------------------------------------------------------------------------
# Página 1 — Visão Geral (Dois Cards Centrais + Tabela Inferior Empilhada)
# ---------------------------------------------------------------------------
def renderizar_pagina_inicio(dados: dict, maquinas: list):
    """Layout modular: dois cards 50%/50% e tabela inferior empilhada."""
    c_left, c_right = st.columns(2)

    with c_left:
        # Card Esquerdo (50%) — Ativos Monitorados
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

                col_btn, col_info = st.columns([2, 1])
                with col_btn:
                    if st.button(f"#{m_id:02d} {m_nome}", key=f"sel_m_{m_id}", use_container_width=True):
                        st.session_state["maquina_ativa_id"] = m_id
                        st.rerun()
                with col_info:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px; height: 100%; padding-top: 6px;">
                          <span style="font-family: 'Space Grotesk', monospace; font-size: 0.84rem; color: {T['text_main']};">{score}%</span>
                          <span class="telemetry-dot {'warn' if is_warn else ''}"></span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        # Card Direito (50%) — Diagnóstico Preditivo Global & Controles
        st.markdown(
            f"""
            <div class="mid-card">
              <div class="mid-card-header">
                <span class="mid-card-title">Diagnóstico Preditivo Global</span>
                <span class="mid-card-badge">TechForge AI</span>
              </div>
              <div style="font-size: 0.86rem; color: {T['text_sub']}; line-height: 1.6; margin-bottom: 16px;">
                O motor preditivo MetalSense processa variações de gradiente térmico (dT/dt), picos de aceleração mecânica e oscilações de consumo elétrico para antecipar falhas industriais críticas.
              </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="background: {T['surface_card_alt']}; border: 1px solid {T['border_subtle']}; border-radius: 8px; padding: 12px; margin-bottom: 16px;">
              <div style="font-size: 0.70rem; font-weight: 700; text-transform: uppercase; color: {T['text_muted']}; margin-bottom: 4px;">Modo de Ingestão</div>
              <div style="font-size: 0.82rem; color: {T['text_main']};">Streaming Contínuo • Rate Limiter: 120 req/min • Auth: X-API-Key</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Coletar Amostragem em Todas as Máquinas", use_container_width=True):
            for m in maquinas:
                registrar_leitura(dados, m["id"], gerar_anomalia=False)
            st.toast("Leituras coletadas em tempo real!", icon="✅")
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
            <span class="base-section-subtitle-bar">Fluxo de Telemetria Industrial</span>
            <span style="font-size: 0.74rem; color: {T['text_muted']}; font-family: 'Space Grotesk', monospace;">Buffer: {len(todas_leituras)} eventos</span>
          </div>
        """,
        unsafe_allow_html=True,
    )

    # Garante exatamente 4 barras horizontais longas empilhadas verticalmente com espaçamento uniforme
    itens_exibir = list(todas_leituras[:4])
    while len(itens_exibir) < 4:
        slot = len(itens_exibir) + 1
        itens_exibir.append({
            "maquina_nome": f"Linha Industrial {slot:02d} — Standby",
            "timestamp": "Aguardando amostragem programada",
            "temperatura": 50.0,
            "vibracao": 1.8,
            "consumo": 260.0,
            "is_placeholder": True,
        })

    for item in itens_exibir:
        is_anomalo = (item.get("temperatura", 0) > 85.0 or item.get("vibracao", 0) > 8.0 or item.get("consumo", 0) > 500.0)
        dot_cls = "warn" if is_anomalo else ""
        ts = item.get("timestamp", "—")
        t_val = item.get("temperatura", 0.0)
        v_val = item.get("vibracao", 0.0)
        c_val = item.get("consumo", 0.0)
        nome_m = item.get("maquina_nome", "Ativo")

        st.markdown(
            f"""
            <div class="telemetry-row-bar">
              <div class="telemetry-col-main">
                <span class="telemetry-dot {dot_cls}"></span>
                <span style="font-size: 0.84rem; font-weight: 600; color: {T['text_main']};">{nome_m}</span>
                <span class="telemetry-timestamp">{ts}</span>
              </div>
              <div class="telemetry-stats">
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
    """Visualização da máquina com 2 grandes cards intermediários e histórico."""
    id_m = maquina["id"]
    nome_m = maquina["nome"]
    historico = maquina.get("historico", [])
    status_m = maquina.get("status", "sem dados").lower()

    diagnostico_texto = analisar_maquina(dados, id_m)
    saude = calcular_indice_saude(historico)
    score = saude["score"]

    # Botão minimalista de retorno
    if st.button("← Voltar para Visão Geral", use_container_width=False):
        st.session_state["maquina_ativa_id"] = None
        st.rerun()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    # Linha Intermediária: Dois Grandes Cards (50% / 50%)
    col_card1, col_card2 = st.columns(2)

    with col_card1:
        # Card 1 (50%): Saúde do Ativo + Diagnóstico Preditivo
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
            <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: {T['text_muted']}; margin-top: 10px; margin-bottom: 4px;">
              Análise Preditiva
            </div>
            <div style="font-size: 0.88rem; line-height: 1.5; color: {T['text_main']};">
              {diagnostico_texto}
            </div>
            """,
            unsafe_allow_html=True,
        )

        tend = saude.get("tendencias", {})
        st.markdown(
            f"""
            <div style="display: flex; gap: 16px; margin-top: 14px; padding-top: 10px; border-top: 1px solid {T['border_subtle']}; font-size: 0.78rem; color: {T['text_muted']}; font-family: 'Space Grotesk', monospace;">
              <div>Temp: <strong style="color: {T['text_main']};">{tend.get('temperatura', 'Estável')}</strong></div>
              <div>Vib: <strong style="color: {T['text_main']};">{tend.get('vibracao', 'Estável')}</strong></div>
              <div>Cons: <strong style="color: {T['text_main']};">{tend.get('consumo', 'Estável')}</strong></div>
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
                    <div style="background: {T['surface_card_alt']}; border: 1px solid {T['border_subtle']}; border-radius: 8px; padding: 10px; text-align: center;">
                      <div style="font-size: 0.66rem; font-weight: 700; text-transform: uppercase; color: {T['text_muted']};">Temperatura</div>
                      <div style="font-family: 'Space Grotesk', monospace; font-size: 1.25rem; font-weight: 700; color: {T['text_main']};">{t_val:.1f}°C</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_s2:
                st.markdown(
                    f"""
                    <div style="background: {T['surface_card_alt']}; border: 1px solid {T['border_subtle']}; border-radius: 8px; padding: 10px; text-align: center;">
                      <div style="font-size: 0.66rem; font-weight: 700; text-transform: uppercase; color: {T['text_muted']};">Vibração</div>
                      <div style="font-family: 'Space Grotesk', monospace; font-size: 1.25rem; font-weight: 700; color: {T['text_main']};">{v_val:.2f} mm/s</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_s3:
                st.markdown(
                    f"""
                    <div style="background: {T['surface_card_alt']}; border: 1px solid {T['border_subtle']}; border-radius: 8px; padding: 10px; text-align: center;">
                      <div style="font-size: 0.66rem; font-weight: 700; text-transform: uppercase; color: {T['text_muted']};">Consumo</div>
                      <div style="font-family: 'Space Grotesk', monospace; font-size: 1.25rem; font-weight: 700; color: {T['text_main']};">{c_val:.0f} W</div>
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
            <span class="base-section-subtitle-bar">Últimas Amostragens de Linha</span>
            <span style="font-size: 0.74rem; color: {T['text_muted']}; font-family: 'Space Grotesk', monospace;">Ativo #{id_m:02d}</span>
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
        dot_cls = "warn" if is_anomalo else ""
        ts = item.get("timestamp", "—")
        t_val = item.get("temperatura", 0.0)
        v_val = item.get("vibracao", 0.0)
        c_val = item.get("consumo", 0.0)

        st.markdown(
            f"""
            <div class="telemetry-row-bar">
              <div class="telemetry-col-main">
                <span class="telemetry-dot {dot_cls}"></span>
                <span style="font-size: 0.84rem; font-weight: 600; color: {T['text_main']};">{nome_m}</span>
                <span class="telemetry-timestamp">{ts}</span>
              </div>
              <div class="telemetry-stats">
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
                criar_grafico_telemetria_flat(df_hist, "temperatura", "Temperatura", "°C", 85.0, "#fafafa"),
                use_container_width=True,
            )
        with tab2:
            st.plotly_chart(
                criar_grafico_telemetria_flat(df_hist, "vibracao", "Vibração", "mm/s", 8.0, "#a1a1aa"),
                use_container_width=True,
            )
        with tab3:
            st.plotly_chart(
                criar_grafico_telemetria_flat(df_hist, "consumo", "Consumo", "W", 500.0, "#71717a"),
                use_container_width=True,
            )
        with tab4:
            fig_multi = go.Figure()
            for col_name, cor, nome in [
                ("temperatura", "#fafafa", "Temperatura (°C)"),
                ("vibracao",    "#a1a1aa", "Vibração (mm/s)"),
                ("consumo",     "#71717a", "Consumo (W)"),
            ]:
                fig_multi.add_trace(
                    go.Scatter(x=df_hist["timestamp"], y=df_hist[col_name], mode="lines",
                               name=nome, line=dict(color=cor, width=1.75))
                )
            fig_multi.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor=T["plot_bg"],
                hovermode="x unified",
                hoverlabel=dict(
                    bgcolor=T["hover_bg"],
                    font_size=11,
                    font_color=T["text_main"],
                    font_family="Inter, sans-serif",
                    bordercolor=T["border_solid"],
                ),
                margin=dict(l=10, r=10, t=25, b=10),
                height=280,
                xaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                           tickfont=dict(color=T["plot_text"], size=9)),
                yaxis=dict(showgrid=True, gridcolor=T["plot_grid"], color=T["plot_text"],
                           tickfont=dict(color=T["plot_text"], size=9)),
                legend=dict(font=dict(color=T["text_sub"], size=10)),
                font={'color': T["text_main"]},
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

        st.markdown("##### Ordem de Serviço:")
        st.code(gerar_ordem_servico_texto(maquina), language="text")


# ---------------------------------------------------------------------------
# Fluxo Principal & Barra Lateral (Sidebar)
# ---------------------------------------------------------------------------
def main():
    dados = carregar_dados()
    maquinas = dados.get("maquinas", [])

    # Barra Lateral
    with st.sidebar:
        # 1. Cabeçalho: botão/avatar quadrado branco de alto contraste + texto em 2 níveis + chevron down
        chevron_down_ico = get_icon("chevron-down", color=T["text_muted"], size=16)
        st.markdown(
            f"""
            <div class="sidebar-header-box">
              <div class="sidebar-header-avatar">M</div>
              <div class="sidebar-header-text">
                <span class="sidebar-header-title">MetalSense</span>
                <span class="sidebar-header-sub">TechForge Enterprise</span>
              </div>
              <div class="sidebar-header-chevron">{chevron_down_ico}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Separador de Seção Caixa Alta
        st.markdown("<div class='sidebar-section-label'>PLATAFORMA</div>", unsafe_allow_html=True)

        # Item de Navegação: Todas as Máquinas (Dashboard)
        grid_ico = get_icon("grid", color="#ffffff" if st.session_state["maquina_ativa_id"] is None else T["text_sub"], size=15)
        is_all_selected = (st.session_state["maquina_ativa_id"] is None)
        total_anomalias = sum(1 for m in maquinas if m.get("status") == "anomalia")

        if st.button("Visão Geral da Planta", key="btn_nav_all", icon=":material/grid_view:", use_container_width=True,
                     type="primary" if is_all_selected else "secondary"):
            st.session_state["maquina_ativa_id"] = None
            st.rerun()

        # 3. Separador: Máquinas em Operação
        st.markdown("<div class='sidebar-section-label'>MÁQUINAS EM OPERAÇÃO</div>", unsafe_allow_html=True)

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

        # Lista de atalhos rápidos com chevron e badge circular
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

        # 4. Separador: Gestão de Ativos
        st.markdown("<div class='sidebar-section-label'>GESTÃO DE ATIVOS</div>", unsafe_allow_html=True)

        with st.form("form_nova_maquina", clear_on_submit=True):
            nome_input = st.text_input("Cadastrar Máquina:", placeholder="Nome da Máquina...", label_visibility="collapsed")
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

        # Opção de exclusão
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

        # 5. Rodapé da Sidebar: Dois itens alinhados à base
        st.markdown("<div class='sidebar-footer-group'>", unsafe_allow_html=True)
        st.button("Documentação & API", key="btn_footer_docs", icon=":material/menu_book:", use_container_width=True, type="secondary")
        st.button("Configurações do Sistema", key="btn_footer_settings", icon=":material/settings:", use_container_width=True, type="secondary")
        st.markdown("</div>", unsafe_allow_html=True)

    # Renderização da Área Principal
    maquina_selecionada = None
    if st.session_state["maquina_ativa_id"] is not None:
        maquina_selecionada = next((m for m in maquinas if m["id"] == st.session_state["maquina_ativa_id"]), None)

    # 1. Barra Superior (Header)
    renderizar_main_header(maquina_selecionada)

    # 2. Topo: Pequeno bloco retangular horizontal indicando a área de título
    if maquina_selecionada is None:
        renderizar_bloco_titulo_topo("Visão Geral da Planta Industrial", "Telemetria & Diagnóstico Preditivo em Tempo Real")
    else:
        renderizar_bloco_titulo_topo(f"Ativo #{maquina_selecionada['id']:02d} — {maquina_selecionada['nome']}", "Análise Operacional de Linha de Produção")

    # 3. Topo: Área de KPIs
    renderizar_kpis_topo_minimalista(maquinas)

    # 4. Conteúdo Central (Linha intermediária 50%/50%) e Base (4 barras uniformes)
    if maquina_selecionada is None:
        renderizar_pagina_inicio(dados, maquinas)
    else:
        renderizar_detalhes_maquina(dados, maquina_selecionada)


if __name__ == "__main__":
    main()
