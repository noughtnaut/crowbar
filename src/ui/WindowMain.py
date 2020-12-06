from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QPushButton, QToolBar, QStatusBar, QWidget, QSplitter, QLabel, QGridLayout, QLayout, QVBoxLayout


class WindowMain(QMainWindow):

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg = cfg
        self._populate_main_window()

    def _populate_main_window(self):
        self.resize(800, 600)
        self.setWindowTitle(self.cfg.get('app_name'))
        self.setCentralWidget(self.create_central_widget())
        self._create_menu()
        self._create_toolbar()
        self._create_status_bar()

    def create_central_widget(self):  # See: https://stackoverflow.com/a/65167358/14577190
        left_pane = self.create_pane(self.create_pane_content('left'))
        right_pane = self.create_pane(self.create_pane_content('right'))

        # Splitter, containing left and right panes
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)

        # Container widget for splitter
        central_container = QWidget()
        grid_layout = QGridLayout(central_container)
        grid_layout.addWidget(splitter)
        central_container.setLayout(grid_layout)
        return central_container

    def create_pane(self, content: QLayout) -> QWidget:
        # Container widget for pane layout
        pane_layout_container = QWidget()
        pane_layout_container.setLayout(content)
        return pane_layout_container

    def create_pane_content(self, identifier) -> QLayout:
        content = QVBoxLayout()  # Layout widget for pane content

        # FROM HERE you create your own content

        toolbar = QToolBar()
        toolbar.addWidget(QPushButton("Do Something"))
        content.addWidget(toolbar)  # Don't forget this! ^_^

        label = QLabel(identifier)
        label.setAutoFillBackground(True)
        p = label.palette()
        p.setColor(label.backgroundRole(), Qt.lightGray)
        label.setPalette(p)
        label.setAlignment(Qt.AlignCenter)

        content.addWidget(label)  # Don't forget this! ^_^

        # UNTIL HERE you populate your content

        return content

    def _create_menu(self):
        menu_file = self.menuBar().addMenu("&File")
        menu_file.addAction('&New Flow ...', self._do_new_flow)
        menu_file.addAction('New &Group ...', self._do_new_group)
        menu_file.addSeparator()
        menu_file.addAction('&Quit', self._do_quit)

        menu_help = self.menuBar().addMenu("&Help")
        menu_help.addAction('&About', self._do_show_about)

    def _create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        toolbar.addAction('New Flow ...', self._do_new_flow)
        toolbar.addAction('New Group ...', self._do_new_group)
        toolbar.addSeparator()
        toolbar.addAction('Run', self._do_NYI)
        toolbar.addAction('Triggers ...', self._do_NYI)

    def _create_status_bar(self):
        status = QStatusBar()
        status.showMessage("/!\\ This app is a PROTOTYPE - do not use for anything serious!")
        self.setStatusBar(status)

    def _do_new_flow(self):
        print("Feel the flow, man ...")

    def _do_new_group(self):
        print("Here's a new group for you.")

    def _do_quit(self):
        self.close()

    def _do_show_about(self):
        print("Ain't that shiny?")

    def _do_NYI(self):
        print("<Not yet implemented>")
