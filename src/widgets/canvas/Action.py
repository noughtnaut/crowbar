from PyQt5.QtGui import QPainter

from widgets.canvas.Canvas import Component


class Action(Component):

    def paintShape(self, painter: QPainter):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.fillRect(self.rect(), self.brush())
        painter.drawRect(self.rect())
