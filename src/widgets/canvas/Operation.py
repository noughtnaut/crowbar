from PyQt5.QtGui import QPainter

from widgets.canvas.core.Component import Component


class Operation(Component):
    """ In a task (flow) that requires several steps to complete, each step is a Component.
        An Operation can be one of any number of pre-defined actions, or it can be a user script. It will execute when
        signalled by an input Wire, carrying out whatever operation it is meant to do, and may then pass execution on
        to other Components through output Wires (or terminate the process).
    """

    def paintShape(self, painter: QPainter):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.fillRect(self.rect(), self.brush())
        painter.drawRect(self.rect())
