from PyQt5 import uic
from PyQt5.QtWidgets import QDialog


class WindowAbout(QDialog):

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.load_ui()

    def load_ui(self):
        uic.loadUi(self.cfg.get('BASEDIR', '.') + "src/ui/window_about.ui", self)  # TODO Create this file
        self.setFixedSize(self.size())  # FIXME Should be doable in .ui file
