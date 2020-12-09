from typing import Any, Optional

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QCursor, QMouseEvent, QPainter, QPen, QWheelEvent
from PyQt5.QtWidgets import QAbstractGraphicsShapeItem, QFrame, QGraphicsItem, QGraphicsItemGroup, QGraphicsScene, \
    QGraphicsView, QGridLayout, QStyleOptionGraphicsItem, QWidget

from ui.UiUtils import click_descriptor, with_control_key


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = CanvasScene()
        self.view = CanvasView(self.scene, self)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setLayout(layout)


class CanvasShape(QAbstractGraphicsShapeItem):
    _pos: QPointF
    _rect: QRectF

    def __init__(self, pos: QPointF, *__args):
        super().__init__(*__args)
        self.setPos(pos)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.setVisible(True)

    def setPos(self, pos: QPointF):
        self._pos = pos

    def setWidth(self, w: int):
        self._width = w

    def setHeight(self, h: int):
        self._height = h

    def boundingRect(self) -> QtCore.QRectF:
        return self.rect()

    def rect(self):
        return QRectF(
            self._pos.x() - self._width / 2,
            self._pos.y() - self._height / 2,
            self._width,
            self._height
        )

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # value is the new position
            rect = self.scene().sceneRect()
            # Keep the item inside the scene rect
            if not rect.contains(value):
                value.setX(min(rect.right(), max(value.x(), rect.left())))
                value.setY(min(rect.bottom(), max(value.y(), rect.top())))
            # Snap item to grid
            grid_size = 10
            x = round(value.x() / grid_size) * grid_size
            y = round(value.y() / grid_size) * grid_size
            return QPointF(x, y)
        else:
            return QGraphicsItem.itemChange(self, change, value)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        r = self.boundingRect()
        painter.drawRect(r)
        painter.drawLine(r.topLeft(), r.bottomRight())
        painter.drawLine(r.bottomLeft(), r.topRight())
        raise Exception('Override the paint() method in your subclass')


class CanvasScene(QGraphicsScene):
    _grid_minor = 20
    _grid_medium = 100
    _grid_major = 500

    def __init__(self):
        super().__init__()
        self.setSceneRect(-5000, -500, 10000, 10000)  # TODO This should be set outside of Canvas
        self._create_background_grid()

    def _create_background_grid(self):
        self._group_grid = QGraphicsItemGroup()
        self.addItem(self._group_grid)

        self._brush_background = QBrush(QColor(0, 40, 0))
        scene_rect = self.sceneRect()
        self._group_grid.addToGroup(
            self.addRect(scene_rect, QPen(), self._brush_background))
        self._pen_grid_minor = QPen()
        self._pen_grid_minor.setWidth(1)
        self._pen_grid_minor.setCosmetic(True)
        self._pen_grid_minor.setColor(QColor(0, 48, 0))
        for x in range(int(scene_rect.left()), int(scene_rect.right()), self._grid_minor):
            self._group_grid.addToGroup(
                self.addLine(x, scene_rect.top(), x, scene_rect.bottom(), self._pen_grid_minor))
        for y in range(int(scene_rect.top()), int(scene_rect.bottom()), self._grid_minor):
            self._group_grid.addToGroup(
                self.addLine(scene_rect.left(), y, scene_rect.right(), y, self._pen_grid_minor))
        self._pen_grid_medium = QPen()
        self._pen_grid_medium.setWidth(2)
        self._pen_grid_medium.setCosmetic(True)
        self._pen_grid_medium.setColor(QColor(0, 56, 0))
        for x in range(int(scene_rect.left()), int(scene_rect.right()), self._grid_medium):
            self._group_grid.addToGroup(
                self.addLine(x, scene_rect.top(), x, scene_rect.bottom(), self._pen_grid_medium))
        for y in range(int(scene_rect.top()), int(scene_rect.bottom()), self._grid_medium):
            self._group_grid.addToGroup(
                self.addLine(scene_rect.left(), y, scene_rect.right(), y, self._pen_grid_medium))
        self._pen_grid_major = QPen()
        self._pen_grid_major.setWidth(3)
        self._pen_grid_major.setCosmetic(True)
        self._pen_grid_major.setColor(QColor(0, 64, 0))
        for x in range(int(scene_rect.left()), int(scene_rect.right()), self._grid_major):
            self._group_grid.addToGroup(
                self.addLine(x, scene_rect.top(), x, scene_rect.bottom(), self._pen_grid_major))
        for y in range(int(scene_rect.top()), int(scene_rect.bottom()), self._grid_major):
            self._group_grid.addToGroup(
                self.addLine(scene_rect.left(), y, scene_rect.right(), y, self._pen_grid_major))
        # Axis lines
        self._pen_grid_major.setColor(QColor(0, 96, 0))
        self._group_grid.addToGroup(
            self.addLine(0, scene_rect.top(), 0, scene_rect.bottom(), self._pen_grid_major))
        self._group_grid.addToGroup(
            self.addLine(scene_rect.left(), 0, scene_rect.right(), 0, self._pen_grid_major))

    def itemsBoundingRectWithoutGrid(self) -> QtCore.QRectF:
        self.removeItem(self._group_grid)
        r = self.itemsBoundingRect()
        self.addItem(self._group_grid)
        self._group_grid.setZValue(-1)
        return r


class CanvasView(QGraphicsView):
    _zoom = 1.0
    _zoom_factor = 1.25
    _zoom_min = 0.125
    _zoom_max = 8

    def __init__(self, scene: CanvasScene, parent: QWidget):
        super().__init__(scene, parent)
        self.setFrameStyle(QFrame.Panel)
        self.setMouseTracking(True)
        self._cursor_normal = QCursor(Qt.ArrowCursor)
        self._cursor_crosshair = QCursor(Qt.CrossCursor)
        self._cursor_closed_hand = QCursor(Qt.ClosedHandCursor)
        self.setCursor(self._cursor_normal)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        print(click_descriptor(event, 'drag¤'))
        super().dragMoveEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # print(click_descriptor(event, 'move'))
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        print(click_descriptor(event, 'click'))
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseDoubleClickEvent(event)
        print(click_descriptor(event, 'double-click'))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        print(click_descriptor(event, 'release'))
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        # print(click_descriptor(event, 'scroll'))
        # Zoom on Ctrl-scroll
        if with_control_key(event) and event.angleDelta().y():
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            super().wheelEvent(event)

    def zoom_out(self):
        factor = 1 / self._zoom_factor
        self.zoom_by_factor(factor)

    def zoom_in(self):
        factor = self._zoom_factor
        self.zoom_by_factor(factor)

    def zoom_by_factor(self, factor):
        new_zoom = self._zoom * factor
        if self._zoom_min < new_zoom < self._zoom_max:
            self.scale(factor, factor)
            self._zoom = self.transform().m11()  # m11 and m22 are the applied x and y scaling factors
        # TODO Keep the point at the cursor position in place while zooming (when possible)

    def zoom_reset(self):
        # Note: This works, but does nothing to bring the contents into view
        self.scale(1 / self._zoom, 1 / self._zoom)
        self._zoom = self.transform().m11()

    def zoom_to_fit(self):
        self.fitInView(self.scene().itemsBoundingRectWithoutGrid(), Qt.KeepAspectRatio)
        self._zoom = self.transform().m11()
