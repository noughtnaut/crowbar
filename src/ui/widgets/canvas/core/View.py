from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QFrame, QGraphicsView, QWidget

from ui.UiUtils import click_descriptor, with_control_key
from ui.widgets.canvas.core.Scene import CanvasScene


class CanvasView(QGraphicsView):
    _zoom = 1.0
    _zoom_factor = 1.25
    _zoom_min = 0.125
    _zoom_max = 8

    def __init__(self, scene: CanvasScene, parent: QWidget):
        super().__init__(scene, parent)
        self.setFrameStyle(QFrame.Panel)
        self.setMouseTracking(True)
        self._pan_from = None
        self._pan_to = None

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        print(click_descriptor(event, 'drag¤'))
        super().dragMoveEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # print(click_descriptor(event, 'move'))
        super().mouseMoveEvent(event)
        # Panning canvas while click-and-dragging the background
        if self._pan_from is not None:
            self._pan_to = self.mapToScene(event.pos())
            delta = self._pan_to - self._pan_from
            self.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # print(click_descriptor(event, 'click'))
        super().mousePressEvent(event)
        target = self.itemAt(event.pos())
        # Start panning canvas if click-and-dragging the background
        if click_descriptor(event) == "left-" and target is None:
            self.setCursor(Qt.ClosedHandCursor)
            self._pan_from = self.mapToScene(event.pos())
            self._pan_to = self._pan_from

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        # print(click_descriptor(event, 'double-click'))
        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        # print(click_descriptor(event, 'release'))
        super().mouseReleaseEvent(event)
        # Stop panning canvas if no longer dragging the background
        if click_descriptor(event) == "left-" and self._pan_from is not None:
            self.unsetCursor()
            self._pan_from = None

    def wheelEvent(self, event: QWheelEvent) -> None:
        # print(click_descriptor(event, 'scroll'))
        # Zoom on Ctrl-scroll
        if with_control_key(event) and event.angleDelta().y():
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            super().wheelEvent(event)

    def zoom_out(self):
        factor = 1 / self._zoom_factor
        self.zoom_by_factor(factor)

    def zoom_in(self):
        factor = self._zoom_factor
        self.zoom_by_factor(factor)

    def zoom_by_factor(self, factor):
        new_zoom = self._zoom * factor
        if self._zoom_min < new_zoom < self._zoom_max:
            self.scale(factor, factor)
            self._zoom = self.transform().m11()  # m11 and m22 are the applied x and y scaling factors

    def zoom_reset(self):
        # Note: This works, but does nothing to bring the contents into view
        self.scale(1 / self._zoom, 1 / self._zoom)
        self._zoom = self.transform().m11()

    def zoom_to_fit(self):
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        self._zoom = self.transform().m11()
