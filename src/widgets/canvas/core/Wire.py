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

        p_from = self._from_component.socketPoint(self._from_socket)
        p_to = self._to_component.socketPoint(self._to_socket)

        delta_x = p_to.x() - p_from.x()
        delta_y = p_to.y() - p_from.y()

        # First point
        route.append(p_from)

        if self._to_socket.oppositeOf(self._from_socket):  # Some variant of I- or Z-shape
            if self._from_socket == Socket.TOP or self._from_socket == Socket.BOTTOM:
                # If there isn't enough room to make a simple cross-line, we need to make a detour
                if delta_x != 0:
                    if abs(delta_y) >= 2 * self._min_len:
                        # Make a simple cross-line
                        offset_y = delta_y / 2
                        route.append(QPointF(
                            p_from.x(),
                            p_from.y() + offset_y
                        ))
                        route.append(QPointF(
                            p_to.x(),
                            p_from.y() + offset_y
                        ))
                    else:  # Make an S-shaped detour
                        # First, an offset point
                        offset_y = self._min_len if self._from_socket == Socket.BOTTOM else -self._min_len
                        route.append(QPointF(
                            p_from.x(),
                            p_from.y() + offset_y
                        ))
                        # Then, a Z-shaped route between the offset points
                        offset_x = delta_x / 2
                        offset_y = self._min_len if self._from_socket == Socket.BOTTOM else -self._min_len
                        route.append(QPointF(
                            p_from.x() + offset_x,
                            p_from.y() + offset_y
                        ))
                        offset_x = delta_x / 2
                        offset_y = self._min_len if self._to_socket == Socket.BOTTOM else -self._min_len
                        route.append(QPointF(
                            p_to.x() - offset_x,
                            p_to.y() + offset_y
                        ))
                        # # Finally, another offset point
                        offset_y = self._min_len if self._to_socket == Socket.BOTTOM else -self._min_len
                        route.append(QPointF(
                            p_to.x(),
                            p_to.y() + offset_y
                        ))
                # else: Straight vertical, no intermediate points needed
            else:  # self._from_socket == Socket.LEFT or self._from_socket == Socket.RIGHT
                # If there isn't enough room to make a simple cross-line, we need to make a detour
                if delta_y != 0:
                    if abs(delta_x) >= 2 * self._min_len:
                        # Make a simple cross-line
                        offset_x = delta_x / 2
                        route.append(QPointF(
                            p_from.x() + offset_x,
                            p_from.y()
                        ))
                        route.append(QPointF(
                            p_from.x() + offset_x,
                            p_to.y()
                        ))
                    else:  # Make an S-shaped detour
                        # First, an offset point
                        offset_x = self._min_len if self._from_socket == Socket.RIGHT else -self._min_len
                        route.append(QPointF(
                            p_from.x() + offset_x,
                            p_from.y()
                        ))
                        # Then, a Z-shaped route between the offset points
                        offset_x = self._min_len if self._from_socket == Socket.RIGHT else -self._min_len
                        offset_y = delta_y / 2
                        route.append(QPointF(
                            p_from.x() + offset_x,
                            p_from.y() + offset_y
                        ))
                        offset_x = self._min_len if self._to_socket == Socket.RIGHT else -self._min_len
                        offset_y = delta_y / 2
                        route.append(QPointF(
                            p_to.x() + offset_x,
                            p_to.y() - offset_y
                        ))
                        # # Finally, another offset point
                        offset_x = self._min_len if self._to_socket == Socket.RIGHT else -self._min_len
                        route.append(QPointF(
                            p_to.x() + offset_x,
                            p_to.y()
                        ))
                # else: Straight horizontal, no intermediate points needed
        elif self._to_socket == self._from_socket:  # Some variant of C-shape
            pass
        else:  # Some variant of L-shape
            pass

        # Last point
        route.append(p_to)
        self._add_path_arrow_head(route)
        self.setPolygon(route)

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
        # FIXME Paint wires *behind* components
        # TODO Write label near source socket
