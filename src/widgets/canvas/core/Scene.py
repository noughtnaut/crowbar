from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QLineF, QPoint, QRect
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsScene


class CanvasScene(QGraphicsScene):
    _grid_line_increment = 20
    _grid_snap_increment = 20

    def __init__(self):
        super().__init__()
        self.setSceneRect(-5000, -500, 10000, 10000)  # TODO This should be set outside of Canvas
        # TODO Ideally, the canvas should be 'boundless', adjusted on the fly as needed, with no scroll bars
        self._prepare_background()

    def grid_snap_increment(self):
        return self._grid_snap_increment

    def grid_minor(self):
        return self._grid_line_increment

    def grid_medium(self):
        return self.grid_minor() * 2

    def grid_major(self):
        return self.grid_medium() * 4

    def _prepare_background(self):
        self._brush_background = QBrush(QColor(0, 24, 0))
        self._prepare_background_dots()
        # self._prepare_background_grid()

    def _prepare_background_dots(self):
        self._pen_grid_dot = QPen()
        self._pen_grid_dot.setWidth(1)
        self._pen_grid_dot.setCosmetic(True)
        self._pen_grid_dot.setColor(QColor(0, 64, 0))

    def _prepare_background_grid(self):
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
        painter.setRenderHint(QPainter.Antialiasing)

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
        self._draw_background_dots(painter, r)
        # self._draw_background_grid(painter, r)

    def _draw_background_dots(self, painter: QtGui.QPainter, r: QRect):
        painter.setPen(self._pen_grid_dot)
        for x in range(r.left(), r.right(), self.grid_minor()):
            for y in range(r.top(), r.bottom(), self.grid_minor()):
                painter.drawPoint(QPoint(x, y))

    def _draw_background_grid(self, painter: QtGui.QPainter, r: QtCore.QRect) -> None:
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
