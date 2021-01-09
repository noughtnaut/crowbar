from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QLineF, QPoint, QRect
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsScene

from widgets.canvas.Condition import Condition
from widgets.canvas.Operation import Operation
from widgets.canvas.Trigger import Trigger
from widgets.canvas.core.Enums import Mode, Socket
from widgets.canvas.core.Wire import Wire


class CanvasScene(QGraphicsScene):
    _grid_line_increment = 20
    _grid_snap_increment = 20

    def __init__(self):
        super().__init__()
        self.setSceneRect(-5000, -500, 10000, 10000)  # TODO This should be set outside of Canvas
        # TODO Ideally, the canvas should be 'boundless', adjusted on the fly as needed, with no scroll bars
        self._prepare_background()
        # self.create_sample_flow()
        self.create_test_flows()

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
        # Draw in order from minor to axis, so br lines aren't chopped t by darker ones
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

    def create_sample_flow(self):
        # TODO Find a better place for the Trigger, which should be a fixture rather than part of a 'sample'.
        point1 = QPoint(0, 0)
        point2 = QPoint(0, 160)
        point3 = QPoint(0, 320)
        point4 = QPoint(160, 320)
        box_trigger = Trigger(point1, 'Trigger')
        box_condition = Condition(point2, 'Condition')
        box_action1 = Operation(point3, 'Action 1')
        box_action2 = Operation(point4, 'Action 2')
        self.addItem(box_trigger)
        self.addItem(box_condition)
        self.addItem(box_action1)
        self.addItem(box_action2)

        wire1 = Wire(self, box_trigger, Socket.BOTTOM,
                     box_condition, Socket.TOP)
        wire2 = Wire(self, box_condition, Socket.BOTTOM,
                     box_action1, Socket.TOP,
                     Mode.TRUE)
        wire3 = Wire(self, box_condition, Socket.TOP,
                     box_action2, Socket.LEFT,
                     Mode.FALSE)
        wire4 = Wire(self, box_condition, Socket.TOP,
                     box_action2, Socket.TOP,
                     Mode.NORMAL)
        wire5 = Wire(self, box_condition, Socket.TOP,
                     box_action2, Socket.RIGHT,
                     Mode.TRUE)
        wire6 = Wire(self, box_condition, Socket.TOP,
                     box_action2, Socket.BOTTOM,
                     Mode.ERROR)
        self.addItem(wire1)
        self.addItem(wire2)
        self.addItem(wire3)
        self.addItem(wire4)
        self.addItem(wire5)
        self.addItem(wire6)

    def create_test_flows(self):
        # I-shaped routes
        point_i_base = QPoint(0, 0)
        point_i_t = QPoint(0, -120)
        point_i_b = QPoint(0, 120)
        point_i_l = QPoint(-120, 0)
        point_i_r = QPoint(120, 0)
        box_i_base = Operation(point_i_base, 'I')
        box_i_t = Operation(point_i_t, 'I_t')
        box_i_b = Operation(point_i_b, 'I_b')
        box_i_l = Operation(point_i_l, 'I_l')
        box_i_r = Operation(point_i_r, 'I_r')
        self.addItem(box_i_base)
        self.addItem(box_i_t)
        self.addItem(box_i_b)
        self.addItem(box_i_l)
        self.addItem(box_i_r)
        wire_i_t = Wire(self, box_i_base, Socket.TOP,
                        box_i_t, Socket.BOTTOM,
                        Mode.TRUE)
        wire_i_b = Wire(self, box_i_base, Socket.BOTTOM,
                        box_i_b, Socket.TOP,
                        Mode.FALSE)
        wire_i_l = Wire(self, box_i_base, Socket.LEFT,
                        box_i_l, Socket.RIGHT,
                        Mode.ERROR)
        wire_i_r = Wire(self, box_i_base, Socket.RIGHT,
                        box_i_r, Socket.LEFT,
                        Mode.NORMAL)
        self.addItem(wire_i_t)
        self.addItem(wire_i_b)
        self.addItem(wire_i_l)
        self.addItem(wire_i_r)

        # L-shaped routes
        point_l_base = QPoint(400, 0)
        point_l_tr = QPoint(520, -120)
        point_l_bl = QPoint(280, 120)
        point_l_lt = QPoint(280, -120)
        point_l_rb = QPoint(520, 120)
        box_l_base = Operation(point_l_base, 'L')
        box_l_tr = Operation(point_l_tr, 'L_tr')
        box_l_bl = Operation(point_l_bl, 'L_bl')
        box_l_lt = Operation(point_l_lt, 'L_lt')
        box_l_rb = Operation(point_l_rb, 'L_rb')
        self.addItem(box_l_base)
        self.addItem(box_l_tr)
        self.addItem(box_l_bl)
        self.addItem(box_l_lt)
        self.addItem(box_l_rb)
        wire_l_tr = Wire(self, box_l_base, Socket.TOP,
                         box_l_tr, Socket.LEFT,
                         Mode.TRUE)
        wire_l_bl = Wire(self, box_l_base, Socket.BOTTOM,
                         box_l_bl, Socket.RIGHT,
                         Mode.FALSE)
        wire_l_lt = Wire(self, box_l_base, Socket.LEFT,
                         box_l_lt, Socket.BOTTOM,
                         Mode.ERROR)
        wire_l_rb = Wire(self, box_l_base, Socket.RIGHT,
                         box_l_rb, Socket.TOP,
                         Mode.NORMAL)
        self.addItem(wire_l_tr)
        self.addItem(wire_l_bl)
        self.addItem(wire_l_lt)
        self.addItem(wire_l_rb)

        # Z-shaped routes
        point_z_base = QPoint(0, 400)
        point_z_tr = QPoint(120, 280)
        point_z_bl = QPoint(-120, 520)
        point_z_lt = QPoint(-120, 280)
        point_z_rb = QPoint(120, 520)
        box_z_base = Operation(point_z_base, 'Z')
        box_z_tr = Operation(point_z_tr, 'Z_tr')
        box_z_bl = Operation(point_z_bl, 'Z_bl')
        box_z_lt = Operation(point_z_lt, 'Z_lt')
        box_z_rb = Operation(point_z_rb, 'Z_rb')
        self.addItem(box_z_base)
        self.addItem(box_z_tr)
        self.addItem(box_z_bl)
        self.addItem(box_z_lt)
        self.addItem(box_z_rb)
        wire_z_tr = Wire(self, box_z_base, Socket.TOP,
                         box_z_tr, Socket.BOTTOM,
                         Mode.TRUE)
        wire_z_bl = Wire(self, box_z_base, Socket.BOTTOM,
                         box_z_bl, Socket.TOP,
                         Mode.FALSE)
        wire_z_lt = Wire(self, box_z_base, Socket.LEFT,
                         box_z_lt, Socket.RIGHT,
                         Mode.ERROR)
        wire_z_rb = Wire(self, box_z_base, Socket.RIGHT,
                         box_z_rb, Socket.LEFT,
                         Mode.NORMAL)
        self.addItem(wire_z_tr)
        self.addItem(wire_z_bl)
        self.addItem(wire_z_lt)
        self.addItem(wire_z_rb)

        # S-shaped routes
        point_s_base = QPoint(400, 400)
        point_s_tr = QPoint(520, 280)
        point_s_bl = QPoint(280, 520)
        point_s_lt = QPoint(280, 280)
        point_s_rb = QPoint(520, 520)
        box_s_base = Operation(point_s_base, 'S')
        box_s_tr = Operation(point_s_tr, 'S_tr')
        box_s_bl = Operation(point_s_bl, 'S_bl')
        box_s_lt = Operation(point_s_lt, 'S_lt')
        box_s_rb = Operation(point_s_rb, 'S_rb')
        self.addItem(box_s_base)
        self.addItem(box_s_tr)
        self.addItem(box_s_bl)
        self.addItem(box_s_lt)
        self.addItem(box_s_rb)
        wire_s_tr = Wire(self, box_s_base, Socket.BOTTOM,
                         box_s_tr, Socket.TOP,
                         Mode.TRUE)
        wire_s_bl = Wire(self, box_s_base, Socket.TOP,
                         box_s_bl, Socket.BOTTOM,
                         Mode.FALSE)
        wire_s_lt = Wire(self, box_s_base, Socket.RIGHT,
                         box_s_lt, Socket.LEFT,
                         Mode.ERROR)
        wire_s_rb = Wire(self, box_s_base, Socket.LEFT,
                         box_s_rb, Socket.RIGHT,
                         Mode.NORMAL)
        self.addItem(wire_s_tr)
        self.addItem(wire_s_bl)
        self.addItem(wire_s_lt)
        self.addItem(wire_s_rb)

        # C-shaped routes, destination
        point_ca_base = QPoint(0, 800)
        point_ca_tr = QPoint(120, 680)
        point_ca_bl = QPoint(-120, 920)
        point_ca_lt = QPoint(-120, 680)
        point_ca_rb = QPoint(120, 920)
        box_ca_base = Operation(point_ca_base, 'Ca')
        box_ca_tr = Operation(point_ca_tr, 'Ca_tr')
        box_ca_bl = Operation(point_ca_bl, 'Ca_bl')
        box_ca_lt = Operation(point_ca_lt, 'Ca_lt')
        box_ca_rb = Operation(point_ca_rb, 'Ca_rb')
        self.addItem(box_ca_base)
        self.addItem(box_ca_tr)
        self.addItem(box_ca_bl)
        self.addItem(box_ca_lt)
        self.addItem(box_ca_rb)
        wire_ca_tr = Wire(self, box_ca_base, Socket.TOP,
                          box_ca_tr, Socket.TOP,
                          Mode.TRUE)
        wire_ca_bl = Wire(self, box_ca_base, Socket.BOTTOM,
                          box_ca_bl, Socket.BOTTOM,
                          Mode.FALSE)
        wire_ca_lt = Wire(self, box_ca_base, Socket.LEFT,
                          box_ca_lt, Socket.LEFT,
                          Mode.ERROR)
        wire_ca_rb = Wire(self, box_ca_base, Socket.RIGHT,
                          box_ca_rb, Socket.RIGHT,
                          Mode.NORMAL)
        self.addItem(wire_ca_tr)
        self.addItem(wire_ca_bl)
        self.addItem(wire_ca_lt)
        self.addItem(wire_ca_rb)

        # C-shaped routes, source
        point_cb_base = QPoint(400, 800)
        point_cb_tr = QPoint(520, 680)
        point_cb_bl = QPoint(280, 920)
        point_cb_lt = QPoint(280, 680)
        point_cb_rb = QPoint(520, 920)
        box_cb_base = Operation(point_cb_base, 'Cb')
        box_cb_tr = Operation(point_cb_tr, 'Cb_tr')
        box_cb_bl = Operation(point_cb_bl, 'Cb_bl')
        box_cb_lt = Operation(point_cb_lt, 'Cb_lt')
        box_cb_rb = Operation(point_cb_rb, 'Cb_rb')
        self.addItem(box_cb_base)
        self.addItem(box_cb_tr)
        self.addItem(box_cb_bl)
        self.addItem(box_cb_lt)
        self.addItem(box_cb_rb)
        wire_cb_tr = Wire(self, box_cb_base, Socket.BOTTOM,
                          box_cb_tr, Socket.BOTTOM,
                          Mode.TRUE)
        wire_cb_bl = Wire(self, box_cb_base, Socket.TOP,
                          box_cb_bl, Socket.TOP,
                          Mode.FALSE)
        wire_cb_lt = Wire(self, box_cb_base, Socket.RIGHT,
                          box_cb_lt, Socket.RIGHT,
                          Mode.ERROR)
        wire_cb_rb = Wire(self, box_cb_base, Socket.LEFT,
                          box_cb_rb, Socket.LEFT,
                          Mode.NORMAL)
        self.addItem(wire_cb_tr)
        self.addItem(wire_cb_bl)
        self.addItem(wire_cb_lt)
        self.addItem(wire_cb_rb)

        # C-shaped routes, when an S-shape needs to wrap
        point_cs_base = QPoint(800, 800)
        point_cs_tr = QPoint(910, 690)
        point_cs_bl = QPoint(690, 910)
        point_cs_lt = QPoint(690, 690)
        point_cs_rb = QPoint(910, 910)
        box_cs_base = Operation(point_cs_base, 'C (S-wrap)')
        box_cs_tr = Operation(point_cs_tr, 'CS_tr')
        box_cs_bl = Operation(point_cs_bl, 'CS_bl')
        box_cs_lt = Operation(point_cs_lt, 'CS_lt')
        box_cs_rb = Operation(point_cs_rb, 'CS_rb')
        self.addItem(box_cs_base)
        self.addItem(box_cs_tr)
        self.addItem(box_cs_bl)
        self.addItem(box_cs_lt)
        self.addItem(box_cs_rb)
        wire_cs_tr = Wire(self, box_cs_base, Socket.BOTTOM,
                          box_cs_tr, Socket.TOP,
                          Mode.TRUE)
        wire_cs_bl = Wire(self, box_cs_base, Socket.TOP,
                          box_cs_bl, Socket.BOTTOM,
                          Mode.FALSE)
        wire_cs_lt = Wire(self, box_cs_base, Socket.RIGHT,
                          box_cs_lt, Socket.LEFT,
                          Mode.ERROR)
        wire_cs_rb = Wire(self, box_cs_base, Socket.LEFT,
                          box_cs_rb, Socket.RIGHT,
                          Mode.NORMAL)
        self.addItem(wire_cs_tr)
        self.addItem(wire_cs_bl)
        self.addItem(wire_cs_lt)
        self.addItem(wire_cs_rb)
