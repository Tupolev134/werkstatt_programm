from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class NavigationBar(QWidget):
    def __init__(self, window_manager):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.back_btn = QPushButton("Back", self)
        self.forward_btn = QPushButton("Forward", self)

        self.back_btn.clicked.connect(window_manager.go_back)
        self.forward_btn.clicked.connect(window_manager.go_forward)

        self.layout.addWidget(self.back_btn)
        self.layout.addWidget(self.forward_btn)
