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
    page_title="MetalSense | Industrial Predictive IoT",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Estilos CSS de Alto Padrão (Inspirado em Dribbble / Dark Glassmorphism SaaS)
# -----------------------------------------------------------------------------
DRIBBBLE_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Fundo Principal - Dark Void com Gradientes Sutis */
.stApp {
    background: radial-gradient(circle at 15% 15%, #0f172a 0%, #070a13 75%);
    color: #f1f5f9;
}

/* Top Navbar Minimalista */
.dribbble-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 16px 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6);
}
.brand-group {
    display: flex;
    align-items: center;
    gap: 14px;
}
.brand-icon {
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.35);
}
.brand-text h1 {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #ffffff, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.brand-text p {
    margin: 0;
    font-size: 0.78rem;
    color: #64748b;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.live-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34d399;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.live-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 10px #10b981;
    animation: pulse-green 2s infinite;
}
@keyframes pulse-green {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1.1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* Cards de Métricas / KPI Dribbble */
.kpi-card {
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 16px;
    padding: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.kpi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(56, 189, 248, 0.4);
    box-shadow: 0 12px 28px -8px rgba(0, 242, 254, 0.15);
}
.kpi-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.kpi-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
.kpi-icon-wrap {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.1rem;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: -1px;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 0.78rem;
    color: #64748b;
    margin-top: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Badges de Status Fluorescentes */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}
.status-pill-normal {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #34d399;
    box-shadow: 0 0 16px rgba(16, 185, 129, 0.2);
}
.status-pill-anomalia {
    background: rgba(239, 68, 68, 0.18);
    border: 1px solid rgba(239, 68, 68, 0.5);
    color: #f87171;
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.35);
    animation: pulse-danger 1.5s infinite;
}
@keyframes pulse-danger {
    0% { transform: scale(0.97); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6); }
    70% { transform: scale(1.02); box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
    100% { transform: scale(0.97); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}
.status-pill-sem-dados {
    background: rgba(148, 163, 184, 0.1);
    border: 1px solid rgba(148, 163, 184, 0.2);
    color: #94a3b8;
}

/* Card Heroico da Máquina */
.asset-card {
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 18px;
    transition: all 0.3s ease;
}
.asset-card:hover {
    border-color: rgba(56, 189, 248, 0.35);
    box-shadow: 0 10px 30px -10px rgba(0, 242, 254, 0.15);
}

/* Painel de Diagnóstico com Borda Gradiente */
.ai-diagnosis-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 18px;
    padding: 22px 26px;
    box-shadow: 0 10px 30px -10px rgba(139, 92, 246, 0.2);
    margin-bottom: 24px;
}
.ai-diagnosis-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.95rem;
    font-weight: 700;
    color: #c084fc;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
}
.ai-diagnosis-text {
    font-size: 1.05rem;
    line-height: 1.6;
    color: #f1f5f9;
}

/* Tag de Causa Raiz */
.root-cause-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.35);
    color: #fca5a5;
    padding: 5px 12px;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-top: 8px;
    margin-right: 6px;
}

/* Sensor Mini Card */
.sensor-metric-box {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    transition: all 0.2s ease;
}
.sensor-metric-box:hover {
    border-color: rgba(255, 255, 255, 0.15);
}
.sensor-label {
    font-size: 0.78rem;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.sensor-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.7rem;
    font-weight: 700;
    color: #f8fafc;
    margin: 6px 0;
}
.sensor-badge {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    display: inline-block;
}

/* Estilo de Botões Primários */
div.stButton > button:first-child {
    border-radius: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
div.stButton > button:first-child:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px -6px rgba(0, 242, 254, 0.25);
}

