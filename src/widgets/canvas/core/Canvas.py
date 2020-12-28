from PyQt5.QtWidgets import QGridLayout, QWidget

from widgets.canvas.core.Scene import CanvasScene
from widgets.canvas.core.View import CanvasView


class Canvas(QWidget):
    _scene: CanvasScene
    _view: CanvasView

    def __init__(self):
        super().__init__()
        self._scene = CanvasScene()
        self._view = CanvasView(self._scene, self)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view())
        self.setLayout(layout)

    def scene(self):
        return self._scene

    def view(self):
        return self._view
