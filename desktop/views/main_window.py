"""
Janela Principal da Aplicação MetalSense Desktop.
Implementa Tema Escuro Moderno, Sidebar de Navegação, Área Central Dinâmica e Barra de Status.
"""
import customtkinter as ctk
from datetime import datetime

from desktop.config import THEME_COLORS
from desktop.views.tabs.dashboard_tab import DashboardTab
from desktop.views.tabs.machines_tab import MachinesTab
from desktop.views.tabs.telemetry_tab import TelemetryTab


class MainWindow(ctk.CTk):
    """Janela desktop de alto desempenho e ergonomia visual."""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # Configurações da Janela
        self.title("MetalSense — Monitoramento Industrial Preditivo • TechForge")
        self.geometry("1200x760")
        self.minsize(980, 620)

        # Configura Tema Escuro
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=THEME_COLORS["bg_dark"])

        # Grid Principal: Sidebar (col 0) + Área de Conteúdo (col 1)
        self.grid_columnconfigure(0, weight=0, minsize=230)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # Rodapé / Status Bar

        self._build_sidebar()
        self._build_content_area()
        self._build_status_bar()

        # Define aba inicial
        self.navegar_para("dashboard")

    def _build_sidebar(self):
        """Barra lateral com identidade visual e navegação."""
        self.sidebar = ctk.CTkFrame(self, fg_color=THEME_COLORS["bg_card"], width=230, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)

        # Brand / Logo
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 25))

        lbl_brand_tag = ctk.CTkLabel(
            brand_frame,
            text="TECHFORGE INDUSTRY",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=THEME_COLORS["accent_blue"],
        )
        lbl_brand_tag.pack(anchor="w")

        lbl_logo = ctk.CTkLabel(
            brand_frame,
            text="⚙️ MetalSense",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=THEME_COLORS["text_primary"],
        )
        lbl_logo.pack(anchor="w")

        # Botões de Navegação
        self.btn_nav_dash = ctk.CTkButton(
            self.sidebar,
            text="📊 Dashboard Geral",
            anchor="w",
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=THEME_COLORS["accent_blue"],
            command=lambda: self.navegar_para("dashboard"),
        )
        self.btn_nav_dash.pack(fill="x", padx=12, pady=4)

        self.btn_nav_machines = ctk.CTkButton(
            self.sidebar,
            text="🏭 Gestão de Máquinas",
            anchor="w",
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            text_color=THEME_COLORS["text_primary"],
            hover_color=THEME_COLORS["bg_card_alt"],
            command=lambda: self.navegar_para("machines"),
        )
        self.btn_nav_machines.pack(fill="x", padx=12, pady=4)

        self.btn_nav_telemetry = ctk.CTkButton(
            self.sidebar,
            text="📈 Telemetria & Gráficos",
            anchor="w",
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            text_color=THEME_COLORS["text_primary"],
            hover_color=THEME_COLORS["bg_card_alt"],
            command=lambda: self.navegar_para("telemetry"),
        )
        self.btn_nav_telemetry.pack(fill="x", padx=12, pady=4)

        # Rodapé da Sidebar
        sidebar_bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_bottom.pack(side="bottom", fill="x", padx=16, pady=20)

        lbl_version = ctk.CTkLabel(
            sidebar_bottom,
            text="Versão 2.4.0 • Enterprise\nStatus: Conectado",
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_secondary"],
            justify="left",
        )
        lbl_version.pack(anchor="w")

    def _build_content_area(self):
        """Área central dinâmica onde as abas/telas são montadas."""
        self.content_container = ctk.CTkFrame(self, fg_color=THEME_COLORS["bg_dark"], corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Instancia as 3 abas principais
        self.tab_dashboard = DashboardTab(self.content_container, controller=self.controller)
        self.tab_machines = MachinesTab(self.content_container, controller=self.controller)
        self.tab_telemetry = TelemetryTab(self.content_container, controller=self.controller)

    def _build_status_bar(self):
        """Barra inferior de status, feedback ao usuário e atividade de background."""
        self.status_bar = ctk.CTkFrame(self, fg_color=THEME_COLORS["bg_card"], height=32, corner_radius=0)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_columnconfigure(0, weight=1)
        self.status_bar.grid_propagate(False)

        # Mensagem de Log / Status
        self.lbl_status = ctk.CTkLabel(
            self.status_bar,
            text="🟢 MetalSense Desktop pronto.",
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_secondary"],
        )
        self.lbl_status.pack(side="left", padx=16)

        # Indicador de Atividade (Barra indeterminada para operações em background)
        self.progress_bar = ctk.CTkProgressBar(
            self.status_bar,
            width=140,
            height=8,
            mode="indeterminate",
            fg_color=THEME_COLORS["bg_card_alt"],
            progress_color=THEME_COLORS["accent_blue"],
        )
        # Oculta inicialmente
        self.progress_bar.set(0)

        # Relógio / Timestamp da Sessão
        self.lbl_clock = ctk.CTkLabel(
            self.status_bar,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_secondary"],
        )
        self.lbl_clock.pack(side="right", padx=16)
        self._update_clock()

    def _update_clock(self):
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.lbl_clock.configure(text=now_str)
        self.after(1000, self._update_clock)

    def set_busy_state(self, is_busy: bool, message: str = ""):
        """Mostra/oculta barra de progresso durante execução não-bloqueante."""
        if is_busy:
            self.progress_bar.pack(side="right", padx=10)
            self.progress_bar.start()
            if message:
                self.set_status_message(f"⏳ {message}")
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            if message:
                self.set_status_message(message)

    def set_status_message(self, message: str, is_error: bool = False):
        """Atualiza a mensagem na barra de status inferior."""
        cor = THEME_COLORS["status_anomaly"] if is_error else THEME_COLORS["text_primary"]
        self.lbl_status.configure(text=message, text_color=cor)

    def navegar_para(self, destino: str):
        """Alterna visualmente as abas com destaque no menu lateral."""
        # Reseta estilos dos botões
        for btn in [self.btn_nav_dash, self.btn_nav_machines, self.btn_nav_telemetry]:
            btn.configure(fg_color="transparent", text_color=THEME_COLORS["text_primary"])

        # Oculta todas as telas
        for tab in [self.tab_dashboard, self.tab_machines, self.tab_telemetry]:
            tab.grid_forget()

        if destino == "dashboard":
            self.btn_nav_dash.configure(fg_color=THEME_COLORS["accent_blue"])
            self.tab_dashboard.grid(row=0, column=0, sticky="nsew")
            self.controller.atualizar_dados_globais()
        elif destino == "machines":
            self.btn_nav_machines.configure(fg_color=THEME_COLORS["accent_blue"])
            self.tab_machines.grid(row=0, column=0, sticky="nsew")
            self.controller.atualizar_dados_globais()
        elif destino == "telemetry":
            self.btn_nav_telemetry.configure(fg_color=THEME_COLORS["accent_blue"])
            self.tab_telemetry.grid(row=0, column=0, sticky="nsew")
            self.controller.atualizar_dados_globais()
