from PyQt5.QtWidgets import QSizePolicy, QToolBar, QWidget


class ToolBar(QToolBar):
    """
    A QToolBar that has learned a new trick.
    """

    def addSeparator(self, expand: bool = False):
        """
        Appends a separator as usual unless `expand` is True, in which case it bloats.
        """
        if expand:
            expander = QWidget()
            expander.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            return self.addWidget(expander)
        else:
            return super().addSeparator()
