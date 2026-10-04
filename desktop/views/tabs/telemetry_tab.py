"""
Aba de Telemetria e Monitoramento Preditivo em Tempo Real com Gráficos.
"""
import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from typing import Optional

from desktop.config import THEME_COLORS, LIMITES_OPERACIONAIS
from desktop.views.components.status_badge import StatusBadge

# Tentativa de import do Matplotlib para integração gráfica nativa
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False


class TelemetryTab(ctk.CTkFrame):
    """Monitoramento contínuo, injeção de falhas, laudo preditivo e gráficos temporais."""

    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self.selected_machine_id: Optional[int] = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_ui()

    def _build_ui(self):
        # 1. Barra Superior: Seletor de Máquina e Controles de Ação
        top_bar = ctk.CTkFrame(self, fg_color=THEME_COLORS["bg_card"], corner_radius=10, border_width=1, border_color=THEME_COLORS["border"])
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        top_bar.grid_columnconfigure(1, weight=1)

        # Seletor
        ctk.CTkLabel(top_bar, text="Equipamento em Foco:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(15, 5), pady=12, sticky="w")
        
        self.combo_machines = ctk.CTkComboBox(
            top_bar,
            values=["Nenhuma máquina"],
            width=240,
            command=self._on_machine_selected,
        )
        self.combo_machines.grid(row=0, column=1, padx=5, pady=12, sticky="w")

        # Status Badge
        self.badge_status = StatusBadge(top_bar, status="sem dados")
        self.badge_status.grid(row=0, column=2, padx=15, pady=12, sticky="e")

        # 2. Painel de Diagnóstico e Ações Rápidas
        actions_panel = ctk.CTkFrame(self, fg_color=THEME_COLORS["bg_card"], corner_radius=10, border_width=1, border_color=THEME_COLORS["border"])
        actions_panel.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        actions_panel.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Caixa de Diagnóstico Preditivo
        self.diag_frame = ctk.CTkFrame(actions_panel, fg_color=THEME_COLORS["bg_card_alt"], corner_radius=8)
        self.diag_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=15, pady=(12, 10))
        self.diag_frame.grid_columnconfigure(0, weight=1)

        self.lbl_diag_title = ctk.CTkLabel(
            self.diag_frame,
            text="🧠 LAUDO DO MOTOR PREDITIVO METALSENSE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["accent_blue"],
        )
        self.lbl_diag_title.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))

        self.lbl_diagnostico = ctk.CTkLabel(
            self.diag_frame,
            text="Selecione uma máquina para carregar o laudo de telemetria.",
            font=ctk.CTkFont(size=13),
            text_color=THEME_COLORS["text_primary"],
            wraplength=900,
            justify="left",
        )
        self.lbl_diagnostico.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

        # Botões de Ação
        self.btn_simular_normal = ctk.CTkButton(
            actions_panel,
            text="🟢 Simular Leitura Normal",
            fg_color=THEME_COLORS["status_normal"],
            font=ctk.CTkFont(weight="bold"),
            command=self._on_simular_normal_click,
        )
        self.btn_simular_normal.grid(row=1, column=0, padx=(15, 6), pady=(0, 12), sticky="ew")

        self.btn_simular_anomalia = ctk.CTkButton(
            actions_panel,
            text="⚠️ Simular Anomalia (Teste)",
            fg_color=THEME_COLORS["status_anomaly"],
            font=ctk.CTkFont(weight="bold"),
            command=self._on_simular_anomalia_click,
        )
        self.btn_simular_anomalia.grid(row=1, column=1, padx=6, pady=(0, 12), sticky="ew")

        self.btn_live_monitor = ctk.CTkButton(
            actions_panel,
            text="📡 Iniciar Streaming Contínuo",
            fg_color=THEME_COLORS["accent_blue"],
            command=self._on_toggle_live_monitor,
        )
        self.btn_live_monitor.grid(row=1, column=2, padx=6, pady=(0, 12), sticky="ew")

        self.btn_exportar = ctk.CTkButton(
            actions_panel,
            text="📥 Exportar CSV",
            fg_color=THEME_COLORS["bg_card_alt"],
            command=self._on_exportar_csv_click,
        )
        self.btn_exportar.grid(row=1, column=3, padx=(6, 15), pady=(0, 12), sticky="ew")

        # 3. Área de Gráficos e Histórico
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        main_content.grid_columnconfigure(0, weight=3)
        main_content.grid_columnconfigure(1, weight=2)
        main_content.grid_rowconfigure(0, weight=1)

        # Lado Esquerdo: Área Gráfica
        self.graph_container = ctk.CTkFrame(main_content, fg_color=THEME_COLORS["bg_card"], corner_radius=10, border_width=1, border_color=THEME_COLORS["border"])
        self.graph_container.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        self.graph_container.grid_columnconfigure(0, weight=1)
        self.graph_container.grid_rowconfigure(1, weight=1)

        lbl_graph = ctk.CTkLabel(self.graph_container, text="Evolução Temporal dos Sensores", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_graph.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self.canvas_area = ctk.CTkFrame(self.graph_container, fg_color=THEME_COLORS["bg_card_alt"], corner_radius=8)
        self.canvas_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Lado Direito: Tabela / Histórico Recente
        self.table_container = ctk.CTkFrame(main_content, fg_color=THEME_COLORS["bg_card"], corner_radius=10, border_width=1, border_color=THEME_COLORS["border"])
        self.table_container.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)

        lbl_tbl = ctk.CTkLabel(self.table_container, text="Últimas Medições Registradas", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_tbl.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self.scroll_readings = ctk.CTkScrollableFrame(self.table_container, fg_color="transparent")
        self.scroll_readings.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_readings.grid_columnconfigure(0, weight=1)

        # Variáveis de monitoramento ao vivo
        self.is_monitoring_live = False
        self.matplotlib_canvas = None

    def _on_machine_selected(self, choice: str):
        if not choice or choice == "Nenhuma máquina":
            return
        try:
            # Formato: "[ID #1] Nome da Maquina"
            id_str = choice.split("]")[0].replace("[ID #", "").strip()
            mid = int(id_str)
            self.selected_machine_id = mid
            self.controller.carregar_detalhes_maquina(mid)
        except Exception:
            pass

    def _on_simular_normal_click(self):
        if self.selected_machine_id:
            self.controller.registrar_leitura_async(self.selected_machine_id, gerar_anomalia=False)

    def _on_simular_anomalia_click(self):
        if self.selected_machine_id:
            self.controller.registrar_leitura_async(self.selected_machine_id, gerar_anomalia=True)

    def _on_toggle_live_monitor(self):
        if not self.selected_machine_id:
            return

        if not self.is_monitoring_live:
            self.is_monitoring_live = True
            self.btn_live_monitor.configure(text="🛑 Parar Streaming", fg_color=THEME_COLORS["status_anomaly"])
            self.controller.iniciar_streaming_ao_vivo(self.selected_machine_id)
        else:
            self.is_monitoring_live = False
            self.btn_live_monitor.configure(text="📡 Iniciar Streaming Contínuo", fg_color=THEME_COLORS["accent_blue"])
            self.controller.parar_streaming_ao_vivo()

    def _on_exportar_csv_click(self):
        if not self.selected_machine_id:
            return
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv")],
            title="Salvar Histórico de Telemetria",
        )
        if caminho:
            self.controller.exportar_csv_async(self.selected_machine_id, Path(caminho))

    def update_combo_options(self, maquinas: list, selected_id: Optional[int] = None):
        options = [f"[ID #{m.id}] {m.nome}" for m in maquinas]
        if not options:
            options = ["Nenhuma máquina"]
        self.combo_machines.configure(values=options)

        if selected_id:
            for opt in options:
                if f"#{selected_id}]" in opt:
                    self.combo_machines.set(opt)
                    self.selected_machine_id = selected_id
                    break
        elif options and options[0] != "Nenhuma máquina" and not self.selected_machine_id:
            self.combo_machines.set(options[0])
            self._on_machine_selected(options[0])

    def render_machine_data(self, maquina, diagnostico_texto: str):
        self.selected_machine_id = maquina.id
        self.badge_status.set_status(maquina.status)
        self.lbl_diagnostico.configure(text=diagnostico_texto)

        # Atualiza tabela de últimas leituras
        for w in self.scroll_readings.winfo_children():
            w.destroy()

        leituras = list(reversed(maquina.historico))[:25]
        if not leituras:
            lbl_vazio = ctk.CTkLabel(self.scroll_readings, text="Nenhuma leitura registrada.", text_color=THEME_COLORS["text_secondary"])
            lbl_vazio.pack(pady=20)
        else:
            for l in leituras:
                row = ctk.CTkFrame(self.scroll_readings, fg_color=THEME_COLORS["bg_card_alt"], corner_radius=6)
                row.pack(fill="x", pady=2)
                row.grid_columnconfigure(0, weight=1)

                is_anomalo = (
                    l.temperatura > LIMITES_OPERACIONAIS["temperatura_max"]
                    or l.vibracao > LIMITES_OPERACIONAIS["vibracao_max"]
                    or l.consumo > LIMITES_OPERACIONAIS["consumo_max"]
                )

                txt_status = "⚠️ ANOMALIA" if is_anomalo else "🟢 NORMAL"
                cor_status = THEME_COLORS["status_anomaly"] if is_anomalo else THEME_COLORS["status_normal"]

                lbl_info = ctk.CTkLabel(
                    row,
                    text=f"{l.timestamp.split(' ')[-1]} | T: {l.temperatura}°C | V: {l.vibracao}mm/s | C: {l.consumo}W",
                    font=ctk.CTkFont(size=11),
                )
                lbl_info.pack(side="left", padx=8, pady=4)

                lbl_st = ctk.CTkLabel(
                    row,
                    text=txt_status,
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=cor_status,
                )
                lbl_st.pack(side="right", padx=8, pady=4)

        # Renderização de Gráficos com Matplotlib
        self._plot_graphs(maquina.historico)

    def _plot_graphs(self, historico: list):
        if not MATPLOTLIB_AVAILABLE:
            for w in self.canvas_area.winfo_children():
                w.destroy()
            lbl = ctk.CTkLabel(
                self.canvas_area,
                text="Biblioteca Matplotlib não instalada.\nInstale com: pip install matplotlib\npara visualizar os gráficos em tempo real.",
                text_color=THEME_COLORS["text_secondary"],
            )
            lbl.pack(pady=60)
            return

        if len(historico) < 2:
            for w in self.canvas_area.winfo_children():
                w.destroy()
            lbl = ctk.CTkLabel(
                self.canvas_area,
                text="Histórico insuficiente para plotar gráficos (mínimo 2 medições).\nClique em 'Simular Leitura' para gerar pontos de telemetria.",
                text_color=THEME_COLORS["text_secondary"],
            )
            lbl.pack(pady=60)
            return

        # Limpa widgets anteriores do canvas
        for w in self.canvas_area.winfo_children():
            w.destroy()

        # Cria figura Matplotlib com 3 subplots estilizados em tema escuro
        fig = Figure(figsize=(6, 3.8), dpi=100, facecolor=THEME_COLORS["bg_card_alt"])
        
        # Pega últimas 20 leituras para visualização limpa
        dados_plot = historico[-20:]
        x_indices = list(range(len(dados_plot)))
        temps = [d.temperatura for d in dados_plot]
        vibs = [d.vibracao for d in dados_plot]
        conss = [d.consumo for d in dados_plot]

        # Subplot 1: Temperatura
        ax1 = fig.add_subplot(3, 1, 1)
        ax1.set_facecolor(THEME_COLORS["bg_dark"])
        ax1.plot(x_indices, temps, color="#ef4444", marker="o", markersize=3, linewidth=1.5)
        ax1.axhline(LIMITES_OPERACIONAIS["temperatura_max"], color="#f87171", linestyle="--", linewidth=1, alpha=0.7)
        ax1.set_ylabel("Temp (°C)", color="#f8fafc", fontsize=8)
        ax1.tick_params(colors="#94a3b8", labelsize=7)
        ax1.grid(True, linestyle=":", alpha=0.3, color="#64748b")

        # Subplot 2: Vibração
        ax2 = fig.add_subplot(3, 1, 2)
        ax2.set_facecolor(THEME_COLORS["bg_dark"])
        ax2.plot(x_indices, vibs, color="#f59e0b", marker="o", markersize=3, linewidth=1.5)
        ax2.axhline(LIMITES_OPERACIONAIS["vibracao_max"], color="#fbbf24", linestyle="--", linewidth=1, alpha=0.7)
        ax2.set_ylabel("Vib (mm/s)", color="#f8fafc", fontsize=8)
        ax2.tick_params(colors="#94a3b8", labelsize=7)
        ax2.grid(True, linestyle=":", alpha=0.3, color="#64748b")

        # Subplot 3: Consumo
        ax3 = fig.add_subplot(3, 1, 3)
        ax3.set_facecolor(THEME_COLORS["bg_dark"])
        ax3.plot(x_indices, conss, color="#3b82f6", marker="o", markersize=3, linewidth=1.5)
        ax3.axhline(LIMITES_OPERACIONAIS["consumo_max"], color="#60a5fa", linestyle="--", linewidth=1, alpha=0.7)
        ax3.set_ylabel("Cons (W)", color="#f8fafc", fontsize=8)
        ax3.tick_params(colors="#94a3b8", labelsize=7)
        ax3.grid(True, linestyle=":", alpha=0.3, color="#64748b")

        fig.tight_layout(pad=1.2)

        # Incorpora o canvas na interface CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
