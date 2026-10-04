"""
Componente reutilizável de Cartão de KPI para métricas industriais.
"""
import customtkinter as ctk
from desktop.config import THEME_COLORS


class KPICard(ctk.CTkFrame):
    """Card moderno de indicador de desempenho com título, valor e subtítulo."""

    def __init__(
        self,
        master,
        title: str,
        initial_value: str = "0",
        subtitle: str = "",
        accent_color: str = THEME_COLORS["accent_blue"],
        **kwargs
    ):
        super().__init__(master, fg_color=THEME_COLORS["bg_card"], corner_radius=10, border_width=1, border_color=THEME_COLORS["border"], **kwargs)

        self.grid_columnconfigure(0, weight=1)

        # Barra de destaque lateral / topo
        self.accent_bar = ctk.CTkFrame(self, height=4, fg_color=accent_color, corner_radius=2)
        self.accent_bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 4))

        # Título
        self.title_label = ctk.CTkLabel(
            self,
            text=title.upper(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=THEME_COLORS["text_secondary"],
        )
        self.title_label.grid(row=1, column=0, sticky="w", padx=14, pady=(2, 0))

        # Valor Principal
        self.value_label = ctk.CTkLabel(
            self,
            text=initial_value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=THEME_COLORS["text_primary"],
        )
        self.value_label.grid(row=2, column=0, sticky="w", padx=14, pady=(2, 2))

        # Subtítulo / Delta
        self.subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color=THEME_COLORS["text_secondary"],
        )
        self.subtitle_label.grid(row=3, column=0, sticky="w", padx=14, pady=(0, 10))

    def update_data(self, value: str, subtitle: str = None, text_color: str = None):
        """Atualiza dinamicamente o valor e mensagem do card."""
        self.value_label.configure(text=str(value))
        if subtitle is not None:
            self.subtitle_label.configure(text=subtitle)
        if text_color is not None:
            self.value_label.configure(text_color=text_color)
