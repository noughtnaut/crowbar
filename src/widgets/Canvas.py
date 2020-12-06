import sys

from PyQt5.QtGui import QColor, QPainter, QPen, QWheelEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget

if 'PyQt5' in sys.modules:
    from PyQt5 import QtGui, QtWidgets
    from PyQt5.QtCore import Qt, QPoint, QRect

else:
    from PySide2 import QtGui, QtWidgets
    from PySide2.QtCore import Qt


# QGraphicsAnchorLayout
# QGraphicsScene
# The QGraphicsScene class provides a surface for managing a large number of 2D graphical items. More

class Canvas(QWidget):
    """
    The Canvas provides a surface for drawing upon. It handles view transformations (panning,
    zooming, etc.) You can place Shape elements on the Canvas, and Shapes may then be subsequently
    moved about and otherwise edited.
    """
    _config_canvas_background_color = QColor.fromRgb(16, 32, 16)  # dark green
    _config_canvas_grid_color = QtGui.QColor('darkgreen')
    _config_canvas_grid_size = 25
    _view_offset = QPoint(20, 200)
    _view_pan_from = QPoint(0, 0)
    _view_pan_to = QPoint(0, 0)
    _is_panning = False

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )
        self.setCursor(Qt.OpenHandCursor)
        self.setMouseTracking(True)
        self._view_offset = QPoint(50, 200)

    def paintEvent(self, e):
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing)
            self.paint_background(painter)
            self.paint_grid(painter)
            self.paint_contents(painter)
            self.paint_transform(painter)

    def paint_background(self, painter: QPainter):
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), self._config_canvas_background_color)
        p.setColor(self.foregroundRole(), self._config_canvas_grid_color)
        self.setPalette(p)

    def paint_grid(self, painter: QPainter):
        # Draw a pattern of grid intersections/dots
        # TODO Better done as pattern or hatch, so it is boundless
        pen = QPen()
        pen.setCosmetic(True)
        pen.setColor(self._config_canvas_grid_color)
        painter.setPen(pen)
        for i in range(1, 50):
            x = i * self._config_canvas_grid_size
            for j in range(1, 50):
                y = j * self._config_canvas_grid_size
                painter.drawLine(x, y - 3, x, y + 3)
                painter.drawLine(x - 3, y, x + 3, y)

        # Draw origin
        pen.setColor(QtGui.QColor('yellow'))
        painter.setPen(pen)
        painter.drawLine(0, -3, 0, 3)
        painter.drawLine(-3, 0, 3, 0)

        # Draw a vector while panning
        if self._is_panning:
            pen.setColor(QtGui.QColor('brown'))
            pen.setDashPattern([3, 7])
            painter.setPen(pen)
            painter.drawLine(self._view_pan_from, self._view_pan_to)
            painter.drawText(self._view_pan_to, "Pan offset")

    def paint_contents(self, painter: QPainter):
        pass

    def paint_transform(self, painter: QPainter):
        transform = painter.worldTransform()
        transform.translate(50, 35)
        transform.translate(self._view_offset.x(), self._view_offset.y())
        # transform.scale(self._view_zoom/100, self._view_zoom/100)
        painter.setWorldTransform(transform)
        pass

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            print("Click")
        elif event.button() == Qt.RightButton:
            print("Click-right")
        elif event.button() == Qt.MiddleButton:
            print("Click-middle")
        elif event.button() == Qt.BackButton:
            print("Click-back")
        elif event.button() == Qt.ForwardButton:
            print("Click-fwd")
        else:
            print("Click:", event.button())

        if event.button() == Qt.LeftButton:
            self._view_pan_from = event.pos()
            self._view_pan_to = self._view_pan_from
            self._is_panning = True
            self.setCursor(Qt.ClosedHandCursor)
            self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        print("Cli-click")
        pass

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_panning and event.button() == Qt.LeftButton:
            self._view_pan_from = QPoint(0, 0)
            self._view_pan_to = QPoint(0, 0)
            self._is_panning = False
            self.setCursor(Qt.OpenHandCursor)
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_panning:
            self._view_pan_to = event.pos()
            # self._view_offset = self._view_offset + self._view_pan_to - self._view_pan_from
            # print('offset: ', self._view_offset.x(), self._view_offset.y())
            self.update()

    def wheelEvent(self, event: QWheelEvent):
        print("Wheeee!", event.angleDelta().y())
        # if self.with_control_key(event: QMouseEvent):
        #     self.zoom_adjust(event.angleDelta().y())

    # def zoom_adjust(self, adjustment: float):
    #     if not self._view_zoom_granularity_mouse:
    #         self._view_zoom_granularity_mouse = abs(adjustment)/self._view_zoom_granularity
    #
    #     adjustment = -self._view_zoom_granularity_mouse - adjustment
    #
    #     self._view_zoom = self._view_zoom * adjustment
    #     print("Zoom level: ", self._view_zoom)
    #     self.update()
    #
    # def with_control_key(self, event: QMouseEvent) -> bool:
    #     return event.modifiers() & Qt.ControlModifier
    #
    # def with_alt_key(self, event: QMouseEvent) -> bool:
    #     return event.modifiers() & Qt.AltModifier
    #
    # def with_shift_key(self, event: QMouseEvent) -> bool:
    #     return event.modifiers() & Qt.ShiftModifier


class Block(QWidget):
    """
    The Block is ... a block.
    """

    pos = QPoint()

    def __init__(self, cfg, x: int, y: int):
        super().__init__()
        self.cfg = cfg
        self.pos = QPoint(x, y)
        self.setFixedSize(100, 75)

    def paintEvent(self, e):
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen()
            pen.setCosmetic(True)
            pen.setWidth(2)
            pen.setColor(QtGui.QColor('blue'))
            painter.setPen(pen)
            rect = QRect(self.pos.x(), self.pos.y(), self.pos.x()+100, self.pos.y()+50)
            painter.drawRoundedRect(rect, 5, 5, )
