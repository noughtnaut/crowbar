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
        point_i_top = QPoint(0, -120)
        point_i_down = QPoint(0, 120)
        point_i_left = QPoint(-120, 0)
        point_i_right = QPoint(120, 0)
        box_i_base = Operation(point_i_base, 'I')
        box_i_top = Operation(point_i_top, 'I_top')
        box_i_down = Operation(point_i_down, 'I_down')
        box_i_left = Operation(point_i_left, 'I_left')
        box_i_right = Operation(point_i_right, 'I_right')
        self.addItem(box_i_base)
        self.addItem(box_i_top)
        self.addItem(box_i_down)
        self.addItem(box_i_left)
        self.addItem(box_i_right)
        wire_i_top = Wire(self, box_i_base, Socket.TOP,
                          box_i_top, Socket.BOTTOM,
                          Mode.TRUE)
        wire_i_down = Wire(self, box_i_base, Socket.BOTTOM,
                           box_i_down, Socket.TOP,
                           Mode.FALSE)
        wire_i_left = Wire(self, box_i_base, Socket.LEFT,
                           box_i_left, Socket.RIGHT,
                           Mode.ERROR)
        wire_i_right = Wire(self, box_i_base, Socket.RIGHT,
                            box_i_right, Socket.LEFT,
                            Mode.NORMAL)
        self.addItem(wire_i_top)
        self.addItem(wire_i_down)
        self.addItem(wire_i_left)
        self.addItem(wire_i_right)

        # L-shaped routes
        point_l_base = QPoint(400, 0)
        point_l_topright = QPoint(520, -120)
        point_l_bottomleft = QPoint(280, 120)
        point_l_lefttop = QPoint(280, -120)
        point_l_rightbottom = QPoint(520, 120)
        box_l_base = Operation(point_l_base, 'L')
        box_l_topright = Operation(point_l_topright, 'L_topright')
        box_l_bottomleft = Operation(point_l_bottomleft, 'L_bottomleft')
        box_l_lefttop = Operation(point_l_lefttop, 'L_lefttop')
        box_l_rightbottom = Operation(point_l_rightbottom, 'L_rightbottom')
        self.addItem(box_l_base)
        self.addItem(box_l_topright)
        self.addItem(box_l_bottomleft)
        self.addItem(box_l_lefttop)
        self.addItem(box_l_rightbottom)
        wire_l_topright = Wire(self, box_l_base, Socket.TOP,
                               box_l_topright, Socket.LEFT,
                               Mode.TRUE)
        wire_l_bottomleft = Wire(self, box_l_base, Socket.BOTTOM,
                                 box_l_bottomleft, Socket.RIGHT,
                                 Mode.FALSE)
        wire_l_lefttop = Wire(self, box_l_base, Socket.LEFT,
                              box_l_lefttop, Socket.BOTTOM,
                              Mode.ERROR)
        wire_l_rightbottom = Wire(self, box_l_base, Socket.RIGHT,
                                  box_l_rightbottom, Socket.TOP,
                                  Mode.NORMAL)
        self.addItem(wire_l_topright)
        self.addItem(wire_l_bottomleft)
        self.addItem(wire_l_lefttop)
        self.addItem(wire_l_rightbottom)

        # Z-shaped routes
        point_z_base = QPoint(0, 400)
        point_z_topright = QPoint(120, 280)
        point_z_bottomleft = QPoint(-120, 520)
        point_z_lefttop = QPoint(-120, 280)
        point_z_rightbottom = QPoint(120, 520)
        box_z_base = Operation(point_z_base, 'Z')
        box_z_topright = Operation(point_z_topright, 'Z_topright')
        box_z_bottomleft = Operation(point_z_bottomleft, 'Z_bottomleft')
        box_z_lefttop = Operation(point_z_lefttop, 'Z_lefttop')
        box_z_rightbottom = Operation(point_z_rightbottom, 'Z_rightbottom')
        self.addItem(box_z_base)
        self.addItem(box_z_topright)
        self.addItem(box_z_bottomleft)
        self.addItem(box_z_lefttop)
        self.addItem(box_z_rightbottom)
        wire_z_topright = Wire(self, box_z_base, Socket.TOP,
                               box_z_topright, Socket.BOTTOM,
                               Mode.TRUE)
        wire_z_bottomleft = Wire(self, box_z_base, Socket.BOTTOM,
                                 box_z_bottomleft, Socket.TOP,
                                 Mode.FALSE)
        wire_z_lefttop = Wire(self, box_z_base, Socket.LEFT,
                              box_z_lefttop, Socket.RIGHT,
                              Mode.ERROR)
        wire_z_rightbottom = Wire(self, box_z_base, Socket.RIGHT,
                                  box_z_rightbottom, Socket.LEFT,
                                  Mode.NORMAL)
        self.addItem(wire_z_topright)
        self.addItem(wire_z_bottomleft)
        self.addItem(wire_z_lefttop)
        self.addItem(wire_z_rightbottom)

        # S-shaped routes
        point_s_base = QPoint(400, 400)
        point_s_topright = QPoint(520, 280)
        point_s_bottomleft = QPoint(280, 520)
        point_s_lefttop = QPoint(280, 280)
        point_s_rightbottom = QPoint(520, 520)
        box_s_base = Operation(point_s_base, 'S')
        box_s_topright = Operation(point_s_topright, 'S_topright')
        box_s_bottomleft = Operation(point_s_bottomleft, 'S_bottomleft')
        box_s_lefttop = Operation(point_s_lefttop, 'S_lefttop')
        box_s_rightbottom = Operation(point_s_rightbottom, 'S_rightbottom')
        self.addItem(box_s_base)
        self.addItem(box_s_topright)
        self.addItem(box_s_bottomleft)
        self.addItem(box_s_lefttop)
        self.addItem(box_s_rightbottom)
        wire_s_topright = Wire(self, box_s_base, Socket.BOTTOM,
                               box_s_topright, Socket.TOP,
                               Mode.TRUE)
        wire_s_bottomleft = Wire(self, box_s_base, Socket.TOP,
                                 box_s_bottomleft, Socket.BOTTOM,
                                 Mode.FALSE)
        wire_s_lefttop = Wire(self, box_s_base, Socket.RIGHT,
                              box_s_lefttop, Socket.LEFT,
                              Mode.ERROR)
        wire_s_rightbottom = Wire(self, box_s_base, Socket.LEFT,
                                  box_s_rightbottom, Socket.RIGHT,
                                  Mode.NORMAL)
        self.addItem(wire_s_topright)
        self.addItem(wire_s_bottomleft)
        self.addItem(wire_s_lefttop)
        self.addItem(wire_s_rightbottom)

        # C-shaped routes, destination
        point_ca_base = QPoint(0, 800)
        point_ca_topright = QPoint(120, 680)
        point_ca_bottomleft = QPoint(-120, 920)
        point_ca_lefttop = QPoint(-120, 680)
        point_ca_rightbottom = QPoint(120, 920)
        box_ca_base = Operation(point_ca_base, 'Ca')
        box_ca_topright = Operation(point_ca_topright, 'Ca_topright')
        box_ca_bottomleft = Operation(point_ca_bottomleft, 'Ca_bottomleft')
        box_ca_lefttop = Operation(point_ca_lefttop, 'Ca_lefttop')
        box_ca_rightbottom = Operation(point_ca_rightbottom, 'Ca_rightbottom')
        self.addItem(box_ca_base)
        self.addItem(box_ca_topright)
        self.addItem(box_ca_bottomleft)
        self.addItem(box_ca_lefttop)
        self.addItem(box_ca_rightbottom)
        wire_ca_topright = Wire(self, box_ca_base, Socket.TOP,
                                box_ca_topright, Socket.TOP,
                                Mode.TRUE)
        wire_ca_bottomleft = Wire(self, box_ca_base, Socket.BOTTOM,
                                  box_ca_bottomleft, Socket.BOTTOM,
                                  Mode.FALSE)
        wire_ca_lefttop = Wire(self, box_ca_base, Socket.LEFT,
                               box_ca_lefttop, Socket.LEFT,
                               Mode.ERROR)
        wire_ca_rightbottom = Wire(self, box_ca_base, Socket.RIGHT,
                                   box_ca_rightbottom, Socket.RIGHT,
                                   Mode.NORMAL)
        self.addItem(wire_ca_topright)
        self.addItem(wire_ca_bottomleft)
        self.addItem(wire_ca_lefttop)
        self.addItem(wire_ca_rightbottom)

        # C-shaped routes, source
        point_cb_base = QPoint(400, 800)
        point_cb_topright = QPoint(520, 680)
        point_cb_bottomleft = QPoint(280, 920)
        point_cb_lefttop = QPoint(280, 680)
        point_cb_rightbottom = QPoint(520, 920)
        box_cb_base = Operation(point_cb_base, 'Cb')
        box_cb_topright = Operation(point_cb_topright, 'Cb_topright')
        box_cb_bottomleft = Operation(point_cb_bottomleft, 'Cb_bottomleft')
        box_cb_lefttop = Operation(point_cb_lefttop, 'Cb_lefttop')
        box_cb_rightbottom = Operation(point_cb_rightbottom, 'Cb_rightbottom')
        self.addItem(box_cb_base)
        self.addItem(box_cb_topright)
        self.addItem(box_cb_bottomleft)
        self.addItem(box_cb_lefttop)
        self.addItem(box_cb_rightbottom)
        wire_cb_topright = Wire(self, box_cb_base, Socket.BOTTOM,
                                box_cb_topright, Socket.BOTTOM,
                                Mode.TRUE)
        wire_cb_bottomleft = Wire(self, box_cb_base, Socket.TOP,
                                  box_cb_bottomleft, Socket.TOP,
                                  Mode.FALSE)
        wire_cb_lefttop = Wire(self, box_cb_base, Socket.RIGHT,
                               box_cb_lefttop, Socket.RIGHT,
                               Mode.ERROR)
        wire_cb_rightbottom = Wire(self, box_cb_base, Socket.LEFT,
                                   box_cb_rightbottom, Socket.LEFT,
                                   Mode.NORMAL)
        self.addItem(wire_cb_topright)
        self.addItem(wire_cb_bottomleft)
        self.addItem(wire_cb_lefttop)
        self.addItem(wire_cb_rightbottom)

        # C-shaped routes, when an S-shape needs to wrap
        point_cs_base = QPoint(800, 800)
        point_cs_topright = QPoint(910, 690)
        point_cs_bottomleft = QPoint(690, 910)
        point_cs_lefttop = QPoint(690, 690)
        point_cs_rightbottom = QPoint(910, 910)
        box_cs_base = Operation(point_cs_base, 'C (S-wrap)')
        box_cs_topright = Operation(point_cs_topright, 'CS_topright')
        box_cs_bottomleft = Operation(point_cs_bottomleft, 'CS_bottomleft')
        box_cs_lefttop = Operation(point_cs_lefttop, 'CS_lefttop')
        box_cs_rightbottom = Operation(point_cs_rightbottom, 'CS_rightbottom')
        self.addItem(box_cs_base)
        self.addItem(box_cs_topright)
        self.addItem(box_cs_bottomleft)
        self.addItem(box_cs_lefttop)
        self.addItem(box_cs_rightbottom)
        wire_cs_topright = Wire(self, box_cs_base, Socket.BOTTOM,
                                box_cs_topright, Socket.TOP,
                                Mode.TRUE)
        wire_cs_bottomleft = Wire(self, box_cs_base, Socket.TOP,
                                  box_cs_bottomleft, Socket.BOTTOM,
                                  Mode.FALSE)
        wire_cs_lefttop = Wire(self, box_cs_base, Socket.RIGHT,
                               box_cs_lefttop, Socket.LEFT,
                               Mode.ERROR)
        wire_cs_rightbottom = Wire(self, box_cs_base, Socket.LEFT,
                                   box_cs_rightbottom, Socket.RIGHT,
                                   Mode.NORMAL)
        self.addItem(wire_cs_topright)
        self.addItem(wire_cs_bottomleft)
        self.addItem(wire_cs_lefttop)
        self.addItem(wire_cs_rightbottom)
