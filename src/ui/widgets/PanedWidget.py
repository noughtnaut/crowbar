from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QSplitter, QWidget


# See: https://stackoverflow.com/a/65167358/14577190

class PanedWidget(QWidget):
    """ The PanedWidget encapsulates the necessary widgets and layouts, so that the app doesn't have to deal with
    a widget with a layout with a widget with a widget and a widget...
    """
    _splitter: QSplitter

    def __init__(self,
                 left_or_top_pane: QWidget = None,
                 right_or_bottom_pane: QWidget = None,
                 orientation: Qt.Orientation = Qt.Horizontal):
        super().__init__()

        self.splitter = QSplitter(orientation)
        self.addWidget(left_or_top_pane)
        self.addWidget(right_or_bottom_pane)

        layout = QGridLayout(self)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

    def addWidget(self, widget: QWidget):
        if widget is not None:
            self.splitter.addWidget(widget)

    def insertWidget(self, index: int, widget: QWidget):
        if widget is not None:
            self.splitter.insertWidget(index, widget)

    def setCollapsible(self, index: int, is_collapsible: bool):
        self.splitter.setCollapsible(index, is_collapsible)

    def setStretchFactor(self, index: int, stretch: int):
        self.splitter.setStretchFactor(index, stretch)

    # TODO Expose a bunch of other QSplitter methods ... is there a generic ("magic") way to do this safely?
