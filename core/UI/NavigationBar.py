from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFrame, QGridLayout


def _get_line_widget():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line

class NavigationBar(QWidget):
    def __init__(self, window_manager):
        super().__init__()
        # self.bottom_layout = QHBoxLayout(self)
        self.layout = QGridLayout(self)
        self.back_btn = QPushButton("Back", self)
        self.forward_btn = QPushButton("Forward", self)

        self.back_btn.clicked.connect(window_manager.go_back)
        self.forward_btn.clicked.connect(window_manager.go_forward)

        self.layout.addWidget(self.back_btn, 0, 0)
        self.layout.addWidget(self.forward_btn, 0, 1)
        # self.bottom_layout.addWidget(_get_line_widget())

