from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSplitter, QGridLayout


# See: https://stackoverflow.com/a/65167358/14577190

class PanedWidget(QWidget):

    def __init__(self, first_pane: QWidget, second_pane: QWidget, orientation: Qt.Orientation = Qt.Horizontal):
        super().__init__()

        left_pane = first_pane
        right_pane = second_pane

        splitter = QSplitter(orientation)
        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)

        layout = QGridLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)
