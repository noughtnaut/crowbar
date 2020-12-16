from typing import Optional

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from PyQt5.QtWidgets import QStyleOptionGraphicsItem, QWidget

from ui.UiUtils import draw_static_centered_text
from widgets.Canvas import Canvas, CanvasScene, CanvasShape, CanvasView


class FlowShape(CanvasShape):
    _title: str

    def __init__(self, *__args, title=None):
        super().__init__(*__args)
        self._title = title
        self.setWidth(120)
        self.setHeight(60)
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


class FlowTrigger(FlowShape):
    _corner_roundness = 75  # roundness as percentage, so that 0..100 == rect..ellipse

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRoundedRect(self.rect(), self._corner_roundness / 4, self._corner_roundness)
        draw_static_centered_text(painter, self.pos(), 'Trigger')


class FlowCondition(FlowShape):
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

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawPolygon(self._polygon)
        draw_static_centered_text(painter, self.pos(), 'Is condition true?')

    def shape(self) -> QPainterPath:
        return self._shape


class FlowAction(FlowShape):
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.fillRect(self.rect(), self.brush())
        painter.drawRect(self.rect())
        draw_static_centered_text(painter, self.pos(), 'Action')


class FlowScene(CanvasScene):
    pass  # Just providing the same under a different name


class FlowView(CanvasView):
    pass  # Just providing the same under a different name


class Flow(Canvas):
    pass  # Just providing the same under a different name

    def __init__(self):
        super().__init__()
        self.view.centerOn(QPoint(0, 0))