/* Sidebar Dark Theme Refinement */
section[data-testid="stSidebar"] {
    background-color: #0b0f19;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
"""
st.markdown(DRIBBBLE_THEME_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Componentes Visuais Dribbble
# -----------------------------------------------------------------------------
def renderizar_navbar():
    """Barra de navegação superior inspirada em interfaces modernas de IoT."""
    agora = datetime.now().strftime("%d/%m/%Y • %H:%M")
    st.markdown(
        f"""
        <div class="dribbble-navbar">
            <div class="brand-group">
                <div class="brand-icon">⚡</div>
                <div class="brand-text">
                    <h1>METALSENSE</h1>
                    <p>TechForge Industrial Predictive OS</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 18px;">
                <div style="color: #64748b; font-size: 0.85rem; font-weight: 500;">
                    📅 {agora}
                </div>
                <div class="live-pill">
                    <span class="live-dot"></span>
                    <span>GATEWAY IOT ATIVO</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_kpis_topo(maquinas: list):
    """Grid de 4 cartões com métricas e micro-indicadores visuais."""
    total_maquinas = len(maquinas)
    total_normais = sum(1 for m in maquinas if m.get("status") == "normal")
    total_anomalias = sum(1 for m in maquinas if m.get("status") == "anomalia")
    total_leituras = sum(len(m.get("historico", [])) for m in maquinas)

    # Calcula média geral de saúde do parque
    scores = []
    for m in maquinas:
        hist = m.get("historico", [])
        if hist:
            scores.append(calcular_indice_saude(hist)["score"])
    media_saude = round(sum(scores) / len(scores), 1) if scores else 100.0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-card-header">
                    <span class="kpi-title">Parque Conectado</span>
                    <div class="kpi-icon-wrap" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8;">🏭</div>
                </div>
                <div class="kpi-value">{total_maquinas:02d}</div>
                <div class="kpi-sub">
                    <span style="color: #38bdf8;">●</span> Ativos Cadastrados
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        saude_cor = "#34d399" if media_saude >= 75 else ("#fbbf24" if media_saude >= 50 else "#f87171")
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-card-header">
                    <span class="kpi-title">Fleet Health Score</span>
                    <div class="kpi-icon-wrap" style="background: rgba(16, 185, 129, 0.15); color: #34d399;">🛡️</div>
                </div>
                <div class="kpi-value" style="color: {saude_cor};">{media_saude}%</div>
                <div class="kpi-sub">
                    <span>Média de Integridade Operacional</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        anomalia_bg = "rgba(239, 68, 68, 0.15)" if total_anomalias > 0 else "rgba(16, 185, 129, 0.1)"
        anomalia_cor = "#f87171" if total_anomalias > 0 else "#34d399"
        anomalia_texto = f"{total_anomalias:02d} Em Alerta" if total_anomalias > 0 else "Zero Alertas"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-card-header">
                    <span class="kpi-title">Anomalias Críticas</span>
                    <div class="kpi-icon-wrap" style="background: {anomalia_bg}; color: {anomalia_cor};">🚨</div>
                </div>
                <div class="kpi-value" style="color: {anomalia_cor};">{total_anomalias:02d}</div>
                <div class="kpi-sub">
                    <span style="color: {anomalia_cor}; font-weight: 600;">{anomalia_texto}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-card-header">
                    <span class="kpi-title">Telemetrias Ingeridas</span>
                    <div class="kpi-icon-wrap" style="background: rgba(168, 85, 247, 0.15); color: #c084fc;">📡</div>
                </div>
                <div class="kpi-value">{total_leituras:,}</div>
                <div class="kpi-sub">
                    <span style="color: #c084fc;">●</span> Pontos Analisados
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)


