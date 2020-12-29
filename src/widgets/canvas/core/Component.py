import typing
from typing import Any

from PyQt5 import QtGui
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QStaticText
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem, QStyleOptionGraphicsItem, QWidget

from widgets.canvas.core.Enums import Socket
from widgets.canvas.core import Wire

_DEFAULT_SIZE_W = 80
_DEFAULT_SIZE_H = 80


class Component(QGraphicsRectItem):
    _title: str
    _wiring_in: []
    _wiring_out: []

    def __init__(self, pos: QPointF = None, title: str = None, *__args):
        r = QRectF(
            pos.x() - _DEFAULT_SIZE_W / 2,
            pos.y() - _DEFAULT_SIZE_H / 2,
            _DEFAULT_SIZE_W,
            _DEFAULT_SIZE_H
        )
        super().__init__(r)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.setVisible(True)
        self._title = title
        self.initPainter()
        self._wiring_in = []
        self._wiring_out = []
        self.setCursor(Qt.OpenHandCursor)

    def initPainter(self):
        pen_component_edge = QPen()
        pen_component_edge.setWidth(2)
        pen_component_edge.setJoinStyle(Qt.RoundJoin)
        pen_component_edge.setCosmetic(True)
        pen_component_edge.setColor(QColor(192, 192, 192))
        brush_component_fill = QBrush()
        brush_component_fill.setColor(QColor(0, 0, 64))
        brush_component_fill.setStyle(Qt.SolidPattern)
        self.setPen(pen_component_edge)
        self.setBrush(brush_component_fill)

    # TODO Make Component deletable -- unless it's a Trigger
    # TODO Set cursor on hover: crosshair near anchors to hint wiring, hand in body to hint moving
    # Qt.CrossCursor, Qt.OpenHandCursor
    # TODO Display manipulators on hover: buttons for editing component

    def pos(self):
        return self.rect().center()

    def width(self):
        return self.rect().width()

    def height(self):
        return self.rect().height()

    def title(self):
        return self._title

    def setTitle(self, title: str):
        self._title = '' if title is None else title
        return self

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, new_pos: Any) -> Any:
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            scene_rect = self.scene().sceneRect()
            # Keep the item inside the scene rect
            if not scene_rect.contains(new_pos):
                new_pos.setX(min(scene_rect.right(), max(new_pos.x(), scene_rect.left())))
                new_pos.setY(min(scene_rect.bottom(), max(new_pos.y(), scene_rect.top())))
            # Snap item to grid
            grid_snap_increment = self.scene().grid_snap_increment()
            x = round(new_pos.x() / grid_snap_increment) * grid_snap_increment
            y = round(new_pos.y() / grid_snap_increment) * grid_snap_increment
            return QPointF(x, y)
        elif change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            # FIXME Why is `autoRoute()` still seeing the original component positions?
            for wire in self._wiring_in:
                wire.autoRoute()
            for wire in self._wiring_out:
                wire.autoRoute()
        else:
            return QGraphicsItem.itemChange(self, change, new_pos)

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = ...) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        self.paintShape(painter)
        self.paintTitle(painter)

    def paintShape(self, painter: QPainter):
        r = self.boundingRect()
        painter.drawRect(r)
        painter.drawLine(r.topLeft(), r.bottomRight())
        painter.drawLine(r.bottomLeft(), r.topRight())
        raise Exception('Override the paintShape() method in your subclass')

    def paintTitle(self, painter: QPainter):
        text = QStaticText(self.title())
        text.setTextWidth(20)
        half_size = QPointF(
            text.size().width() / 2,
            text.size().height() / 2
        )
        painter.drawStaticText(self.pos() - half_size, text)
        # FIXME Use drawText() instead of drawStaticText() to have multi-line text centered

    def socketPoint(self, side: Socket):
        if side == Socket.TOP:
            return QPointF(self.pos().x(), self.rect().top())
        if side == Socket.BOTTOM:
            return QPointF(self.pos().x(), self.rect().bottom())
        if side == Socket.LEFT:
            return QPointF(self.rect().left(), self.pos().y())
        if side == Socket.RIGHT:
            return QPointF(self.rect().right(), self.pos().y())

    def addInputWire(self, wire: Wire):
        self._wiring_in.append(wire)

    # TODO removeInputWire()

    def addOutputWire(self, wire: Wire):
        self._wiring_out.append(wire)

    # TODO removeOutputWire()
