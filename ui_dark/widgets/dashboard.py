"""dashboard.py – dashboard page with animated fade and a line chart.
Uses PyQtGraph for the interactive line chart (temperature, vibration, consumo).
"""

from PyQt5.QtWidgets import QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg

from ..base import AnimatedWidget
from dados import carregar_dados

class Dashboard(AnimatedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboard_page")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("📊 Dashboard – Monitoramento em Tempo Real")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #e0e0ff;")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)

        # Create the plot widget (PyQtGraph)
        self.plot = pg.PlotWidget(title="Temperatura, Vibração, Consumo")
        self.plot.setBackground('#1e1e2f')
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        # Legend
        self.plot.addLegend(offset=(30, 30))
        layout.addWidget(self.plot, stretch=1)

        # Load initial data
        self._load_initial_data()

    def _load_initial_data(self):
        # Simple load – we just plot the historic for the first machine (if exists)
        dados = carregar_dados()
        maquinas = dados.get('maquinas', [])
        if not máquinas:
            return
        # Use the first machine's history
        historico = maquinas[0].get('historico', [])
        if not historico:
            return
        # Extract series
        ts = [i for i, _ in enumerate(historico)]
        temp = [m.get('temperatura', 0) for m in historico]
        vib = [m.get('vibracao', 0) for m in historico]
        cons = [m.get('consumo', 0) for m in historico]
        # Plot lines with distinct colors
        self.plot.plot(ts, temp, pen=pg.mkPen('#ff5722', width=2), name='Temperatura (°C)')
        self.plot.plot(ts, vib, pen=pg.mkPen('#03a9f4', width=2), name='Vibração (mm/s)')
        self.plot.plot(ts, cons, pen=pg.mkPen('#8bc34a', width=2), name='Consumo (W)')

        # Set axis labels
        self.plot.setLabel('left', 'Valor')
        self.plot.setLabel('bottom', 'Amostra')
