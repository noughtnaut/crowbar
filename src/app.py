import typing

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from ui.WindowAbout import WindowAbout
from ui.WindowMain import WindowMain


class CrowbarApp(QApplication):
    def __init__(self, argv: typing.List[str]):
        print('Hello, world!')
        super().__init__(argv)
        self.setOrganizationName('golfbravo')
        self.setOrganizationDomain('golfbravo.net')
        self.setApplicationName('crowbar')
        self.setApplicationVersion('0.0.1')
        self.setApplicationDisplayName('well-intentioned crowbar')
        self.setWindowIcon(QIcon('media/crowbar/crowbar-head.svg'))
        # config = QSettings()  # Stores in `$HOME/.config/<self-org-name>/<self-app-name>.conf`

        print("loading main window")
        self.window_main = WindowMain()
        self.window_about = WindowAbout()
        self.window_main.show()

    def run(self):
        print("starting event loop")
        self.exec_()
        print("event loop exited.")
