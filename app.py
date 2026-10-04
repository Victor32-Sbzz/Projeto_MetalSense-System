import streamlit as st
from datetime import datetime

from dados import carregar_dados, salvar_dados
from maquinas import (
    criar_maquina,
    remover_maquina,
    simular_leitura,
    registrar_leitura,
    analisar_maquina,
)
from analytics import calcular_indice_saude
from relatorios import exportar_historico_csv, gerar_relatorio_html, gerar_ordem_servico_texto
from simulador_iot import gerar_leitura_cenario, CENARIOS

# -----------------------------------------------------------------------------
# Configuração da Página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MetalSense - Monitoramento Industrial",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Estilos CSS Personalizados para Identidade Visual Industrial (TechForge)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Estilos Gerais */
    .techforge-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        color: #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .techforge-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #f8fafc;
    }
    .techforge-header p {
        margin: 6px 0 0 0;
        font-size: 1rem;
        color: #94a3b8;
    }
    .techforge-badge-techforge {
        background-color: #3b82f6;
        color: #ffffff;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 8px;
    }

    /* Cards de Métricas e KPIs */
    .kpi-container {
        display: flex;
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        flex: 1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-title {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }

    /* Badges de Status da Máquina */
    .status-badge {
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .status-normal {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #86efac;
    }
    .status-anomalia {
        background-color: #fee2e2;
        color: #b91c1c;
        border: 1px solid #fca5a5;
        animation: pulse 2s infinite;
    }
    .status-sem-dados {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
    }

    /* Card de Diagnóstico */
    .diag-box {
        padding: 16px 20px;
        border-radius: 10px;
        margin-top: 14px;
        margin-bottom: 18px;
        font-size: 0.98rem;
        line-height: 1.5;
    }
    .diag-normal {
        background-color: #f0fdf4;
        border-left: 5px solid #22c55e;
        color: #166534;
    }
    .diag-anomalia {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        color: #991b1b;
    }
    .diag-sem-dados {
        background-color: #f8fafc;
        border-left: 5px solid #94a3b8;
        color: #334155;
    }

    /* Card de Máquina */
    .machine-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def obter_rotulo_status(status: str) -> tuple:
    """Retorna classe CSS, ícone e texto formatado do status."""
    st_limpo = (status or "sem dados").lower().strip()
    if st_limpo == "normal":
        return "status-normal", "diag-normal", "🟢", "Operação Normal"
    elif st_limpo == "anomalia":
        return "status-anomalia", "diag-anomalia", "🚨", "Anomalia Detectada"
    else:
        return "status-sem-dados", "diag-sem-dados", "⚪", "Sem Dados / Aguardando Medições"


def renderizar_cabecalho():
    """Renderiza o cabeçalho oficial MetalSense / TechForge."""
    st.markdown(
        """
        <div class="techforge-header">
            <span class="techforge-badge-techforge">Grupo TechForge • Indústria 4.0</span>
            <h1>⚙️ MetalSense — Sistema de Monitoramento Preditivo</h1>
            <p>Plataforma inteligente de telemetria industrial para detecção antecipada de falhas em máquinas operacionais.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_kpis_gerais(maquinas: list):
    """Renderiza o painel superior de indicadores operacionais (KPIs)."""
    total_maquinas = len(maquinas)
    total_normais = sum(1 for m in maquinas if m.get("status") == "normal")
    total_anomalias = sum(1 for m in maquinas if m.get("status") == "anomalia")
    total_sem_dados = sum(1 for m in maquinas if m.get("status") not in ["normal", "anomalia"])
    total_leituras = sum(len(m.get("historico", [])) for m in maquinas)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total de Máquinas",
            value=total_maquinas,
            help="Total de equipamentos cadastrados no parque fabril",
        )
    with col2:
        st.metric(
            label="Operação Normal",
            value=total_normais,
            delta=f"{(total_normais/total_maquinas*100):.0f}% do parque" if total_maquinas else None,
            delta_color="normal",
            help="Equipamentos operando dentro dos parâmetros especificados",
        )
    with col3:
        st.metric(
            label="Em Anomalia",
            value=total_anomalias,
            delta=f"{total_anomalias} alerta(s)" if total_anomalias > 0 else "0 alertas",
            delta_color="inverse" if total_anomalias > 0 else "normal",
            help="Equipamentos com temperatura, vibração ou consumo fora do limite",
        )
    with col4:
        st.metric(
            label="Total de Leituras",
            value=total_leituras,
            help="Volume total de medições de telemetria coletadas",
        )


def renderizar_visao_geral(dados: dict, maquinas: list):
    """Exibe o painel consolidado com a lista de todas as máquinas cadastradas."""
    st.markdown("### 📋 Parque Fabril — Visão Consolidada")

    if not maquinas:
        st.info("Nenhuma máquina cadastrada no sistema. Utilize o menu lateral para adicionar a primeira máquina.")
        return

    # Tabela consolidada de resumo
    resumo_lista = []
    for m in maquinas:
        hist = m.get("historico", [])
        ult_temp = "-"
        ult_vib = "-"
        ult_cons = "-"
        ult_data = "Sem leituras"

        if hist:
            ult = hist[-1]
            ult_temp = f"{ult.get('temperatura', '-')} °C"
            ult_vib = f"{ult.get('vibracao', '-')} mm/s"
            ult_cons = f"{ult.get('consumo', '-')} W"
            ult_data = ult.get("timestamp", "-")

        status_raw = m.get("status", "sem dados")
        _, _, icone, rotulo = obter_rotulo_status(status_raw)

        resumo_lista.append({
            "ID": m.get("id"),
            "Máquina": m.get("nome"),
            "Status Operacional": f"{icone} {rotulo}",
            "Total Medições": len(hist),
            "Última Temperatura": ult_temp,
            "Última Vibração": ult_vib,
            "Último Consumo": ult_cons,
            "Última Atualização": ult_data,
        })

    # Renderiza tabela elegante
    try:
        import pandas as pd
        df_resumo = pd.DataFrame(resumo_lista)
        st.dataframe(df_resumo, use_container_width=True, hide_index=True)
    except Exception:
        st.table(resumo_lista)

    st.markdown("---")
    st.markdown("#### ⚡ Ações Rápidas em Lote")
    col_sim_todos, col_info = st.columns([1, 2])
    with col_sim_todos:
        if st.button("📡 Coletar Leitura Normal em Todas as Máquinas", use_container_width=True):
            for m in maquinas:
                registrar_leitura(dados, m["id"], gerar_anomalia=False)
            st.toast("Leituras coletadas para todas as máquinas!", icon="✅")
            st.rerun()
    with col_info:
        st.caption("Dica: Selecione uma máquina específica na barra lateral esquerda para visualizar diagnósticos detalhados, simulações pontuais e histórico gráfico de telemetria.")


def renderizar_detalhes_maquina(dados: dict, maquina: dict):
    """Renderiza a visualização aprofundada, diagnósticos, gráficos e ações da máquina selecionada."""
    id_maq = maquina.get("id")
    nome_maq = maquina.get("nome")
    historico = maquina.get("historico", [])

    # Executa a análise preditiva pura do MetalSense e calcula Health Score
    diagnostico_texto = analisar_maquina(dados, id_maq)
    saude = calcular_indice_saude(historico)
    status_atual = maquina.get("status", "sem dados")
    css_status, css_diag, icone, rotulo_status = obter_rotulo_status(status_atual)

    # Topo do detalhe da máquina com Health Score
    col_titulo, col_score, col_status = st.columns([3, 2, 2])
    with col_titulo:
        st.markdown(f"## 🏭 {nome_maq} <span style='font-size: 1.1rem; color: #64748b;'>(ID #{id_maq})</span>", unsafe_allow_html=True)
        st.caption(f"Equipamento monitorado continuamente • Total de registros: **{len(historico)} medição(ões)**")
    
    with col_score:
        st.metric(
            label="Health Score (Saúde do Ativo)",
            value=f"{saude['score']}%",
            delta=saude['classificacao'],
            delta_color="normal" if saude['score'] >= 70 else "inverse",
            help="Índice preditivo de integridade do equipamento baseado em volatilidade e desvios"
        )

    with col_status:
        st.markdown(
            f"""
            <div style="text-align: right; margin-top: 10px;">
                <span class="status-badge {css_status}">
                    {icone} {rotulo_status}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Painel de Diagnóstico Preditivo
    st.markdown(
        f"""
        <div class="diag-box {css_diag}">
            <strong>🧠 Diagnóstico Preditivo MetalSense:</strong><br>
            {diagnostico_texto}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hipóteses de Falha Mecânica (se houver)
    if saude.get("hipoteses"):
        st.error("⚠️ **Alertas de Causa-Raiz Mecânica / Elétrica:**\n- " + "\n- ".join(saude["hipoteses"]))

    # Painel de Ações Rápidas (Simulação de Telemetria)
    st.markdown("#### 🎮 Painel de Ações e Simulação de Telemetria")
    col_act1, col_act2, col_act3 = st.columns([1, 1, 1])

    with col_act1:
        if st.button("🟢 Simular Leitura Normal", use_container_width=True, help="Injeta uma leitura dentro da faixa operacional padrão"):
            res = registrar_leitura(dados, id_maq, gerar_anomalia=False)
            st.toast("Leitura normal registrada com sucesso!", icon="✅")
            st.rerun()

    with col_act2:
        if st.button("⚠️ Simular Anomalia (Teste)", use_container_width=True, type="primary", help="Injeta picos anômalos de temperatura, vibração ou consumo elétrico"):
            res = registrar_leitura(dados, id_maq, gerar_anomalia=True)
            st.toast("Pico anômalo simulado!", icon="🚨")
            st.rerun()

    with col_act3:
        if st.button("🔄 Reavaliar Diagnóstico", use_container_width=True, help="Executa novamente o motor de inferência preditiva"):
            analisar_maquina(dados, id_maq)
            st.toast("Análise preditiva atualizada!", icon="🔄")
            st.rerun()

    # Expander de Injeção de Falhas Específicas IoT
    with st.expander("📡 Simulador Avançado de Cenários de Falha IoT", expanded=False):
        st.caption("Gere simulações de desgaste real para testar os algoritmos de causa-raiz:")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            if st.button("🔩 Desgaste de Rolamento", use_container_width=True):
                leit = gerar_leitura_cenario("rolamento", ciclo=len(historico)+1)
                registrar_leitura(dados, id_maq, leitura=leit)
                st.toast("Cenário de Desgaste de Rolamento injetado!", icon="🔩")
                st.rerun()
        with sc2:
            if st.button("🔥 Superaquecimento Térmico", use_container_width=True):
                leit = gerar_leitura_cenario("aquecimento", ciclo=len(historico)+1)
                registrar_leitura(dados, id_maq, leitura=leit)
                st.toast("Cenário de Superaquecimento injetado!", icon="🔥")
                st.rerun()
        with sc3:
            if st.button("⚡ Sobrecarga Elétrica", use_container_width=True):
                leit = gerar_leitura_cenario("sobrecarga", ciclo=len(historico)+1)
                registrar_leitura(dados, id_maq, leitura=leit)
                st.toast("Cenário de Sobrecarga Elétrica injetado!", icon="⚡")
                st.rerun()

    st.markdown("---")

    # Indicadores da Última Medição
    if historico:
        ultima_medicao = historico[-1]
        st.markdown("#### ⏱️ Última Medição Registrada")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        temp_val = ultima_medicao.get("temperatura", 0.0)
        vib_val = ultima_medicao.get("vibracao", 0.0)
        cons_val = ultima_medicao.get("consumo", 0.0)
        time_val = ultima_medicao.get("timestamp", "-")

        with m_col1:
            st.metric(
                label="Temperatura",
                value=f"{temp_val} °C",
                delta="CRÍTICO (>85°C)" if temp_val > 85.0 else "Normal (55-68°C)",
                delta_color="inverse" if temp_val > 85.0 else "normal",
            )
        with m_col2:
            st.metric(
                label="Vibração",
                value=f"{vib_val} mm/s",
                delta="EXCESSIVA (>8 mm/s)" if vib_val > 8.0 else "Normal (2-4.5 mm/s)",
                delta_color="inverse" if vib_val > 8.0 else "normal",
            )
        with m_col3:
            st.metric(
                label="Consumo Elétrico",
                value=f"{cons_val} W",
                delta="SOBRECARGA (>500W)" if cons_val > 500.0 else "Normal (250-380W)",
                delta_color="inverse" if cons_val > 500.0 else "normal",
            )
        with m_col4:
            st.metric(
                label="Horário da Leitura",
                value=time_val.split(" ")[-1] if " " in time_val else time_val,
                help=f"Data completa: {time_val}",
            )
    else:
        st.info("ℹ️ Esta máquina ainda não possui medições de telemetria. Utilize os botões acima para simular a primeira leitura.")

    st.markdown("---")

    # Gráficos Temporais de Telemetria
    st.markdown("#### 📈 Histórico Temporal de Telemetria")

    if len(historico) < 2:
        st.info("📊 Histórico insuficiente para renderizar gráficos temporais (necessário no mínimo 2 medições). Utilize os botões de simulação acima para registrar leituras consecutivas.")
    else:
        # Prepara dados para os gráficos com suporte elegante a pandas e fallback nativo
        usou_pandas = False
        df_telemetria = None
        try:
            import pandas as pd
            df_telemetria = pd.DataFrame(historico)
            if "timestamp" in df_telemetria.columns:
                df_telemetria["Data/Hora"] = pd.to_datetime(df_telemetria["timestamp"], errors="coerce")
                df_telemetria = df_telemetria.sort_values(by="Data/Hora")
                df_plot = df_telemetria.copy().set_index("Data/Hora")
            else:
                df_plot = df_telemetria.copy()
            usou_pandas = True
        except Exception:
            usou_pandas = False

        tab1, tab2, tab3, tab4 = st.tabs([
            "🌡️ Temperatura (°C)",
            "〰️ Vibração (mm/s)",
            "⚡ Consumo Elétrico (W)",
            "📊 Visão Integrada",
        ])

        with tab1:
            st.caption("Limite operacional seguro: ≤ 85.0 °C")
            if usou_pandas and df_telemetria is not None:
                st.line_chart(df_plot[["temperatura"]], color="#ef4444")
            else:
                st.line_chart({"Temperatura (°C)": [x["temperatura"] for x in historico]})

        with tab2:
            st.caption("Limite operacional seguro: ≤ 8.0 mm/s")
            if usou_pandas and df_telemetria is not None:
                st.line_chart(df_plot[["vibracao"]], color="#f59e0b")
            else:
                st.line_chart({"Vibração (mm/s)": [x["vibracao"] for x in historico]})

        with tab3:
            st.caption("Limite operacional seguro: ≤ 500.0 W")
            if usou_pandas and df_telemetria is not None:
                st.line_chart(df_plot[["consumo"]], color="#3b82f6")
            else:
                st.line_chart({"Consumo (W)": [x["consumo"] for x in historico]})

        with tab4:
            st.caption("Normalização relativa das grandezas industriais")
            if usou_pandas and df_telemetria is not None:
                st.line_chart(df_plot[["temperatura", "vibracao", "consumo"]])
            else:
                st.line_chart({
                    "temperatura": [x["temperatura"] for x in historico],
                    "vibracao": [x["vibracao"] for x in historico],
                    "consumo": [x["consumo"] for x in historico],
                })

    st.markdown("---")

    # Tabela Detalhada com as Últimas Leituras
    st.markdown("#### 📑 Registro Detalhado das Medições")
    if historico:
        # Exibe em ordem decrescente (mais recente primeiro)
        leituras_ordenadas = list(reversed(historico))
        leituras_tabela = []

        for idx, item in enumerate(leituras_ordenadas):
            t = item.get("temperatura", 0.0)
            v = item.get("vibracao", 0.0)
            c = item.get("consumo", 0.0)

            anomalias_detectadas = []
            if t > 85.0:
                anomalias_detectadas.append("🔥 Temp Crítica")
            if v > 8.0:
                anomalias_detectadas.append("⚠️ Vibração Alta")
            if c > 500.0:
                anomalias_detectadas.append("⚡ Consumo Alto")

            status_item = "🟢 Normal" if not anomalias_detectadas else f"🚨 {', '.join(anomalias_detectadas)}"

            leituras_tabela.append({
                "Nº": len(historico) - idx,
                "Timestamp": item.get("timestamp", "-"),
                "Temperatura (°C)": f"{t:.2f}",
                "Vibração (mm/s)": f"{v:.2f}",
                "Consumo (W)": f"{c:.2f}",
                "Status da Leitura": status_item,
            })

        try:
            import pandas as pd
            df_hist = pd.DataFrame(leituras_tabela)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        except Exception:
            st.table(leituras_tabela)

        # Seção de Auditoria e Exportação de Relatórios
        st.markdown("---")
        st.markdown("#### 📑 Auditoria Técnica & Exportação de Laudos")
        with st.expander("Gerar e Baixar Relatórios Técnicos", expanded=False):
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                import io, csv
                csv_buffer = io.StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=["timestamp", "temperatura", "vibracao", "consumo"])
                writer.writeheader()
                for r in historico:
                    writer.writerow({
                        "timestamp": r.get("timestamp", ""),
                        "temperatura": r.get("temperatura", 0.0),
                        "vibracao": r.get("vibracao", 0.0),
                        "consumo": r.get("consumo", 0.0)
                    })
                st.download_button(
                    label="📥 Baixar Telemetria (CSV)",
                    data=csv_buffer.getvalue(),
                    file_name=f"metalsense_telemetria_maquina_{id_maq}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with exp_col2:
                caminho_html = gerar_relatorio_html(maquina)
                with open(caminho_html, "r", encoding="utf-8") as f_html:
                    html_data = f_html.read()
                st.download_button(
                    label="📄 Baixar Laudo de Auditoria (HTML)",
                    data=html_data,
                    file_name=f"laudo_metalsense_maquina_{id_maq}.html",
                    mime="text/html",
                    use_container_width=True
                )
            st.markdown("##### 🛠️ Ordem de Serviço de Manutenção Preditiva")
            st.code(gerar_ordem_servico_texto(maquina), language="text")
    else:
        st.info("Nenhuma leitura arquivada no histórico desta máquina.")


def main():
    # Carrega dados do sistema
    dados = carregar_dados()
    maquinas = dados.get("maquinas", [])

    # Cabeçalho Principal
    renderizar_cabecalho()

    # Painel de KPIs no Topo
    renderizar_kpis_gerais(maquinas)

    # -------------------------------------------------------------------------
    # Barra Lateral (Sidebar)
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("### 🏭 MetalSense")
        st.caption("Controle Operacional TechForge")
        st.markdown("---")

        # Seleção de Máquina ou Visão Geral
        st.markdown("#### 🎯 Seleção de Equipamento")
        opcoes_navegacao = ["📊 Visão Geral de Todas as Máquinas"]
        mapa_maquinas = {}
        for m in maquinas:
            label = f"[ID {m['id']}] {m['nome']}"
            opcoes_navegacao.append(label)
            mapa_maquinas[label] = m

        escolha_navegacao = st.selectbox(
            "Visualizar:",
            options=opcoes_navegacao,
            index=0,
            help="Alterne entre o panorama geral do parque fabril e a análise individual de cada máquina.",
        )

        st.markdown("---")

        # Cadastro de Nova Máquina
        st.markdown("#### ➕ Nova Máquina")
        with st.form("form_nova_maquina", clear_on_submit=True):
            nome_input = st.text_input("Nome / Identificador:", placeholder="Ex: Prensa Hidráulica 03")
            btn_adicionar = st.form_submit_button("Cadastrar Máquina", use_container_width=True)

            if btn_adicionar:
                nome_limpo = nome_input.strip()
                if not nome_limpo:
                    st.error("O nome da máquina não pode ser vazio.")
                else:
                    try:
                        nova = criar_maquina(dados, nome_limpo)
                        st.success(f"Máquina '{nova['nome']}' cadastrada com sucesso!")
                        st.rerun()
                    except ValueError as err:
                        st.error(str(err))

        st.markdown("---")

        # Exclusão da Máquina Selecionada (se houver uma máquina específica em foco)
        maquina_selecionada = mapa_maquinas.get(escolha_navegacao)
        if maquina_selecionada:
            st.markdown("#### 🗑️ Exclusão de Máquina")
            with st.expander("Gerenciar Exclusão", expanded=False):
                st.warning(f"Atenção: removerá a máquina '{maquina_selecionada['nome']}' e todo seu histórico.")
                confirmado = st.checkbox(
                    "Confirmo a exclusão definitiva",
                    key=f"check_del_{maquina_selecionada['id']}",
                )
                if st.button("Excluir Máquina", type="primary", disabled=not confirmado, use_container_width=True):
                    id_remover = maquina_selecionada["id"]
                    if remover_maquina(dados, id_remover):
                        st.success(f"Máquina removida com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao tentar remover a máquina.")

        st.markdown("---")
        st.caption("MetalSense v2.0 • TechForge Industrial Solutions")

    # -------------------------------------------------------------------------
    # Área Principal de Conteúdo
    # -------------------------------------------------------------------------
    if escolha_navegacao == "📊 Visão Geral de Todas as Máquinas" or not maquina_selecionada:
        renderizar_visao_geral(dados, maquinas)
    else:
        renderizar_detalhes_maquina(dados, maquina_selecionada)


if __name__ == "__main__":
    main()
