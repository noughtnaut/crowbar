from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QSplitter, QWidget


# See: https://stackoverflow.com/a/65167358/14577190

class PanedWidget(QWidget):
    """ The PanedWidget encapsulates the necessary widgets and layouts, so that the app doesn't have to deal with
    a widget with a layout with a widget with a widget and a widget...
    """

    def __init__(self,
                 left_or_top_pane: QWidget,
                 right_or_bottom_pane: QWidget,
                 orientation: Qt.Orientation = Qt.Horizontal):
        super().__init__()

        splitter = QSplitter(orientation)
        splitter.addWidget(left_or_top_pane)
        splitter.addWidget(right_or_bottom_pane)

        layout = QGridLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)
