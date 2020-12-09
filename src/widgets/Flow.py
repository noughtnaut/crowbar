from typing import Optional

from PyQt5.QtCore import QPoint, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget

from widgets.Canvas import Canvas, CanvasScene, CanvasShape, CanvasView


class FlowShape(CanvasShape):
    _pos: QPoint
    _width = 120
    _height = 60

    def __init__(self, pos: QPoint, *__args):
        self._pos = pos
        super().__init__(self.rect(), *__args)

        pen_shape_edge = QPen()
        pen_shape_edge.setWidth(2)
        pen_shape_edge.setJoinStyle(Qt.RoundJoin)
        pen_shape_edge.setCosmetic(True)
        pen_shape_edge.setColor(QColor(192, 192, 192))
        brush_shape_fill = QBrush()
        brush_shape_fill.setColor(QColor(0, 0, 64))
        brush_shape_fill.setStyle(Qt.SolidPattern)
        self.setPen(pen_shape_edge)
        self.setBrush(brush_shape_fill)

    def rect(self):
        return QRectF(
            self._pos.x() - self._width / 2,
            self._pos.y() - self._height / 2,
            self._width,
            self._height
        )


class FlowTrigger(FlowShape):
    _corner_roundness = 75  # roundness as percentage, so that 0..100 == rect..ellipse

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRoundedRect(self.rect(), self._corner_roundness / 4, self._corner_roundness)


class FlowCondition(FlowShape):

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pen())
        painter.setBrush(self.brush())

        polygon = QPolygonF()
        # Calculate by axis
        top = QPoint(self._pos.x(), self._pos.y() - self._height / 2)
        bot = QPoint(self._pos.x(), self._pos.y() + self._height / 2)
        lef = QPoint(self._pos.x() - self._width / 2, self._pos.y())
        rig = QPoint(self._pos.x() + self._width / 2, self._pos.y())
        # Add points by clockwise order
        polygon.append(top)
        polygon.append(rig)
        polygon.append(bot)
        polygon.append(lef)
        painter.drawPolygon(polygon)


class FlowAction(FlowShape):
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.fillRect(self.rect(), self.brush())
        painter.drawRect(self.rect())


class FlowScene(CanvasScene):
    pass  # Just providing the same under a different name


class FlowView(CanvasView):
    pass  # Just providing the same under a different name


class Flow(Canvas):
    pass  # Just providing the same under a different name

    def __init__(self):
        super().__init__()
        self.view.centerOn(QPoint(0, 0))
