"""
Controlador da Aplicação Desktop (Padrão MVC / Service-Controller).
Intermedeia eventos de UI, validações e disparo de Workers não-bloqueantes.
"""
from typing import Optional
from pathlib import Path

from desktop.services.telemetry_service import TelemetryService
from desktop.services.worker_service import AsyncWorker, LiveMonitoringWorker


class AppController:
    """Orquestra regras de negócio, serviços assíncronos e sincronização de views."""

    def __init__(self, service: TelemetryService):
        self.service = service
        self.window = None  # Injetado após instanciação da MainWindow
        self.live_worker: Optional[LiveMonitoringWorker] = None
        self.current_selected_machine_id: Optional[int] = None

    def set_view(self, window):
        """Associa a Janela Principal ao Controlador."""
        self.window = window

    # -------------------------------------------------------------------------
    # Métodos de Atualização Global
    # -------------------------------------------------------------------------
    def atualizar_dados_globais(self):
        """Carrega máquinas em background e atualiza todas as abas ativas."""
        def tarefa():
            return self.service.listar_maquinas()

        def sucesso(maquinas):
            # Garante execução na thread principal de GUI
            self.window.after(0, lambda: self._aplicar_dados_globais(maquinas))

        worker = AsyncWorker(target_fn=tarefa, on_success=sucesso)
        worker.start()

    def _aplicar_dados_globais(self, maquinas):
        if not self.window:
            return
        self.window.tab_dashboard.refresh(maquinas)
        self.window.tab_machines.refresh(maquinas)
        self.window.tab_telemetry.update_combo_options(maquinas, self.current_selected_machine_id)

    # -------------------------------------------------------------------------
    # Cadastro e Remoção de Máquinas (Operações Assíncronas Não-Bloqueantes)
    # -------------------------------------------------------------------------
    def cadastrar_maquina_async(self, nome: str):
        """Dispara cadastro seguro em background com feedback visual imediato."""
        self.window.set_busy_state(True, f"Cadastrando '{nome}'...")

        def tarefa():
            return self.service.cadastrar_maquina(nome)

        def sucesso(nova_maquina):
            self.window.after(0, lambda: self._on_cadastrar_sucesso(nova_maquina))

        def erro(ex):
            self.window.after(0, lambda: self._on_erro(f"Falha ao cadastrar: {ex}"))

        AsyncWorker(target_fn=tarefa, on_success=sucesso, on_error=erro).start()

    def _on_cadastrar_sucesso(self, nova_maquina):
        self.window.set_busy_state(False, f"✅ Máquina '{nova_maquina.nome}' cadastrada com sucesso! [ID #{nova_maquina.id}]")
        self.current_selected_machine_id = nova_maquina.id
        self.atualizar_dados_globais()

    def remover_maquina_async(self, id_maquina: int):
        """Remove a máquina em background e atualiza a UI."""
        self.window.set_busy_state(True, f"Removendo equipamento #{id_maquina}...")

        def tarefa():
            return self.service.remover_maquina(id_maquina)

        def sucesso(removido):
            self.window.after(0, lambda: self._on_remover_sucesso(removido, id_maquina))

        def erro(ex):
            self.window.after(0, lambda: self._on_erro(f"Erro ao remover máquina: {ex}"))

        AsyncWorker(target_fn=tarefa, on_success=sucesso, on_error=erro).start()

    def _on_remover_sucesso(self, removido: bool, id_maquina: int):
        self.window.set_busy_state(False)
        if removido:
            self.window.set_status_message(f"🗑️ Máquina ID #{id_maquina} removida do parque fabril.")
            if self.current_selected_machine_id == id_maquina:
                self.current_selected_machine_id = None
            self.atualizar_dados_globais()
        else:
            self.window.set_status_message(f"⚠️ Máquina ID #{id_maquina} não pôde ser encontrada.", is_error=True)

    # -------------------------------------------------------------------------
    # Operações de Telemetria e Diagnóstico Preditivo
    # -------------------------------------------------------------------------
    def selecionar_maquina_para_inspecao(self, id_maquina: int):
        """Navega da tela de Dashboard diretamente para a telemetria da máquina."""
        self.current_selected_machine_id = id_maquina
        self.window.navegar_para("telemetry")
        self.carregar_detalhes_maquina(id_maquina)

    def carregar_detalhes_maquina(self, id_maquina: int):
        """Carrega medições e diagnóstico preditivo para exibição na aba de telemetria."""
        self.current_selected_machine_id = id_maquina
        self.window.set_busy_state(True, "Processando inferência preditiva...")

        def tarefa():
            maq = self.service.obter_maquina_por_id(id_maquina)
            _, diag = self.service.analisar_maquina(id_maquina)
            return maq, diag

        def sucesso(res):
            maq, diag = res
            self.window.after(0, lambda: self._on_detalhes_carregados(maq, diag))

        def erro(ex):
            self.window.after(0, lambda: self._on_erro(f"Falha ao ler telemetria: {ex}"))

        AsyncWorker(target_fn=tarefa, on_success=sucesso, on_error=erro).start()

    def _on_detalhes_carregados(self, maquina, diagnostico):
        self.window.set_busy_state(False)
        if maquina:
            self.window.tab_telemetry.render_machine_data(maquina, diagnostico)
            self.window.set_status_message(f"Telemetria atualizada para '{maquina.nome}'.")

    def registrar_leitura_async(self, id_maquina: int, gerar_anomalia: bool = False):
        """Registra telemetria normal ou anomalia simulada sem congelar a tela."""
        tipo_msg = "anomalia de teste" if gerar_anomalia else "leitura normal"
        self.window.set_busy_state(True, f"Injetando {tipo_msg}...")

        def tarefa():
            leitura, status, diag = self.service.registrar_leitura(id_maquina, gerar_anomalia=gerar_anomalia)
            maq = self.service.obter_maquina_por_id(id_maquina)
            return leitura, status, diag, maq

        def sucesso(res):
            leitura, status, diag, maq = res
            self.window.after(0, lambda: self._on_leitura_registrada(leitura, status, diag, maq))

        def erro(ex):
            self.window.after(0, lambda: self._on_erro(f"Erro ao injetar telemetria: {ex}"))

        AsyncWorker(target_fn=tarefa, on_success=sucesso, on_error=erro).start()

    def _on_leitura_registrada(self, leitura, status, diag, maquina):
        self.window.set_busy_state(False)
        if maquina:
            self.window.tab_telemetry.render_machine_data(maquina, diag)
            icon = "🚨" if status == "anomalia" else "✅"
            self.window.set_status_message(f"{icon} Nova leitura gravada em {leitura.timestamp}. Status: {status.upper()}")
            # Sincroniza dashboards
            self.window.tab_dashboard.refresh(self.service.listar_maquinas())

    # -------------------------------------------------------------------------
    # Streaming Contínuo ao Vivo (Background Daemon)
    # -------------------------------------------------------------------------
    def iniciar_streaming_ao_vivo(self, id_maquina: int):
        """Inicia geração de dados a cada 2 segundos em thread daemon independente."""
        self.parar_streaming_ao_vivo()

        def tarefa_tick():
            leitura, status, diag = self.service.registrar_leitura(id_maquina, gerar_anomalia=False)
            maq = self.service.obter_maquina_por_id(id_maquina)
            return leitura, status, diag, maq

        def on_tick(res):
            leitura, status, diag, maq = res
            self.window.after(0, lambda: self._on_tick_streaming(leitura, status, diag, maq))

        self.live_worker = LiveMonitoringWorker(task_callback=tarefa_tick, interval_seconds=2.0, on_tick=on_tick)
        self.live_worker.start()
        self.window.set_status_message(f"📡 Monitoramento contínuo em tempo real ATIVO (ID #{id_maquina}).")

    def _on_tick_streaming(self, leitura, status, diag, maquina):
        if maquina and self.current_selected_machine_id == maquina.id:
            self.window.tab_telemetry.render_machine_data(maquina, diag)
            self.window.set_status_message(f"📡 Sinal recebido às {leitura.timestamp} | Status: {status.upper()}")

    def parar_streaming_ao_vivo(self):
        """Interrompe o worker de streaming."""
        if self.live_worker and self.live_worker.is_running():
            self.live_worker.stop()
            self.live_worker = None
            self.window.set_status_message("⏹️ Monitoramento contínuo encerrado.")

    # -------------------------------------------------------------------------
    # Exportação de Dados
    # -------------------------------------------------------------------------
    def exportar_csv_async(self, id_maquina: int, caminho: Path):
        """Exporta CSV de medições em background."""
        self.window.set_busy_state(True, "Exportando arquivo CSV...")

        def tarefa():
            return self.service.exportar_relatorio_csv(id_maquina, caminho)

        def sucesso(ok):
            self.window.after(0, lambda: self._on_exportar_sucesso(ok, caminho))

        def erro(ex):
            self.window.after(0, lambda: self._on_erro(f"Erro na exportação: {ex}"))

        AsyncWorker(target_fn=tarefa, on_success=sucesso, on_error=erro).start()

    def _on_exportar_sucesso(self, ok: bool, caminho: Path):
        self.window.set_busy_state(False)
        if ok:
            self.window.set_status_message(f"📁 Arquivo exportado com sucesso: {caminho.name}")
        else:
            self.window.set_status_message("⚠️ Não há dados suficientes para exportar.", is_error=True)

    def _on_erro(self, msg: str):
        self.window.set_busy_state(False)
        self.window.set_status_message(f"❌ {msg}", is_error=True)
