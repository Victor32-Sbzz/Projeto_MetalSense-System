"""
Aba de Dashboard / Visão Geral do Parque Fabril.
"""
import customtkinter as ctk
from desktop.config import THEME_COLORS
from desktop.views.components.kpi_card import KPICard
from desktop.views.components.status_badge import StatusBadge


class DashboardTab(ctk.CTkFrame):
    """Visualização consolidada de indicadores e máquinas do sistema."""

    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_ui()

    def _build_ui(self):
        # Título da seção
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 15))
        
        lbl_title = ctk.CTkLabel(
            header_frame,
            text="Visão Executiva do Parque Fabril",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=THEME_COLORS["text_primary"],
        )
        lbl_title.pack(side="left")

        lbl_sub = ctk.CTkLabel(
            header_frame,
            text="Telemetria em tempo real • Inteligência Preditiva TechForge",
            font=ctk.CTkFont(size=12),
            text_color=THEME_COLORS["text_secondary"],
        )
        lbl_sub.pack(side="left", padx=15, pady=(4, 0))

        # Grade de KPIs
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 15))
        self.kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")

        self.kpi_total = KPICard(self.kpi_frame, title="Total de Máquinas", accent_color=THEME_COLORS["accent_blue"])
        self.kpi_total.grid(row=0, column=0, padx=6, pady=4, sticky="nsew")

        self.kpi_normal = KPICard(self.kpi_frame, title="Operação Normal", accent_color=THEME_COLORS["status_normal"])
        self.kpi_normal.grid(row=0, column=1, padx=6, pady=4, sticky="nsew")

        self.kpi_anomalia = KPICard(self.kpi_frame, title="Em Anomalia", accent_color=THEME_COLORS["status_anomaly"])
        self.kpi_anomalia.grid(row=0, column=2, padx=6, pady=4, sticky="nsew")

        self.kpi_leituras = KPICard(self.kpi_frame, title="Total de Leituras", accent_color=THEME_COLORS["accent_cyan"])
        self.kpi_leituras.grid(row=0, column=3, padx=6, pady=4, sticky="nsew")

        # Container inferior: Tabela / Lista de Máquinas
        self.list_container = ctk.CTkFrame(self, fg_color=THEME_COLORS["bg_card"], corner_radius=10, border_width=1, border_color=THEME_COLORS["border"])
        self.list_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_rowconfigure(1, weight=1)

        # Cabeçalho da Lista
        list_header = ctk.CTkFrame(self.list_container, fg_color=THEME_COLORS["bg_card_alt"], height=38, corner_radius=8)
        list_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        list_header.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(list_header, text="ID", font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME_COLORS["text_secondary"]).grid(row=0, column=0, padx=10, pady=6, sticky="w")
        ctk.CTkLabel(list_header, text="MÁQUINA", font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME_COLORS["text_secondary"]).grid(row=0, column=1, padx=10, pady=6, sticky="w")
        ctk.CTkLabel(list_header, text="STATUS", font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME_COLORS["text_secondary"]).grid(row=0, column=2, padx=10, pady=6, sticky="w")
        ctk.CTkLabel(list_header, text="ÚLTIMA TELEMETRIA", font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME_COLORS["text_secondary"]).grid(row=0, column=3, padx=10, pady=6, sticky="w")
        ctk.CTkLabel(list_header, text="AÇÃO", font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME_COLORS["text_secondary"]).grid(row=0, column=4, padx=10, pady=6, sticky="e")

        # Scrollable frame para as linhas
        self.scroll_rows = ctk.CTkScrollableFrame(self.list_container, fg_color="transparent")
        self.scroll_rows.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_rows.grid_columnconfigure(0, weight=1)

    def refresh(self, maquinas: list):
        """Atualiza os indicadores e a lista de máquinas exibida."""
        total = len(maquinas)
        normais = sum(1 for m in maquinas if m.status == "normal")
        anomalias = sum(1 for m in maquinas if m.status == "anomalia")
        leituras = sum(len(m.historico) for m in maquinas)

        self.kpi_total.update_data(str(total), subtitle=f"Parque monitorado")
        self.kpi_normal.update_data(str(normais), subtitle=f"{(normais/total*100):.0f}% do total" if total else "0%")
        self.kpi_anomalia.update_data(str(anomalias), subtitle="Alerta(s) ativo(s)" if anomalias else "Sem anomalias")
        self.kpi_leituras.update_data(str(leituras), subtitle="Medições coletadas")

        # Limpa linhas anteriores
        for widget in self.scroll_rows.winfo_children():
            widget.destroy()

        if not maquinas:
            empty_lbl = ctk.CTkLabel(
                self.scroll_rows,
                text="Nenhum equipamento cadastrado. Utilize a aba 'Gestão de Máquinas' para adicionar.",
                text_color=THEME_COLORS["text_secondary"],
                font=ctk.CTkFont(size=13),
            )
            empty_lbl.pack(pady=30)
            return

        for idx, m in enumerate(maquinas):
            row = ctk.CTkFrame(self.scroll_rows, fg_color=THEME_COLORS["bg_card"] if idx % 2 == 0 else THEME_COLORS["bg_card_alt"], corner_radius=6)
            row.pack(fill="x", pady=2, padx=2)
            row.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

            ctk.CTkLabel(row, text=f"#{m.id}", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=m.nome, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=8, sticky="w")

            badge = StatusBadge(row, status=m.status)
            badge.grid(row=0, column=2, padx=10, pady=8, sticky="w")

            ult_str = "Sem leituras"
            if m.historico:
                u = m.historico[-1]
                ult_str = f"{u.temperatura}°C | {u.vibracao}mm/s | {u.consumo}W"
            ctk.CTkLabel(row, text=ult_str, text_color=THEME_COLORS["text_secondary"]).grid(row=0, column=3, padx=10, pady=8, sticky="w")

            btn_ver = ctk.CTkButton(
                row,
                text="Inspecionar",
                width=90,
                height=28,
                fg_color=THEME_COLORS["accent_blue"],
                command=lambda mid=m.id: self.controller.selecionar_maquina_para_inspecao(mid),
            )
            btn_ver.grid(row=0, column=4, padx=10, pady=8, sticky="e")
