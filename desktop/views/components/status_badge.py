"""
Componente reutilizável de Badge visual para status operacional.
"""
import customtkinter as ctk
from desktop.config import THEME_COLORS


class StatusBadge(ctk.CTkFrame):
    """Badge arredondado colorido para exibição imediata do status."""

    def __init__(self, master, status: str = "sem dados", **kwargs):
        super().__init__(master, corner_radius=14, **kwargs)

        self.label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffffff",
            padx=12,
            pady=4,
        )
        self.label.pack()

        self.set_status(status)

    def set_status(self, status: str):
        st_clean = (status or "sem dados").strip().lower()

        if st_clean == "normal":
            bg_color = THEME_COLORS["status_normal"]
            text_display = "🟢 OPERAÇÃO NORMAL"
        elif st_clean == "anomalia":
            bg_color = THEME_COLORS["status_anomaly"]
            text_display = "🚨 ANOMALIA DETECTADA"
        else:
            bg_color = THEME_COLORS["status_unknown"]
            text_display = "⚪ SEM DADOS"

        self.configure(fg_color=bg_color)
        self.label.configure(text=text_display)
