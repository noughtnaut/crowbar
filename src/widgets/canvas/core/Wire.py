import typing

from PyQt5 import QtGui
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsPolygonItem, QStyleOptionGraphicsItem, QWidget

from widgets.canvas.core import Component
from widgets.canvas.core.Enums import Mode, Socket


class Wire(QGraphicsPolygonItem):
    # FIXME Wires must belong to the component they originate at, so that the component knows its exit paths.
    # FIXME Source components must also request wires to re-route when the component moves.
    # FIXME Destination components must also (be able to!) request wires to re-route when the component moves.
    _mode: Mode
    _title: str
    _from_component: Component
    _from_socket: Socket
    _to_component: Component
    _to_socket: Socket

    _color = {
        Mode.NORMAL: QColor(192, 192, 192),  # white
        Mode.TRUE: QColor(0, 192, 0),  # green
        Mode.FALSE: QColor(192, 0, 0),  # red
        Mode.ERROR: QColor(192, 192, 0),  # yellow
    }

    def __init__(self,
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
        self.autoRoute()

    def initPainter(self):
        pen = QPen()
        pen.setWidth(2)
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
        #   This requires the sockets to be opposing and aligned.
        # - If the sockets are not aligned with the ideal routing, go straight out for 20px before turning.
        #   This gives the wire some distance from the component, and also provides a space for the arrow head.
        # - If the wire must wrap around a component to reach its socket, also keep 20px of distance.
        # - If we need to make a Z-bend, let the zig intersect the zag down the middle.
        #   This is mainly for pleasing symmetry. We should be able to manually adjust routes later on.
        new_path = QPolygonF()
        # First point
        new_path.append(self._from_component.socketPoint(self._from_socket))

        delta_x = self._to_component.pos().x() - self._from_component.pos().x()
        delta_y = self._to_component.pos().y() - self._from_component.pos().y()

        # TODO It must be possible to normalize/optimize this to cut down on the number of branches
        # Idea: Introduce a point 20px out from each socket, no matter where we're going?
        #       - This would free us from having to consider the "facing" of sockets!
        #       - This might result in artifacts when manually adjusting routes later on, but that's acceptable.
        # Idea: Implement routing between arbitrary points as an incremental path builder?
        if delta_x > 0:  # Going right
            if delta_y > 0:  # Going down
                if self._from_socket == Socket.TOP:
                    pass  # TODO This is just a stupid amount of code I really don't wanna write
                elif self._from_socket == Socket.RIGHT:
                    if self._to_socket == Socket.TOP:
                        new_path.append(QPointF(
                            self._to_component.socketPoint(self._to_socket).x(),
                            self._from_component.socketPoint(self._from_socket).y()
                        ))
                    elif self._to_socket == Socket.RIGHT:
                        new_path.append(QPointF(
                            self._to_component.socketPoint(self._to_socket).x() + 20,
                            self._from_component.socketPoint(self._from_socket).y()
                        ))
                        new_path.append(QPointF(
                            self._to_component.socketPoint(self._to_socket).x() + 20,
                            self._to_component.socketPoint(self._to_socket).y()
                        ))
                    elif self._to_socket == Socket.BOTTOM:
                        new_path.append(QPointF(
                            self._from_component.socketPoint(self._from_socket).x()
                            + (delta_x - self._to_component.width()) / 2,
                            self._from_component.socketPoint(self._from_socket).y()
                        ))
                        new_path.append(QPointF(
                            self._from_component.socketPoint(self._from_socket).x()
                            + (delta_x - self._to_component.width()) / 2,
                            self._to_component.socketPoint(self._to_socket).y() + 20
                        ))
                        new_path.append(QPointF(
                            self._to_component.socketPoint(self._to_socket).x(),
                            self._to_component.socketPoint(self._to_socket).y() + 20
                        ))
                    elif self._to_socket == Socket.LEFT:
                        new_path.append(QPointF(
                            self._from_component.socketPoint(self._from_socket).x()
                            + (delta_x - self._to_component.width()) / 2,
                            self._from_component.socketPoint(self._from_socket).y()
                        ))
                        new_path.append(QPointF(
                            self._from_component.socketPoint(self._from_socket).x()
                            + (delta_x - self._to_component.width()) / 2,
                            self._to_component.socketPoint(self._to_socket).y()
                        ))
                elif self._from_socket == Socket.BOTTOM:
                    pass  # TODO
                elif self._from_socket == Socket.LEFT:
                    pass  # TODO
            elif delta_y < 0:  # Going up
                pass  # TODO
            # else: Going horizontally
        elif delta_x < 0:  # Going left
            if delta_y > 0:  # Going down
                pass  # TODO
            elif delta_y < 0:  # Going up
                pass  # TODO
            # else: Going horizontally
        # else: Going nowhere!

        # Last point
        new_path.append(self._to_component.socketPoint(self._to_socket))
        # TODO Add an arrow head
        # TODO Write label near source socket
        self.setPolygon(new_path)

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
