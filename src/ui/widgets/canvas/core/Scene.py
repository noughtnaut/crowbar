from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QLineF, QPoint, QRect
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsScene

from src.ui.widgets.canvas.Condition import Condition
from src.ui.widgets.canvas.Operation import Operation
from src.ui.widgets.canvas.Trigger import Trigger
from src.ui.widgets.canvas.core.Enums import Mode, Socket
from src.ui.widgets.canvas.core.Wire import Wire


class CanvasScene(QGraphicsScene):
    _grid_line_increment = 20
    _grid_snap_increment = 20

    def __init__(self):
        super().__init__()
        self.setSceneRect(-5000, -500, 10000, 10000)  # TODO This should be set outside of Canvas
        # TODO Ideally, the canvas should be 'boundless', adjusted on the fly as needed, with no scroll bars
        self._prepare_background()
        self.create_sample_flow()
        # self.create_test_flows()

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
        self._pen_grid_dot.setColor(QColor(0, 96, 0))

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
            int(rect.left() - self.grid_minor() - rect.left() % self.grid_minor()),
            int(rect.top() - self.grid_minor() - rect.top() % self.grid_minor()),
            int(rect.width() + 2 * (self.grid_minor() + rect.width() % self.grid_minor())),
            int(rect.height() + 2 * (self.grid_minor() + rect.height() % self.grid_minor()))
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
        # Draw in minor>medium>major>axis order so brighter lines aren't chopped up by darker ones
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
        wire3 = Wire(self, box_condition, Socket.RIGHT,
                     box_action2, Socket.LEFT,
                     Mode.FALSE)
        self.addItem(wire1)
        self.addItem(wire2)
        self.addItem(wire3)

    def create_test_flows(self):
        # I-shaped routes
        point_i_base = QPoint(0, 0)
        point_i_t = QPoint(0, -120)
        point_i_b = QPoint(0, 120)
        point_i_l = QPoint(-120, 0)
        point_i_r = QPoint(120, 0)
        box_i_base = Trigger(point_i_base, 'I')
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

        # L-shaped routes (inside/direct route)
        point_li_base = QPoint(400, 0)
        point_li_tr = QPoint(520, -120)
        point_li_bl = QPoint(280, 120)
        point_li_tl = QPoint(280, -120)
        point_li_br = QPoint(520, 120)
        box_li_base = Trigger(point_li_base, 'LI')
        box_li_tr = Operation(point_li_tr, 'LI_tr')
        box_li_bl = Operation(point_li_bl, 'LI_bl')
        box_li_tl = Operation(point_li_tl, 'LI_tl')
        box_li_br = Operation(point_li_br, 'LI_br')
        self.addItem(box_li_base)
        self.addItem(box_li_tr)
        self.addItem(box_li_bl)
        self.addItem(box_li_tl)
        self.addItem(box_li_br)
        wire_li_tr = Wire(self, box_li_base, Socket.TOP,
                          box_li_tr, Socket.LEFT,
                          Mode.TRUE)
        wire_li_bl = Wire(self, box_li_base, Socket.BOTTOM,
                          box_li_bl, Socket.RIGHT,
                          Mode.FALSE)
        wire_li_tl = Wire(self, box_li_base, Socket.LEFT,
                          box_li_tl, Socket.BOTTOM,
                          Mode.ERROR)
        wire_li_br = Wire(self, box_li_base, Socket.RIGHT,
                          box_li_br, Socket.TOP,
                          Mode.NORMAL)
        self.addItem(wire_li_tr)
        self.addItem(wire_li_bl)
        self.addItem(wire_li_tl)
        self.addItem(wire_li_br)

        # L-shaped routes (outside/indirect route)
        point_lo_base = QPoint(800, 0)
        point_lo_tr = QPoint(910, -120)
        point_lo_bl = QPoint(690, 120)
        point_lo_tl = QPoint(690, -120)
        point_lo_br = QPoint(910, 120)
        box_lo_base = Trigger(point_lo_base, 'LO')
        box_lo_tr = Operation(point_lo_tr, 'LO_t')
        box_lo_bl = Operation(point_lo_bl, 'LO_b')
        box_lo_tl = Operation(point_lo_tl, 'LO_l')
        box_lo_br = Operation(point_lo_br, 'LO_r')
        self.addItem(box_lo_base)
        self.addItem(box_lo_tr)
        self.addItem(box_lo_bl)
        self.addItem(box_lo_tl)
        self.addItem(box_lo_br)
        wire_lo_tr = Wire(self, box_lo_base, Socket.LEFT,
                          box_lo_tr, Socket.TOP,
                          Mode.TRUE)
        wire_lo_bl = Wire(self, box_lo_base, Socket.RIGHT,
                          box_lo_bl, Socket.BOTTOM,
                          Mode.FALSE)
        wire_lo_tl = Wire(self, box_lo_base, Socket.BOTTOM,
                          box_lo_tl, Socket.LEFT,
                          Mode.ERROR)
        wire_lo_br = Wire(self, box_lo_base, Socket.TOP,
                          box_lo_br, Socket.RIGHT,
                          Mode.NORMAL)
        self.addItem(wire_lo_tr)
        self.addItem(wire_lo_bl)
        self.addItem(wire_lo_tl)
        self.addItem(wire_lo_br)

        # Z-shaped routes
        point_z_base = QPoint(0, 400)
        point_z_tr = QPoint(120, 280)
        point_z_bl = QPoint(-120, 520)
        point_z_tl = QPoint(-120, 280)
        point_z_br = QPoint(120, 520)
        box_z_base = Trigger(point_z_base, 'Z')
        box_z_tr = Operation(point_z_tr, 'Z_tr')
        box_z_bl = Operation(point_z_bl, 'Z_bl')
        box_z_tl = Operation(point_z_tl, 'Z_tl')
        box_z_br = Operation(point_z_br, 'Z_br')
        self.addItem(box_z_base)
        self.addItem(box_z_tr)
        self.addItem(box_z_bl)
        self.addItem(box_z_tl)
        self.addItem(box_z_br)
        wire_z_tr = Wire(self, box_z_base, Socket.TOP,
                         box_z_tr, Socket.BOTTOM,
                         Mode.TRUE)
        wire_z_bl = Wire(self, box_z_base, Socket.BOTTOM,
                         box_z_bl, Socket.TOP,
                         Mode.FALSE)
        wire_z_tl = Wire(self, box_z_base, Socket.LEFT,
                         box_z_tl, Socket.RIGHT,
                         Mode.ERROR)
        wire_z_br = Wire(self, box_z_base, Socket.RIGHT,
                         box_z_br, Socket.LEFT,
                         Mode.NORMAL)
        self.addItem(wire_z_tr)
        self.addItem(wire_z_bl)
        self.addItem(wire_z_tl)
        self.addItem(wire_z_br)

        # S-shaped routes
        point_s_base = QPoint(400, 400)
        point_s_tr = QPoint(520, 280)
        point_s_bl = QPoint(280, 520)
        point_s_tl = QPoint(280, 280)
        point_s_br = QPoint(520, 520)
        box_s_base = Trigger(point_s_base, 'S')
        box_s_tr = Operation(point_s_tr, 'S_tr')
        box_s_bl = Operation(point_s_bl, 'S_bl')
        box_s_tl = Operation(point_s_tl, 'S_tl')
        box_s_br = Operation(point_s_br, 'S_br')
        self.addItem(box_s_base)
        self.addItem(box_s_tr)
        self.addItem(box_s_bl)
        self.addItem(box_s_tl)
        self.addItem(box_s_br)
        wire_s_tr = Wire(self, box_s_base, Socket.BOTTOM,
                         box_s_tr, Socket.TOP,
                         Mode.TRUE)
        wire_s_bl = Wire(self, box_s_base, Socket.TOP,
                         box_s_bl, Socket.BOTTOM,
                         Mode.FALSE)
        wire_s_tl = Wire(self, box_s_base, Socket.RIGHT,
                         box_s_tl, Socket.LEFT,
                         Mode.ERROR)
        wire_s_br = Wire(self, box_s_base, Socket.LEFT,
                         box_s_br, Socket.RIGHT,
                         Mode.NORMAL)
        self.addItem(wire_s_tr)
        self.addItem(wire_s_bl)
        self.addItem(wire_s_tl)
        self.addItem(wire_s_br)

        # C-shaped routes, destination
        point_ca_base = QPoint(0, 800)
        point_ca_tr = QPoint(120, 680)
        point_ca_bl = QPoint(-120, 920)
        point_ca_tl = QPoint(-120, 680)
        point_ca_br = QPoint(120, 920)
        box_ca_base = Trigger(point_ca_base, 'Ca')
        box_ca_tr = Operation(point_ca_tr, 'Ca_tr')
        box_ca_bl = Operation(point_ca_bl, 'Ca_bl')
        box_ca_tl = Operation(point_ca_tl, 'Ca_tl')
        box_ca_br = Operation(point_ca_br, 'Ca_br')
        self.addItem(box_ca_base)
        self.addItem(box_ca_tr)
        self.addItem(box_ca_bl)
        self.addItem(box_ca_tl)
        self.addItem(box_ca_br)
        wire_ca_tr = Wire(self, box_ca_base, Socket.TOP,
                          box_ca_tr, Socket.TOP,
                          Mode.TRUE)
        wire_ca_bl = Wire(self, box_ca_base, Socket.BOTTOM,
                          box_ca_bl, Socket.BOTTOM,
                          Mode.FALSE)
        wire_ca_tl = Wire(self, box_ca_base, Socket.LEFT,
                          box_ca_tl, Socket.LEFT,
                          Mode.ERROR)
        wire_ca_br = Wire(self, box_ca_base, Socket.RIGHT,
                          box_ca_br, Socket.RIGHT,
                          Mode.NORMAL)
        self.addItem(wire_ca_tr)
        self.addItem(wire_ca_bl)
        self.addItem(wire_ca_tl)
        self.addItem(wire_ca_br)

        # C-shaped routes, source
        point_cb_base = QPoint(400, 800)
        point_cb_tr = QPoint(520, 680)
        point_cb_bl = QPoint(280, 920)
        point_cb_tl = QPoint(280, 680)
        point_cb_br = QPoint(520, 920)
        box_cb_base = Trigger(point_cb_base, 'Cb')
        box_cb_tr = Operation(point_cb_tr, 'Cb_tr')
        box_cb_bl = Operation(point_cb_bl, 'Cb_bl')
        box_cb_tl = Operation(point_cb_tl, 'Cb_tl')
        box_cb_br = Operation(point_cb_br, 'Cb_br')
        self.addItem(box_cb_base)
        self.addItem(box_cb_tr)
        self.addItem(box_cb_bl)
        self.addItem(box_cb_tl)
        self.addItem(box_cb_br)
        wire_cb_tr = Wire(self, box_cb_base, Socket.BOTTOM,
                          box_cb_tr, Socket.BOTTOM,
                          Mode.TRUE)
        wire_cb_bl = Wire(self, box_cb_base, Socket.TOP,
                          box_cb_bl, Socket.TOP,
                          Mode.FALSE)
        wire_cb_tl = Wire(self, box_cb_base, Socket.RIGHT,
                          box_cb_tl, Socket.RIGHT,
                          Mode.ERROR)
        wire_cb_br = Wire(self, box_cb_base, Socket.LEFT,
                          box_cb_br, Socket.LEFT,
                          Mode.NORMAL)
        self.addItem(wire_cb_tr)
        self.addItem(wire_cb_bl)
        self.addItem(wire_cb_tl)
        self.addItem(wire_cb_br)

        # C-shaped routes, when an S-shape needs to wrap
        point_cs_base = QPoint(800, 800)
        point_cs_tr = QPoint(880, 680)
        point_cs_bl = QPoint(720, 920)
        point_cs_tl = QPoint(680, 720)
        point_cs_br = QPoint(920, 880)
        box_cs_base = Trigger(point_cs_base, 'C (S-wrap)')
        box_cs_tr = Operation(point_cs_tr, 'CS_tr')
        box_cs_bl = Operation(point_cs_bl, 'CS_bl')
        box_cs_tl = Operation(point_cs_tl, 'CS_tl')
        box_cs_br = Operation(point_cs_br, 'CS_br')
        self.addItem(box_cs_base)
        self.addItem(box_cs_tr)
        self.addItem(box_cs_bl)
        self.addItem(box_cs_tl)
        self.addItem(box_cs_br)
        wire_cs_tr = Wire(self, box_cs_base, Socket.BOTTOM,
                          box_cs_tr, Socket.TOP,
                          Mode.TRUE)
        wire_cs_bl = Wire(self, box_cs_base, Socket.TOP,
                          box_cs_bl, Socket.BOTTOM,
                          Mode.FALSE)
        wire_cs_tl = Wire(self, box_cs_base, Socket.RIGHT,
                          box_cs_tl, Socket.LEFT,
                          Mode.ERROR)
        wire_cs_br = Wire(self, box_cs_base, Socket.LEFT,
                          box_cs_br, Socket.RIGHT,
                          Mode.NORMAL)
        self.addItem(wire_cs_tr)
        self.addItem(wire_cs_bl)
        self.addItem(wire_cs_tl)
        self.addItem(wire_cs_br)
