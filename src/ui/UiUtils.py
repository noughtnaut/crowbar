from typing import Union

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QDragMoveEvent, QMouseEvent, QPainter, QStaticText, QWheelEvent
from PyQt5.QtWidgets import QGraphicsSceneMouseEvent


def get_child(container, target_type):
    for child in container.children():
        type1 = target_type
        type2 = type(child)
        if type1 == type2:
            return child
    return None


_any_mouse_event = Union[
    QMouseEvent,
    QWheelEvent,
    QDragMoveEvent,
    QGraphicsSceneMouseEvent
]


def with_control_key(event: _any_mouse_event) -> bool:
    return event.modifiers() & Qt.ControlModifier


def with_alt_key(event: _any_mouse_event) -> bool:
    return event.modifiers() & Qt.AltModifier


def with_shift_key(event: _any_mouse_event) -> bool:
    return event.modifiers() & Qt.ShiftModifier


def click_descriptor(event: _any_mouse_event, suffix: str):
    action = ""
    if with_control_key(event):
        action += "ctrl-"
    if with_alt_key(event):
        action += "alt-"
    if with_shift_key(event):
        action += "shift-"

    if isinstance(event, QWheelEvent):
        if event.angleDelta().y() > 0:
            action += "up-"
        elif event.angleDelta().y() < 0:
            action += "down-"
        if event.angleDelta().x() > 0:
            action += "left-"
        elif event.angleDelta().x() < 0:
            action += "right-"
    else:
        if event.button() == Qt.RightButton:
            action += "right-"
        elif event.button() == Qt.MiddleButton:
            action += "middle-"
        elif event.button() == Qt.BackButton:
            action += "back-"
        elif event.button() == Qt.ForwardButton:
            action += "fwd-"
        elif event.button() == Qt.LeftButton:
            action += "left-"
            pass
        elif event.button() > 0:
            action += "unknown-"
            print("Unknown button:", event.button())
    action += suffix + "  -  (" + str(event.pos().x()) + ", " + str(event.pos().y()) + ")"
    return action


def draw_static_centered_text(painter: QPainter, pos: QPointF, s: str):
    text = QStaticText(s)  # FIXME Use drawText() instead of drawStaticText() to have multi-line text centered
    text.setTextWidth(20)
    half_size = QPointF(
        text.size().width() / 2,
        text.size().height() / 2
    )
    painter.drawStaticText(pos - half_size, text)
