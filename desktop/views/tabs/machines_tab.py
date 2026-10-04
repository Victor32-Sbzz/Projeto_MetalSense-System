"""
Aba de Gestão de Equipamentos (Cadastro, Busca e Exclusão).
"""
import customtkinter as ctk
from desktop.config import THEME_COLORS
from desktop.views.components.status_badge import StatusBadge


class MachinesTab(ctk.CTkFrame):
    """Permite cadastrar, visualizar e remover máquinas com validação e confirmação."""

    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._build_ui()

    def _build_ui(self):
        # Painel Esquerdo: Cadastro e Ações
        self.left_panel = ctk.CTkFrame(self, fg_color=THEME_COLORS["bg_card"], corner_radius=10, border_width=1, border_color=THEME_COLORS["border"])
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.left_panel.grid_columnconfigure(0, weight=1)

        lbl_cad = ctk.CTkLabel(
            self.left_panel,
            text="➕ Cadastrar Máquina",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=THEME_COLORS["text_primary"],
        )
        lbl_cad.pack(anchor="w", padx=20, pady=(20, 5))

        lbl_desc = ctk.CTkLabel(
            self.left_panel,
            text="Insira o identificador fabril para iniciar o monitoramento.",
            font=ctk.CTkFont(size=12),
            text_color=THEME_COLORS["text_secondary"],
        )
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 20))

        # Campo de Nome
        lbl_field = ctk.CTkLabel(self.left_panel, text="Nome do Equipamento:", font=ctk.CTkFont(weight="bold"))
        lbl_field.pack(anchor="w", padx=20, pady=(5, 2))

        self.entry_nome = ctk.CTkEntry(
            self.left_panel,
            placeholder_text="Ex: Prensa Hidráulica 04",
            height=38,
            font=ctk.CTkFont(size=13),
        )
        self.entry_nome.pack(fill="x", padx=20, pady=(0, 8))

        # Mensagem de validação
        self.lbl_feedback = ctk.CTkLabel(self.left_panel, text="", font=ctk.CTkFont(size=11), text_color=THEME_COLORS["status_anomaly"])
        self.lbl_feedback.pack(anchor="w", padx=20, pady=(0, 10))

        # Botão Cadastrar
        self.btn_cadastrar = ctk.CTkButton(
            self.left_panel,
            text="Adicionar ao Sistema",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=THEME_COLORS["accent_blue"],
            command=self._on_cadastrar_click,
        )
        self.btn_cadastrar.pack(fill="x", padx=20, pady=10)

        # Divisor
        div = ctk.CTkFrame(self.left_panel, height=1, fg_color=THEME_COLORS["border"])
        div.pack(fill="x", padx=20, pady=25)

        # Seção de Remoção Segura
        lbl_del_title = ctk.CTkLabel(
            self.left_panel,
            text="🗑️ Exclusão de Máquina",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=THEME_COLORS["status_anomaly"],
        )
        lbl_del_title.pack(anchor="w", padx=20, pady=(0, 5))

        self.lbl_sel_info = ctk.CTkLabel(
            self.left_panel,
            text="Selecione um equipamento na lista ao lado para habilitar a exclusão.",
            font=ctk.CTkFont(size=12),
            text_color=THEME_COLORS["text_secondary"],
            wraplength=260,
            justify="left",
        )
        self.lbl_sel_info.pack(anchor="w", padx=20, pady=(0, 10))

        self.chk_confirmar = ctk.CTkCheckBox(
            self.left_panel,
            text="Confirmo exclusão definitiva",
            font=ctk.CTkFont(size=12),
            state="disabled",
            command=self._on_toggle_confirm,
        )
        self.chk_confirmar.pack(anchor="w", padx=20, pady=5)

        self.btn_remover = ctk.CTkButton(
            self.left_panel,
            text="Excluir Selecionada",
            height=36,
            fg_color=THEME_COLORS["status_anomaly"],
            state="disabled",
            command=self._on_remover_click,
        )
        self.btn_remover.pack(fill="x", padx=20, pady=(10, 20))

        # Painel Direito: Lista de Máquinas e Seleção
        self.right_panel = ctk.CTkFrame(self, fg_color=THEME_COLORS["bg_card"], corner_radius=10, border_width=1, border_color=THEME_COLORS["border"])
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(1, weight=1)

        # Header do Painel Direito
        top_bar = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        top_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top_bar,
            text="Parque Fabril Cadastrado",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=THEME_COLORS["text_primary"],
        ).grid(row=0, column=0, sticky="w")

        # Scrollable list
        self.scroll_machines = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.scroll_machines.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.scroll_machines.grid_columnconfigure(0, weight=1)

        self.selected_machine_id = None

    def _on_cadastrar_click(self):
        nome = self.entry_nome.get().strip()
        if not nome:
            self.lbl_feedback.configure(text="* Informe um nome válido para a máquina.", text_color=THEME_COLORS["status_anomaly"])
            self.entry_nome.focus()
            return

        self.lbl_feedback.configure(text="")
        self.controller.cadastrar_maquina_async(nome)
        self.entry_nome.delete(0, "end")

    def _on_toggle_confirm(self):
        if self.chk_confirmar.get() == 1 and self.selected_machine_id:
            self.btn_remover.configure(state="normal")
        else:
            self.btn_remover.configure(state="disabled")

    def _on_remover_click(self):
        if self.selected_machine_id:
            self.controller.remover_maquina_async(self.selected_machine_id)
            self.selected_machine_id = None
            self.chk_confirmar.deselect()
            self.chk_confirmar.configure(state="disabled")
            self.btn_remover.configure(state="disabled")
            self.lbl_sel_info.configure(text="Máquina removida com sucesso.")

    def select_machine(self, mid: int, nome: str):
        """Seleciona a máquina para contexto de exclusão ou ação."""
        self.selected_machine_id = mid
        self.chk_confirmar.configure(state="normal")
        self.chk_confirmar.deselect()
        self.btn_remover.configure(state="disabled")
        self.lbl_sel_info.configure(
            text=f"Máquina selecionada: [ID #{mid}] {nome}.\nMarque a confirmação para habilitar a remoção.",
            text_color=THEME_COLORS["text_primary"],
        )
        self.highlight_selected_card()

    def highlight_selected_card(self):
        for w in self.scroll_machines.winfo_children():
            if hasattr(w, "machine_id"):
                if w.machine_id == self.selected_machine_id:
                    w.configure(border_color=THEME_COLORS["accent_blue"], border_width=2)
                else:
                    w.configure(border_color=THEME_COLORS["border"], border_width=1)

    def refresh(self, maquinas: list):
        """Atualiza listagem de máquinas com cards interativos."""
        for widget in self.scroll_machines.winfo_children():
            widget.destroy()

        if not maquinas:
            empty = ctk.CTkLabel(
                self.scroll_machines,
                text="Nenhum equipamento cadastrado.",
                text_color=THEME_COLORS["text_secondary"],
            )
            empty.pack(pady=40)
            return

        for m in maquinas:
            card = ctk.CTkFrame(
                self.scroll_machines,
                fg_color=THEME_COLORS["bg_card_alt"],
                corner_radius=8,
                border_width=2 if m.id == self.selected_machine_id else 1,
                border_color=THEME_COLORS["accent_blue"] if m.id == self.selected_machine_id else THEME_COLORS["border"],
            )
            card.machine_id = m.id
            card.pack(fill="x", pady=4, padx=2)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(card, text=f"#{m.id}", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=10, sticky="w")
            ctk.CTkLabel(card, text=m.nome, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=1, padx=6, pady=10, sticky="w")

            badge = StatusBadge(card, status=m.status)
            badge.grid(row=0, column=2, padx=10, pady=10, sticky="e")

            btn_sel = ctk.CTkButton(
                card,
                text="Selecionar",
                width=80,
                height=28,
                fg_color=THEME_COLORS["accent_blue"],
                command=lambda mid=m.id, mnome=m.nome: self.select_machine(mid, mnome),
            )
            btn_sel.grid(row=0, column=3, padx=(4, 10), pady=10, sticky="e")
