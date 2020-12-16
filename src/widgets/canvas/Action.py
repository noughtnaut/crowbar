from PyQt5.QtGui import QPainter

from widgets.canvas.Canvas import CanvasShape


class Action(CanvasShape):

    def paintShape(self, painter: QPainter):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.fillRect(self.rect(), self.brush())
        painter.drawRect(self.rect())
