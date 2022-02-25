from PyQt5.QtGui import QPainter, QPainterPath, QPolygonF

from src.ui.widgets.canvas.core.Component import Component
from src.ui.widgets.canvas.core.Enums import Socket


class Condition(Component):
    """ In a task (flow) that requires several steps to complete, each step is a Component.
        A Condition contains some user-defined script snippet that will result in a True/False decision. If the
        decision is True, the Condition will create a flow process for only those Wires connected to it that are of
        mode True. Similarly, if the decision is False, the Condition will create a flow process for only those Wires
        connected to it that are of mode False.
    """
    _polygon: QPolygonF
    _shape: QPainterPath

    def __init__(self, *__args):
        super().__init__(*__args)
        self.initShape()

    def initShape(self):
        self._polygon = QPolygonF()
        # Add points by clockwise order
        self._polygon.append(self.socketPoint(Socket.TOP))
        self._polygon.append(self.socketPoint(Socket.RIGHT))
        self._polygon.append(self.socketPoint(Socket.BOTTOM))
        self._polygon.append(self.socketPoint(Socket.LEFT))
        self._shape = QPainterPath()
        self._shape.addPolygon(self._polygon)

    def shape(self) -> QPainterPath:
        # This defines the outline when it comes to resolving click targets
        return self._shape

    def paintShape(self, painter: QPainter):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawConvexPolygon(self._polygon)
