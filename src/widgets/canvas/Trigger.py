from PyQt5.QtGui import QPainter

from widgets.canvas.core.Component import Component


class Trigger(Component):
    """ In a task (flow) that requires several steps to complete, each step is a Component.
        A Trigger monitors the universe, waiting for certain events to happen. When they do, the Trigger will create a
        flow process for each output Wire connected to it, and is thus the initial step in any task.
    """
    _corner_roundness = 75  # roundness as percentage, so that 0..100 == rect..ellipse

    def paintShape(self, painter: QPainter):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRoundedRect(self.rect(), self._corner_roundness / 4, self._corner_roundness)

    # TODO NTH: Take rounded corners into consideration when determining shape
    # def shape(self) -> QPainterPath:
    # This defines the outline when it comes to resolving click targets
    # return self._shape
