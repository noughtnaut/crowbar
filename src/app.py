import typing

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from ui.WindowAbout import WindowAbout
from ui.WindowMain import WindowMain


class CrowbarApp(QApplication):
    _windows = {}

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
        self._windows['main'] = WindowMain()
        self._windows['about'] = WindowAbout()
        self._windows['main'].show()

    def run(self):
        print("starting event loop")
        self.exec_()
        print("event loop exited.")

    def window_main(self):
        return self._windows['main']

    def window_about(self):
        return self._windows['about']

    def do_quit_cleanup(self):
        for window in self._windows.values():
            window.close()
