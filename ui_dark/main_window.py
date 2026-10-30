"""main_window.py – entry point for the dark UI design.
It builds a QMainWindow with a collapsible Sidebar and a QStackedWidget
that holds animated pages (Dashboard, Machines, Telemetry, Settings, Reports).
"""

import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget
from PyQt5.QtCore import Qt

# Local imports
from .base import AnimatedWidget
from .sidebar import Sidebar
from .widgets.dashboard import Dashboard
# Placeholder widgets for other pages (simple empty widgets for now)

class SimplePage(AnimatedWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName(f"page_{title.lower()}")
        # Simple label to identify the page – can be replaced later
        from PyQt5.QtWidgets import QLabel, QVBoxLayout
        layout = QVBoxLayout(self)
        label = QLabel(f"{title} (em construção)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #e0e0ff; font-size: 14pt;")
        layout.addWidget(label)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MetalSense – Dark UI")
        self.resize(1200, 800)
        # Load dark theme stylesheet
        self._apply_stylesheet()

        # Central widget holds sidebar + stacked pages
        central = QWidget(self)
        self.setCentralWidget(central)
        from PyQt5.QtWidgets import QHBoxLayout
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar navigation
        self.sidebar = Sidebar(self)
        self.sidebar.page_changed.connect(self.switch_page)
        layout.addWidget(self.sidebar)

        # Stacked widget for pages
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack)

        # Create pages (Dashboard is real, others are placeholders)
        self.pages = {
            "dashboard": Dashboard(self),
            "machines": SimplePage("Máquinas", self),
            "telemetry": SimplePage("Telemetria", self),
            "settings": SimplePage("Configurações", self),
            "reports": SimplePage("Relatórios", self),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)
        # Show initial page (Dashboard)
        self.stack.setCurrentWidget(self.pages["dashboard"])
        self.pages["dashboard"].fade_in()

    def _apply_stylesheet(self):
        # Load the QSS file located next to this module
        qss_path = os.path.join(os.path.dirname(__file__), "theme.qss")
        if os.path.isfile(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def switch_page(self, page_key: str):
        """Handle navigation – fade out current page, fade in the new one."""
        if page_key not in self.pages:
            return
        current = self.stack.currentWidget()
        new_page = self.pages[page_key]
        if current is new_page:
            return
        # Fade out current, then set and fade in new
        def _show_new():
            self.stack.setCurrentWidget(new_page)
            new_page.fade_in()
        # Connect temporary slot to animation finished
        current.finished.connect(_show_new, type=Qt.DirectConnection)
        current.fade_out()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
