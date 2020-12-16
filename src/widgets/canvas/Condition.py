from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPainter, QPainterPath, QPolygonF

from widgets.canvas.Canvas import CanvasShape


class Condition(CanvasShape):
    _polygon: QPolygonF
    _shape: QPainterPath

    def __init__(self, *__args):
        super().__init__(*__args)
        self._polygon = QPolygonF()
        # Calculate by axis
        top = QPoint(self._pos.x(), self._pos.y() - self._height / 2)
        bot = QPoint(self._pos.x(), self._pos.y() + self._height / 2)
        lef = QPoint(self._pos.x() - self._width / 2, self._pos.y())
        rig = QPoint(self._pos.x() + self._width / 2, self._pos.y())
        # Add points by clockwise order
        self._polygon.append(top)
        self._polygon.append(rig)
        self._polygon.append(bot)
        self._polygon.append(lef)
        self._shape = QPainterPath()
        self._shape.addPolygon(self._polygon)

    def shape(self) -> QPainterPath:
        # This defines the outline when it comes to resolving click targets
        return self._shape

    def paintShape(self, painter: QPainter):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawPolygon(self._polygon)
