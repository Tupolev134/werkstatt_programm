from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QFrame, QGridLayout, \
    QScrollArea
from core.UI.NavigationBar import NavigationBar


def _get_line_widget():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line

def get_sorted_list(list_of_tuples):
    return [item[0] for item in sorted(list_of_tuples, key=lambda x: x[1], reverse=True)]


class MainMenu(QMainWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.setWindowTitle("Overlanders Workshop System")
        self.resize(450, 600)

        # ------------------ setup Sections ------------------
        # Import Data section
        self.import_data_section_layout = QGridLayout()
        self.open_cash_register_btn = QPushButton("Cash Register", self)
        self.convert_parts_to_excel_btn = QPushButton("Convert Parts To Excel", self)
        self.import_part_btn = QPushButton("Import new Part", self)
        self.import_orderable_part_btn = QPushButton("Import new order-able Part", self)
        self.import_orderable_part_raw_btn = QPushButton("Import new order-able Part as raw data", self)
        self.import_order_btn = QPushButton("Import new Order", self)
        self.import_project_btn = QPushButton("Import new Project", self)
        self.import_line = QLineEdit()

        # ------------------ setup Window ------------------
        central_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        self.setMaximumHeight(rect.height())
        self.setCentralWidget(scroll_area)
        self.main_layout = QVBoxLayout(central_widget)

        # ------------------ create and add NavigationBar ------------------
        self.window_manager = window_manager
        self.nav_bar = NavigationBar(self.window_manager)
        self.main_layout.addWidget(self.nav_bar)
        self.main_layout.setAlignment(self.nav_bar, Qt.AlignmentFlag.AlignTop)

        # ------------------ create and add Layout ------------------
        self.create_import_data_section()
        self.main_layout.addLayout(self.import_data_section_layout)

    # ------------------ Sections ------------------

    def create_import_data_section(self):
        self.import_data_section_layout.addWidget(self.open_cash_register_btn)
        self.import_data_section_layout.addWidget(self.convert_parts_to_excel_btn)
        self.import_data_section_layout.addWidget(self.import_orderable_part_btn)
        self.import_data_section_layout.addWidget(self.import_orderable_part_raw_btn)
        self.import_data_section_layout.addWidget(self.import_order_btn)
        # self.import_data_section_layout.addWidget(self.import_part_btn)
        # self.import_data_section_layout.addWidget(self.import_project_btn)
        # self.import_data_section_layout.addWidget(self.import_line)

        self.open_cash_register_btn.clicked.connect(lambda : self.window_manager.show_window('cash_register'))
        self.convert_parts_to_excel_btn.clicked.connect(lambda : self.window_manager.show_window('convert_parts_to_excel'))
        self.import_order_btn.clicked.connect(lambda : self.window_manager.show_window('insert_order'))
        self.import_orderable_part_btn.clicked.connect(lambda : self.window_manager.show_window('orderable_part'))
        self.import_orderable_part_raw_btn.clicked.connect(lambda : self.window_manager.show_window('orderable_part_raw'))