def criar_gauge_saude(score: float, classificacao: str) -> go.Figure:
    """Cria um velocímetro/gauge moderno em Plotly Dark para o Health Score."""
    if score >= 75:
        cor_barra = "#10b981"
    elif score >= 50:
        cor_barra = "#f59e0b"
    else:
        cor_barra = "#ef4444"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={
                'suffix': "%",
                'font': {'size': 44, 'color': '#ffffff', 'family': 'JetBrains Mono, monospace'},
            },
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#334155", 'nticks': 6},
                'bar': {'color': cor_barra, 'thickness': 0.28},
                'bgcolor': "rgba(30, 41, 59, 0.5)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.12)"},
                    {'range': [50, 75], 'color': "rgba(245, 158, 11, 0.12)"},
                    {'range': [75, 100], 'color': "rgba(16, 185, 129, 0.12)"},
                ],
                'threshold': {
                    'line': {'color': "#ef4444", 'width': 2},
                    'thickness': 0.75,
                    'value': 50,
                },
            },
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
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
    df: pd.DataFrame, metrica: str, titulo: str, unidade: str, limite: float, cor_neon: str
) -> go.Figure:
    """Cria gráficos de linha Plotly de alta qualidade com gradientes e threshold."""
    fig = go.Figure()

    # Linha tracejada do Limite Crítico
    fig.add_hline(
        y=limite,
        line_dash="dash",
        line_color="#ef4444",
        line_width=1.5,
        annotation_text=f"Limite Crítico ({limite} {unidade})",
        annotation_position="top right",
        annotation_font=dict(color="#f87171", size=10, family="JetBrains Mono"),
    )

    # Conversão de cor HEX para RGBA para efeito de brilho suave
    r = int(cor_neon[1:3], 16)
    g = int(cor_neon[3:5], 16)
    b = int(cor_neon[5:7], 16)
    cor_fill = f"rgba({r}, {g}, {b}, 0.1)"

    # Traço da telemetria
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"] if "timestamp" in df.columns else list(range(len(df))),
            y=df[metrica],
            mode="lines+markers",
            name=f"{titulo} ({unidade})",
            line=dict(color=cor_neon, width=3, shape="spline"),
            marker=dict(size=6, color=cor_neon, symbol="circle"),
            fill="tozeroy",
            fillcolor=cor_fill,
            hovertemplate="<b>%{y:.2f} " + unidade + "</b><br>%{x}<extra></extra>",
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        hovermode="x unified",
        margin=dict(l=10, r=10, t=30, b=10),
        height=320,
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.04)",
            color="#64748b",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.04)",
            color="#64748b",
            tickfont=dict(size=10),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#94a3b8", size=11),
        ),
    )
    return fig


