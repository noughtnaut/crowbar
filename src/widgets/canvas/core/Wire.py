import typing

from PyQt5 import QtGui
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsPolygonItem, QStyleOptionGraphicsItem, QWidget

from widgets.canvas.core import Component, Scene
from widgets.canvas.core.Enums import Mode, Socket


class Wire(QGraphicsPolygonItem):
    """ In a task (flow) that requires several steps to complete, Wires are used to determine the order of execution.
        Wires come in a few flavours called Modes:
        - Normal, which simply carry the process from the end of one Component to the beginning of another;
        - True/False, which originate from Condition components in accordance with the outcome of the condition;
        - Error, which continue the process in the event that a Condition generated an internal error.

        Note that Components may have any number of Wires coming out of them. The presence of multiple Wires will
        serve to fork the flow into several processes, executing subsequent Components in parallel, whereas a
        Component with no exit paths will end one process. Such continues the flow of execution until no more processes
        are running.
    """
    _mode: Mode
    _title: str
    _from_component: Component
    _from_socket: Socket
    _to_component: Component
    _to_socket: Socket
    _min_len: int

    _color = {
        Mode.NORMAL: QColor(192, 192, 192),  # white
        Mode.TRUE: QColor(0, 192, 0),  # green
        Mode.FALSE: QColor(192, 0, 0),  # red
        Mode.ERROR: QColor(192, 192, 0),  # yellow
    }

    def __init__(self,
                 scene: Scene,
                 from_component: Component, from_socket: Socket,
                 to_component: Component, to_socket: Socket,
                 mode: Mode = Mode.NORMAL,
                 title: str = None):
        super().__init__()
        self.initPainter()
        self.setMode(mode)
        self.setTitle(title)
        self._from_component = from_component
        self._from_socket = from_socket
        self._to_component = to_component
        self._to_socket = to_socket
        self._from_component.addOutputWire(self)
        self._to_component.addInputWire(self)
        self._min_len = scene.grid_snap_increment()
        self.autoRoute()
        # Don't set cursor here; it would apply to entire bounding rect

    def initPainter(self):
        pen = QPen()
        pen.setWidth(1)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        pen.setCosmetic(True)
        self.setPen(pen)

    # TODO Set cursor on hover: col/row-resize over path segments to hint manually adjusting paths
    # Qt.SizeVerCursor, Qt.SizeHorCursor
    # Qt.SplitVCursor, Qt.SplitHCursor
    # TODO Double-click a path segment to convert it to a Z-bend (adjust neighbours by half)
    # TODO Ctrl-double-click a path segment to remove a Z-bend (if possible)

    def autoRoute(self):
        # Routing rules:
        # - If the wire can be straight, let it be straight.
        #   - This requires the sockets to be opposing and aligned.
        # - If the sockets are not aligned with the ideal routing, go straight out for 20px before turning.
        #   - This gives the wire some distance from the component, and also provides a space for the arrow head.
        # - If the wire must wrap around a component to reach its socket, also keep 20px of distance.
        # - If we need to make a Z-bend, let the zig intersect the zag down the middle.
        #   - Ditto for the middle part of S-bends.
        #   - This is mainly for pleasing symmetry. We should be able to manually adjust routes later on.

        route = QPolygonF()

        # print(self._from_component.title(), "-", self._to_component.title())

        p_from = self._from_component.socketPoint(self._from_socket)
        p_to = self._to_component.socketPoint(self._to_socket)

        delta_x = p_to.x() - p_from.x()
        delta_y = p_to.y() - p_from.y()

        # First point
        route.append(p_from)

        # Intermediate points
        if self._to_socket.oppositeOf(self._from_socket):  # Some variant of I-, S- or Z-shape
            if self._from_socket == Socket.TOP or self._from_socket == Socket.BOTTOM:
                if (delta_y >= 2 * self._min_len and self._from_socket == Socket.BOTTOM) \
                        or (delta_y < 2 * self._min_len and self._from_socket == Socket.TOP):
                    # There's enough room between the components to make a simple cross-line
                    if (self._from_socket == Socket.TOP and delta_y > 0) \
                            or (self._from_socket == Socket.BOTTOM and delta_y < 0):
                        print("¤¤¤¤ IC")  # TODO Build a test flow for this
                        # self.route_C_path(route, p_from, p_to, delta_x, delta_y)
                    else:
                        if delta_x == 0:
                            # Straight vertical, no intermediate points needed
                            # We test for this early on because it'll be a common occurrence.
                            print("Straight vertical")
                            pass
                        else:
                            print("N")
                            self.route_Z_path(route, p_from, p_to, delta_x, delta_y)
                else:
                    if delta_x == 0:
                        print("C (vertically aligned)")  # TODO Build a test flow for this
                        self.route_C_path(route, p_from, p_to, delta_x, delta_y)
                    else:
                        # There isn't enough room to make a simple cross-line, we need to make a detour
                        # TODO Detect when the detour can't keep minimum distance, do a C-shape instead
                        print("~")
                        self.route_S_path(route, p_from, p_to, delta_x, delta_y)
            else:  # from Socket.LEFT or from Socket.RIGHT
                if (delta_x >= 2 * self._min_len and self._from_socket == Socket.RIGHT) \
                        or (delta_x < 2 * self._min_len and self._from_socket == Socket.LEFT):
                    # There's enough room between the components to make a simple cross-line
                    if (self._from_socket == Socket.LEFT and delta_x > 0) \
                            or (self._from_socket == Socket.RIGHT and delta_x < 0):
                        print("¤¤¤¤ -C")  # TODO Build a test flow for this
                        # self.route_C_path(route, p_from, p_to, delta_x, delta_y)
                    else:
                        if delta_y == 0:
                            # Straight horizontal, no intermediate points needed
                            # We test for this early on because it'll be a common occurrence.
                            print("Straight horizontal")
                            pass
                        else:
                            print("Z")
                            self.route_Z_path(route, p_from, p_to, delta_x, delta_y)
                else:
                    if delta_y == 0:
                        print("C (horizontally aligned)")  # TODO Build a test flow for this
                        self.route_C_path(route, p_from, p_to, delta_x, delta_y)
                    else:
                        # There isn't enough room to make a simple cross-line, we need to make a detour
                        # TODO Detect when the detour can't keep minimum distance, do a C-shape instead
                        print("S")
                        self.route_S_path(route, p_from, p_to, delta_x, delta_y)
        elif self._to_socket == self._from_socket:  # Some variant of C- or J-shape
            print("C")
            self.route_C_path(route, p_from, p_to, delta_x, delta_y)
        else:  # Some variant of L-shape
            print("L")
            self.route_L_path(route, p_from, p_to)

        # Last point
        route.append(p_to)
        self._add_path_arrow_head(route)
        self.setPolygon(route)

    def route_Z_path(self, route, p_from, p_to, delta_x, delta_y):
        if self._from_socket == Socket.TOP or self._from_socket == Socket.BOTTOM:
            # Components aren't horizontally aligned, so we need a horizontal cross-line.
            offset_y = delta_y / 2
            route.append(QPointF(
                p_from.x(),
                p_from.y() + offset_y
            ))
            route.append(QPointF(
                p_to.x(),
                p_from.y() + offset_y
            ))
        else:
            # Components aren't vertically aligned, so we need a simple vertical cross-line.
            offset_x = delta_x / 2
            route.append(QPointF(
                p_from.x() + offset_x,
                p_from.y()
            ))
            route.append(QPointF(
                p_from.x() + offset_x,
                p_to.y()
            ))

    def route_S_path(self, route, p_from, p_to, delta_x, delta_y):
        # Components aren't horizontally aligned, and there's no room in between them for a horizontal cross-line.
        # So we need to put in an additional vertical segment to curve back.
        if self._from_socket == Socket.TOP or self._from_socket == Socket.BOTTOM:
            offset_from_x = 0
            offset_from_y = self._min_len if self._from_socket == Socket.BOTTOM else -self._min_len
            offset_to_x = 0
            offset_to_y = self._min_len if self._to_socket == Socket.BOTTOM else -self._min_len
        else:
            offset_from_x = self._min_len if self._from_socket == Socket.RIGHT else -self._min_len
            offset_from_y = 0
            offset_to_x = self._min_len if self._to_socket == Socket.RIGHT else -self._min_len
            offset_to_y = 0
        offset_from_x2 = (p_to.x() - p_from.x()) / 2
        offset_from_y2 = (p_to.y() - p_from.y()) / 2
        # First, an offset point
        route.append(QPointF(
            p_from.x() + offset_from_x,
            p_from.y() + offset_from_y
        ))
        if self._from_socket == Socket.TOP or self._from_socket == Socket.BOTTOM:
            pass
            # Then, a Z-shaped route between the offset points
            route.append(QPointF(
                p_from.x() + offset_from_x2,
                p_from.y() + offset_from_y
            ))
            route.append(QPointF(
                p_from.x() + offset_from_x2,
                p_to.y() + offset_to_y
            ))
        else:
            pass
            # Then, a Z-shaped route between the offset points
            route.append(QPointF(
                p_from.x() + offset_from_x,
                p_from.y() + offset_from_y2
            ))
            route.append(QPointF(
                p_to.x() + offset_to_x,
                p_from.y() + offset_from_y2
            ))
        # Finally, another offset point
        route.append(QPointF(
            p_to.x() + offset_to_x,
            p_to.y() + offset_to_y
        ))

    def route_C_path(self, route, p_from, p_to, delta_x, delta_y):
        # The wire needs to go around one or both of the components in order to reach the sockets.
        pass

    def route_L_path(self, route, p_from, p_to):
        # All we need here is to find one corner point.
        # Which way we're going can be determined simply by looking at the orientation of one of the sockets.
        if self._from_socket == Socket.TOP or self._from_socket == Socket.BOTTOM:
            p_x = p_from.x()
            p_y = p_to.y()
        else:
            p_x = p_to.x()
            p_y = p_from.y()
        route.append(QPointF(
            p_x,
            p_y
        ))

    def _add_path_arrow_head(self, wire_path: QPolygonF):
        """ This assumes that the last point of `wire_path` ends at the destination socket,
            and that the destination socket is perpendicular to the component edge.
        """
        if self._to_socket == Socket.TOP:
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x() - 5,
                self._to_component.socketPoint(self._to_socket).y() - 7
            ))
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x() + 5,
                self._to_component.socketPoint(self._to_socket).y() - 7
            ))
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x(),
                self._to_component.socketPoint(self._to_socket).y()
            ))
        elif self._to_socket == Socket.RIGHT:
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x() + 7,
                self._to_component.socketPoint(self._to_socket).y() - 5
            ))
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x() + 7,
                self._to_component.socketPoint(self._to_socket).y() + 5
            ))
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x(),
                self._to_component.socketPoint(self._to_socket).y()
            ))
        elif self._to_socket == Socket.BOTTOM:
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x() + 5,
                self._to_component.socketPoint(self._to_socket).y() + 7
            ))
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x() - 5,
                self._to_component.socketPoint(self._to_socket).y() + 7
            ))
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x(),
                self._to_component.socketPoint(self._to_socket).y()
            ))
        elif self._to_socket == Socket.LEFT:
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x() - 7,
                self._to_component.socketPoint(self._to_socket).y() - 5
            ))
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x() - 7,
                self._to_component.socketPoint(self._to_socket).y() + 5
            ))
            wire_path.append(QPointF(
                self._to_component.socketPoint(self._to_socket).x(),
                self._to_component.socketPoint(self._to_socket).y()
            ))

    def mode(self):
        return self._mode

    def setMode(self, mode):
        self._mode = mode
        p = self.pen()
        p.setColor(self._color[self.mode()])
        self.setPen(p)

    def title(self):
        return self._title

    def setTitle(self, title: str):
        self._title = '' if title is None else title
        return self

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = ...) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.pen())
        painter.drawPolyline(self.polygon())
        self.paint_poly_points(painter)
        # FIXME Paint wires *behind* components
        # TODO Write label near source socket

    def paint_poly_points(self, painter):
        dot_pen = QPen()
        dot_pen.setWidth(4)
        dot_pen.setCosmetic(True)
        dot_pen.setColor(QColor(255, 0, 255))
        painter.setPen(dot_pen)
        for i in range(0, self.polygon().size() - 3):  # Don't paint dots on the arrow head
            p = self.polygon().value(i)
            painter.drawPoint(p)
