import typing

from PyQt5.QtWidgets import QApplication
from src.ui.WindowMain import WindowMain


class CrowbarApp(QApplication):

    def __init__(self, cfg: dict, argv: typing.List[str]):
        print("loading main window")
        super().__init__(argv)
        self.window_main = WindowMain(cfg)
        self.window_main.show()
    #     self.window_about = WindowAbout(cfg)

    def run(self):
        print("starting event loop")
        self.exec_()
        print("event loop exited.")
