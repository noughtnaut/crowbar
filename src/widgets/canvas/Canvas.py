import typing
from typing import Any

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QLineF, QPointF, QRect, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QCursor, QMouseEvent, QPainter, QPen, QStaticText, QWheelEvent
from PyQt5.QtWidgets import QFrame, QGraphicsItem, QGraphicsRectItem, QGraphicsScene, \
    QGraphicsView, \
    QGridLayout, QStyleOptionGraphicsItem, QWidget

from ui.UiUtils import click_descriptor, with_control_key

_DEFAULT_SIZE_W = 120
_DEFAULT_SIZE_H = 60


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = CanvasScene()
        self.view = CanvasView(self.scene, self)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.view.centerOn(QPointF(0, 0))


class CanvasShape(QGraphicsRectItem):
    _title: str

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

    def pos(self):
        return self.rect().center()  # TODO: Fully implement centre-based locations

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
        else:
            return QGraphicsItem.itemChange(self, change, new_pos)

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = ...) -> None:
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


class CanvasScene(QGraphicsScene):
    _grid_line_increment = 20
    _grid_snap_increment = 10

    def __init__(self):
        super().__init__()
        self.setSceneRect(-5000, -500, 10000, 10000)  # TODO This should be set outside of Canvas
        self._prepare_background_grid()

    def grid_snap_increment(self):
        return self._grid_snap_increment

    def grid_minor(self):
        return self._grid_line_increment

    def grid_medium(self):
        return self.grid_minor() * 5

    def grid_major(self):
        return self.grid_medium() * 5

    def _prepare_background_grid(self):
        self._brush_background = QBrush(QColor(0, 24, 0))

        self._pen_grid_minor = QPen()
        self._pen_grid_minor.setWidth(1)
        self._pen_grid_minor.setCosmetic(True)
        self._pen_grid_minor.setColor(QColor(0, 40, 0))

        self._pen_grid_medium = QPen()
        self._pen_grid_medium.setWidth(2)
        self._pen_grid_medium.setCosmetic(True)
        self._pen_grid_medium.setColor(QColor(0, 48, 0))

        self._pen_grid_major = QPen()
        self._pen_grid_major.setWidth(3)
        self._pen_grid_major.setCosmetic(True)
        self._pen_grid_major.setColor(QColor(0, 56, 0))

        self._pen_grid_axis = QPen()
        self._pen_grid_axis.setWidth(3)
        self._pen_grid_axis.setCosmetic(True)
        self._pen_grid_axis.setColor(QColor(0, 80, 0))

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)

        # Calculate necessary grid with a bit of overshoot
        # - this avoids edge glitches of background fill
        # - this ensures all necessary grid lines are included
        r = QRect(
            rect.left() - self.grid_minor() - rect.left() % self.grid_minor(),
            rect.top() - self.grid_minor() - rect.top() % self.grid_minor(),
            rect.width() + 2 * (self.grid_minor() + rect.width() % self.grid_minor()),
            rect.height() + 2 * (self.grid_minor() + rect.height() % self.grid_minor())
        )

        # Fill the background
        painter.setBrush(self._brush_background)
        painter.drawRect(r)

        # Calculate necessary grid lines and sort them into bins
        lines_minor = []
        lines_medium = []
        lines_major = []
        lines_axis = []
        for x in range(r.left(), r.right(), self.grid_minor()):
            line = QLineF(x, r.top(), x, r.bottom())
            if not x % self.grid_major():
                lines_major.append(line)
            elif not x % self.grid_medium():
                lines_medium.append(line)
            else:
                lines_minor.append(line)
        for y in range(r.top(), r.bottom(), self.grid_minor()):
            line = QLineF(r.left(), y, r.right(), y)
            if not y % self.grid_major():
                lines_major.append(line)
            elif not y % self.grid_medium():
                lines_medium.append(line)
            else:
                lines_minor.append(line)
        # Axis lines are simpler
        lines_axis.append(QLineF(0, r.top(), 0, r.bottom()))
        lines_axis.append(QLineF(r.left(), 0, r.right(), 0))
        # Draw in order from minor to axis, so bright lines aren't chopped up by darker ones
        pens_and_lines = [
            (self._pen_grid_minor, lines_minor),
            (self._pen_grid_medium, lines_medium),
            (self._pen_grid_major, lines_major),
            (self._pen_grid_axis, lines_axis)
        ]
        # TODO Might it be faster to pre-calculate all of the above (even if lines need to be longer)?
        for (pen, lines) in pens_and_lines:
            painter.setPen(pen)
            for line in lines:
                painter.drawLine(line)


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
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        self._zoom = self.transform().m11()
