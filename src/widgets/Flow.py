from typing import Optional

from PyQt5.QtCore import QRectF, QPoint, Qt
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtWidgets import QWidget, QStyleOptionGraphicsItem

from widgets.Canvas import CanvasShape, Canvas, CanvasScene, CanvasView


class FlowShape(CanvasShape):
    _pos: QPoint
    _width = 120
    _height = 80

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
    _corner_roundness = 75  # 0-99 on some arbitrary scale

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRoundedRect(self.rect(), self._corner_roundness / 4, self._corner_roundness)


class FlowCondition(FlowShape):

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem,
              widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        # TODO Draw a rhombus
        # painter.drawPolygon(self.midsides())

    def midsides(self):
        t = self.rect().top()
        l = self.rect().left()
        r = self.rect().right()
        b = self.rect().bottom()
        mt = QPoint(l + (r - l) / 2, t)
        mb = QPoint(l + (r - l) / 2, b)
        ml = QPoint(l, t + (b - t) / 2)
        mr = QPoint(r, t + (b - t) / 2)
        return mt, ml, mr, mb
        # FIXME The coordinates are (probably) okay,
        # FIXME but they are not returned in a way that is useful to drawPolygon()


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
