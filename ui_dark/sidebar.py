"""sidebar.py – collapsible dark sidebar navigation for the UI.
Provides Sidebar class with QToolButtons for navigation.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolButton, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal

class Sidebar(QWidget):
    """Sidebar with navigation buttons.

    Emits ``page_changed`` with the name of the page to display.
    """
    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #2c2c44;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Define navigation items (order matters)
        self._pages = [
            ("dashboard", "Dashboard"),
            ("machines", "Máquinas"),
            ("telemetry", "Telemetria"),
            ("settings", "Configurações"),
            ("reports", "Relatórios"),
        ]

        self._buttons = {}
        for key, label in self._pages:
            btn = QToolButton(self)
            btn.setObjectName(f"btn_{key}")
            btn.setText(label)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.setStyleSheet(
                "QToolButton { color: #c0c0ff; padding: 12px; text-align: left; }"
                "QToolButton:hover { background-color: #3a3a66; }"
                "QToolButton:checked { background-color: #0d47a1; color: #ffffff; }"
            )
            btn.clicked.connect(lambda _, k=key: self.page_changed.emit(k))
            layout.addWidget(btn)
            self._buttons[key] = btn

        layout.addStretch(1)
        # Set default selection
        self._buttons["dashboard"].setChecked(True)
        self.page_changed.emit("dashboard")
