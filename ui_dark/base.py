"""base.py – helpers for the dark UI.
Provides an AnimatedWidget that adds a simple fade‑in/out animation
that can be used for any QWidget subclass.
"""

from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, pyqtSignal

class AnimatedWidget(QWidget):
    """A QWidget with built‑in fade‑in/out support.

    Usage:
        widget = AnimatedWidget()
        widget.fade_in()
        widget.fade_out()
    """
    finished = pyqtSignal()  # emitted when fade‑out finishes (widget can be hidden)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)
        self._anim = QPropertyAnimation(self._opacity, b"opacity")
        self._anim.setDuration(300)  # ms – feel free to tweak
        self._anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._anim.finished.connect(self._on_anim_finished)

    def fade_in(self):
        self.show()
        self._anim.stop()
        self._anim.setStartValue(self._opacity.opacity())
        self._anim.setEndValue(1.0)
        self._anim.start()

    def fade_out(self):
        self._anim.stop()
        self._anim.setStartValue(self._opacity.opacity())
        self._anim.setEndValue(0.0)
        self._anim.start()

    def _on_anim_finished(self):
        if self._opacity.opacity() == 0.0:
            self.hide()
            self.finished.emit()
        # otherwise stay visible
