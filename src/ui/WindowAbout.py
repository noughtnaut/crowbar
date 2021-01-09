from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *


class WindowAbout(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('About')
        self.setFixedSize(524, 285)
        self.setWindowIcon(QIcon('media/crowbar/crowbar-head.svg'))
        layout = QVBoxLayout()
        self.setLayout(layout)

        pixmap = QtGui.QPixmap('media/crowbar/crowbar-flat-500.png')
        image = QLabel()
        image.setText('crowbar')
        image.setFrameShape(QFrame.Panel)
        image.setPixmap(pixmap)
        image.setAlignment(Qt.AlignCenter)
        layout.addWidget(image)

        text = QLabel('The well-intentioned crowbar is a desktop task automation tool'
                      + ' with an intuitive visual boxes-and-arrows workflow interface.')
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignCenter)
        layout.addWidget(text)

        version = QLabel('Version ' + qApp.applicationVersion())
        version.setWordWrap(True)
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        github = QLabel('For more info, updates, and source code, visit:')
        github.setOpenExternalLinks(True)
        github.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        github.setWordWrap(True)
        github.setAlignment(Qt.AlignCenter)
        layout.addWidget(github)

        github_link = QLabel('<a href="https://github.com/Noughtnaut/crowbar">github.com/noughtnaut/crowbar</a>')
        github_link.setOpenExternalLinks(True)
        github_link.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        github_link.setWordWrap(True)
        github_link.setAlignment(Qt.AlignCenter)
        layout.addWidget(github_link)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