# -----------------------------------------------------------------------------
# Visão 1: Parque Fabril Consolidado
# -----------------------------------------------------------------------------
def renderizar_visao_parque(dados: dict, maquinas: list):
    """Exibe cards modernos para cada ativo da fábrica em grid visual."""
    st.markdown("### 🏭 Ativos Operacionais no Parque Fabril")
    st.caption("Visão consolidada em tempo real da saúde dos equipamentos industriais.")

    if not maquinas:
        st.info("Nenhuma máquina cadastrada no sistema. Adicione o primeiro equipamento no menu lateral.")
        return

    # Renderiza em Grid de 2 Colunas para visual Dribbble
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
                icone_status = "🟢 OPERAÇÃO NORMAL"
            elif status_m == "anomalia":
                pill_class = "status-pill-anomalia"
                icone_status = "🚨 ANOMALIA DETECTADA"
            else:
                pill_class = "status-pill-sem-dados"
                icone_status = "⚪ AGUARDANDO DADOS"

            ult_temp = f"{hist[-1]['temperatura']}°C" if hist else "—"
            ult_vib = f"{hist[-1]['vibracao']} mm/s" if hist else "—"
            ult_cons = f"{hist[-1]['consumo']} W" if hist else "—"

            cor_prog = "#10b981" if score >= 75 else ("#f59e0b" if score >= 50 else "#ef4444")

            st.markdown(
                f"""
                <div class="asset-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <div>
                            <span style="font-size: 0.78rem; font-weight: 700; color: #38bdf8; text-transform: uppercase;">ASSET #{id_m:02d}</span>
                            <h3 style="margin: 2px 0 0 0; font-size: 1.25rem; font-weight: 700; color: #ffffff;">{nome_m}</h3>
                        </div>
                        <span class="status-pill {pill_class}">{icone_status}</span>
                    </div>

                    <div style="margin: 14px 0 10px 0;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                            <span style="color: #94a3b8;">Health Score</span>
                            <span style="color: {cor_prog}; font-weight: 700; font-family: monospace;">{score}% ({saude['classificacao']})</span>
                        </div>
                        <div style="background: rgba(30, 41, 59, 0.8); height: 6px; border-radius: 9999px; overflow: hidden;">
                            <div style="background: {cor_prog}; width: {score}%; height: 100%; border-radius: 9999px;"></div>
                        </div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 14px; text-align: center;">
                        <div style="background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px;">
                            <div style="font-size: 0.7rem; color: #64748b; text-transform: uppercase;">Temp</div>
                            <div style="font-size: 0.95rem; font-weight: 700; color: #f8fafc; font-family: monospace;">{ult_temp}</div>
                        </div>
                        <div style="background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px;">
                            <div style="font-size: 0.7rem; color: #64748b; text-transform: uppercase;">Vibração</div>
                            <div style="font-size: 0.95rem; font-weight: 700; color: #f8fafc; font-family: monospace;">{ult_vib}</div>
                        </div>
                        <div style="background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px;">
                            <div style="font-size: 0.7rem; color: #64748b; text-transform: uppercase;">Carga</div>
                            <div style="font-size: 0.95rem; font-weight: 700; color: #f8fafc; font-family: monospace;">{ult_cons}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
    st.markdown("#### ⚡ Ações Globais de Telemetria")
    c_btn, c_txt = st.columns([1, 2])
    with c_btn:
        if st.button("📡 Disparar Ciclo de Leitura em Todo o Parque", use_container_width=True):
            for m in maquinas:
                registrar_leitura(dados, m["id"], gerar_anomalia=False)
            st.toast("Ciclo de medição concluído para todo o parque!", icon="✅")
            st.rerun()
    with c_txt:
        st.caption("Envio em massa de telemetria para validação de conectividade com todos os nós cadastrados.")


# -----------------------------------------------------------------------------
# Visão 2: Detalhes Aprofundados da Máquina Selecionada
# -----------------------------------------------------------------------------
def renderizar_detalhes_maquina(dados: dict, maquina: dict):
    """Visualização analítica completa de uma máquina específica."""
    id_m = maquina["id"]
    nome_m = maquina["nome"]
    historico = maquina.get("historico", [])
    status_m = maquina.get("status", "sem dados").lower()

    # Diagnóstico preditivo e Health Score
    diagnostico_texto = analisar_maquina(dados, id_m)
    saude = calcular_indice_saude(historico)
    score = saude["score"]

    if status_m == "normal":
        pill_class = "status-pill-normal"
        icone_status = "🟢 OPERAÇÃO NORMAL"
    elif status_m == "anomalia":
        pill_class = "status-pill-anomalia"
        icone_status = "🚨 ANOMALIA DETECTADA"
    else:
        pill_class = "status-pill-sem-dados"
        icone_status = "⚪ AGUARDANDO DADOS"

    # Header da Máquina
    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.markdown(
            f"""
            <div style="margin-bottom: 8px;">
                <span style="font-size: 0.8rem; font-weight: 700; color: #38bdf8; text-transform: uppercase;">ATIVO EM MONITORAMENTO CONTÍNUO</span>
                <h1 style="margin: 2px 0 0 0; font-size: 2.2rem; font-weight: 800; color: #ffffff;">{nome_m} <span style="font-size: 1.2rem; color: #64748b;">(ID #{id_m:02d})</span></h1>
                <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.9rem;">Telemetria amostrada a cada ciclo • Total de medições: <strong>{len(historico)} registros</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_head2:
        st.markdown(
            f"""
            <div style="text-align: right; margin-top: 18px;">
                <span class="status-pill {pill_class}">{icone_status}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # HERO SECTION: Velocímetro (Gauge) + Diagnóstico AI Preditivo
    col_gauge, col_ai = st.columns([1, 2])

    with col_gauge:
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 18px; padding: 12px; text-align: center;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.6px; margin-top: 6px;">Integridade do Ativo</div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(criar_gauge_saude(score, saude["classificacao"]), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_ai:
        st.markdown(
            f"""
            <div class="ai-diagnosis-card">
                <div class="ai-diagnosis-title">
                    <span>🧠</span>
                    <span>Motor Preditivo MetalSense • Diagnóstico de Campo</span>
                </div>
                <div class="ai-diagnosis-text">{diagnostico_texto}</div>
            """,
            unsafe_allow_html=True,
        )

        # Hipóteses Fisiomecânicas
        if saude.get("hipoteses"):
            st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
            for hip in saude["hipoteses"]:
                st.markdown(f"<span class='root-cause-tag'>⚠️ {hip}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Tendências de Variação
        tend = saude.get("tendencias", {})
        st.markdown(
            f"""
            <div style="display: flex; gap: 16px; margin-top: 16px; font-size: 0.85rem; color: #94a3b8;">
                <div>🌡️ Temp: <strong style="color: #ffffff;">{tend.get('temperatura', 'Estável')}</strong></div>
                <div>〰️ Vibração: <strong style="color: #ffffff;">{tend.get('vibracao', 'Estável')}</strong></div>
                <div>⚡ Carga: <strong style="color: #ffffff;">{tend.get('consumo', 'Estável')}</strong></div>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ÚLTIMA MEDIÇÃO EM CARDS ELEVADOS
    if historico:
        ult = historico[-1]
        t_val = ult.get("temperatura", 0.0)
        v_val = ult.get("vibracao", 0.0)
        c_val = ult.get("consumo", 0.0)
        hora = ult.get("timestamp", "—")

        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            t_status_cor = "#ef4444" if t_val > 85.0 else "#10b981"
            t_status_txt = "CRÍTICO (>85°C)" if t_val > 85.0 else "Normal (55-68°C)"
            st.markdown(
                f"""
                <div class="sensor-metric-box">
                    <div class="sensor-label">Temperatura Térmica</div>
                    <div class="sensor-val" style="color: {t_status_cor};">{t_val} °C</div>
                    <span class="sensor-badge" style="background: rgba(255,255,255,0.06); color: {t_status_cor};">{t_status_txt}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sc2:
            v_status_cor = "#ef4444" if v_val > 8.0 else "#10b981"
            v_status_txt = "EXCESSIVA (>8.0)" if v_val > 8.0 else "Normal (2-4.5)"
            st.markdown(
                f"""
                <div class="sensor-metric-box">
                    <div class="sensor-label">Vibração Mecânica</div>
                    <div class="sensor-val" style="color: {v_status_cor};">{v_val} <span style="font-size: 1rem;">mm/s</span></div>
                    <span class="sensor-badge" style="background: rgba(255,255,255,0.06); color: {v_status_cor};">{v_status_txt}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sc3:
            c_status_cor = "#ef4444" if c_val > 500.0 else "#10b981"
            c_status_txt = "SOBRECARGA (>500W)" if c_val > 500.0 else "Normal (250-380W)"
            st.markdown(
                f"""
                <div class="sensor-metric-box">
                    <div class="sensor-label">Consumo Elétrico</div>
                    <div class="sensor-val" style="color: {c_status_cor};">{c_val} <span style="font-size: 1rem;">W</span></div>
                    <span class="sensor-badge" style="background: rgba(255,255,255,0.06); color: {c_status_cor};">{c_status_txt}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sc4:
            st.markdown(
                f"""
                <div class="sensor-metric-box">
                    <div class="sensor-label">Último Timestamp</div>
                    <div class="sensor-val" style="font-size: 1.25rem; color: #38bdf8;">{hora.split(' ')[-1] if ' ' in hora else hora}</div>
                    <span class="sensor-badge" style="background: rgba(255,255,255,0.06); color: #94a3b8;">{hora.split(' ')[0] if ' ' in hora else 'Hoje'}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # CONTROLES & SIMULADOR DE FALHAS
    st.markdown("#### 🎮 Console de Telemetria & Simulação de Campo")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("🟢 Injetar Leitura Operacional Normal", use_container_width=True):
            registrar_leitura(dados, id_m, gerar_anomalia=False)
            st.toast("Leitura normal registrada!", icon="✅")
            st.rerun()
    with b2:
        if st.button("🚨 Injetar Pico Anômalo Aleatório", type="primary", use_container_width=True):
            registrar_leitura(dados, id_m, gerar_anomalia=True)
            st.toast("Pico de anomalia simulado!", icon="🚨")
            st.rerun()
    with b3:
        if st.button("🔄 Reavaliar Matriz Preditiva", use_container_width=True):
            analisar_maquina(dados, id_m)
            st.toast("Inferência preditiva atualizada!", icon="🔄")
            st.rerun()

    with st.expander("📡 Estúdio de Cenários Físicos Industriais", expanded=False):
        st.caption("Simule modos de falha reais para testes de causa-raiz e demonstrações da banca:")
        sb1, sb2, sb3 = st.columns(3)
        with sb1:
            if st.button("🔩 Desgaste Progressivo de Rolamento", use_container_width=True):
                leit = gerar_leitura_cenario("rolamento", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Cenário de Rolamento injetado!", icon="🔩")
                st.rerun()
        with sb2:
            if st.button("🔥 Falha do Sistema de Arrefecimento", use_container_width=True):
                leit = gerar_leitura_cenario("aquecimento", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Cenário Térmico injetado!", icon="🔥")
                st.rerun()
        with sb3:
            if st.button("⚡ Sobrecarga Severa do Motor", use_container_width=True):
                leit = gerar_leitura_cenario("sobrecarga", ciclo=len(historico) + 1)
                registrar_leitura(dados, id_m, leitura=leit)
                st.toast("Cenário de Sobrecarga injetado!", icon="⚡")
                st.rerun()

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # GRÁFICOS INTERATIVOS DARK
    st.markdown("#### 📈 Séries Temporais de Telemetria (Plotly Dark)")

    if len(historico) < 2:
        st.info("📊 Histórico com menos de 2 medições. Utilize os botões do console acima para gerar leituras.")
    else:
        df_hist = pd.DataFrame(historico)

        tab1, tab2, tab3, tab4 = st.tabs([
            "🌡️ Temperatura (°C)",
            "〰️ Vibração (mm/s)",
            "⚡ Consumo Elétrico (W)",
            "📊 Análise Multivariada",
        ])

        with tab1:
            st.plotly_chart(
                criar_grafico_telemetria(
                    df_hist, "temperatura", "Temperatura", "°C", 85.0, "#00f2fe"
                ),
                use_container_width=True,
            )
        with tab2:
            st.plotly_chart(
                criar_grafico_telemetria(
                    df_hist, "vibracao", "Vibração Mecânica", "mm/s", 8.0, "#f59e0b"
                ),
                use_container_width=True,
            )
        with tab3:
            st.plotly_chart(
                criar_grafico_telemetria(
                    df_hist, "consumo", "Carga Elétrica", "W", 500.0, "#a855f7"
                ),
                use_container_width=True,
            )
        with tab4:
            # Gráfico integrado normalizado
            fig_multi = go.Figure()
            for col, cor, nome in [
                ("temperatura", "#00f2fe", "Temp (°C)"),
                ("vibracao", "#f59e0b", "Vibração (mm/s)"),
                ("consumo", "#a855f7", "Consumo (W)"),
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
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15, 23, 42, 0.4)",
                hovermode="x unified",
                margin=dict(l=10, r=10, t=30, b=10),
                height=340,
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#64748b"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#64748b"),
            )
            st.plotly_chart(fig_multi, use_container_width=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # TABELA DE LOGS & AUDITORIA
    st.markdown("#### 📑 Log de Auditoria & Exportação de Laudos")
    if historico:
        with st.expander("Ver Tabela Detalhada e Exportar Laudo Técnico", expanded=False):
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
                    label="📥 Baixar Telemetria Completa (CSV)",
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
                    label="📄 Baixar Laudo Pericial de Manutenção (HTML)",
                    data=html_data,
                    file_name=f"laudo_metalsense_asset_{id_m}.html",
                    mime="text/html",
                    use_container_width=True,
                )

            st.markdown("##### 🛠️ Ordem de Serviço Emitida")
            st.code(gerar_ordem_servico_texto(maquina), language="text")


# -----------------------------------------------------------------------------
# Fluxo Principal & Sidebar
# -----------------------------------------------------------------------------
def main():
    dados = carregar_dados()
    maquinas = dados.get("maquinas", [])

    # Navbar Superior Dribbble
    renderizar_navbar()

    # Deck de Indicadores / KPIs
    renderizar_kpis_topo(maquinas)

    # SIDEBAR ELEGANTE
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="font-size: 1.4rem;">⚙️</span>
                <span style="font-size: 1.1rem; font-weight: 800; color: #ffffff;">METALSENSE</span>
            </div>
            <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 14px;">Centro de Controle Fabril</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 🎯 Ativo em Foco")
        opcoes = ["📊 Parque Fabril Completo (Visão Geral)"]
        mapa = {}
        for m in maquinas:
            tag = f"[#{m['id']:02d}] {m['nome']}"
            opcoes.append(tag)
            mapa[tag] = m

        escolha = st.selectbox(
            "Selecione para inspecionar:",
            options=opcoes,
            index=0,
            help="Alterne entre o panorama geral do parque e a telemetria detalhada de um equipamento.",
        )

        st.markdown("---")

        # Formulário de Cadastro
        st.markdown("#### ➕ Novo Ativo")
        with st.form("form_novo_ativo", clear_on_submit=True):
            nome_input = st.text_input("Identificador / Modelo:", placeholder="Ex: Torno CNC Mazak 04")
            btn_add = st.form_submit_button("Cadastrar Equipamento", use_container_width=True)

            if btn_add:
                nome_limpo = nome_input.strip()
                if not nome_limpo:
                    st.error("O identificador não pode ser vazio.")
                else:
                    try:
                        nova = criar_maquina(dados, nome_limpo)
                        st.toast(f"Máquina '{nova['nome']}' cadastrada!", icon="✅")
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

        # Exclusão se máquina selecionada
        maquina_ativa = mapa.get(escolha)
        if maquina_ativa:
            st.markdown("---")
            st.markdown("#### 🗑️ Descomissionar")
            with st.expander("Remover este ativo", expanded=False):
                st.caption(f"Atenção: removerá '{maquina_ativa['nome']}' e todo o seu histórico.")
                confirm = st.checkbox("Confirmo a exclusão", key=f"del_{maquina_ativa['id']}")
                if st.button("Remover Permanentemente", type="primary", disabled=not confirm, use_container_width=True):
                    if remover_maquina(dados, maquina_ativa["id"]):
                        st.toast("Ativo removido do parque!", icon="🗑️")
                        st.rerun()

        st.markdown("---")
        st.caption("MetalSense Pro v2.4 • TechForge Industrial")

    # Renderização da Área Principal
    if escolha == "📊 Parque Fabril Completo (Visão Geral)" or not maquina_ativa:
        renderizar_visao_parque(dados, maquinas)
    else:
        renderizar_detalhes_maquina(dados, maquina_ativa)


if __name__ == "__main__":
    main()
