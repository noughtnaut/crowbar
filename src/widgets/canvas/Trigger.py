from PyQt5.QtGui import QPainter

from widgets.canvas.Canvas import CanvasShape


class Trigger(CanvasShape):
    _corner_roundness = 75  # roundness as percentage, so that 0..100 == rect..ellipse

    def paintShape(self, painter: QPainter):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRoundedRect(self.rect(), self._corner_roundness / 4, self._corner_roundness)
