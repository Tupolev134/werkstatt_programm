from datetime import datetime

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QScrollArea, QTableWidget, QTableWidgetItem, \
    QApplication, QDateEdit, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox

from core.UI.NavigationBar import NavigationBar

import os
from dotenv import load_dotenv

from core.UI.emailer.SupplierData import SupplierData


# noinspection PyAttributeOutsideInit
class OrderPartsEmailPage(QMainWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.setWindowTitle("Order Parts")

        # ------------------ setup Window ------------------
        central_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        self.setMaximumHeight(rect.height())
        self.main_layout = QVBoxLayout(central_widget)
        self.resize(600,900)

        # ------------------ create and add NavigationBar ------------------
        self.window_manager = window_manager
        self.nav_bar = NavigationBar(self.window_manager)  # Assuming NavigationBar is imported
        self.main_layout.addWidget(self.nav_bar)
        self.main_layout.setAlignment(self.nav_bar, Qt.AlignmentFlag.AlignTop)

    def create_order_header_section(self):
        self.order_header_section = QVBoxLayout()

        # Load suppliers and populate dropdown
        self.supplier_data = SupplierData()
        supplier_names = [f"{supplier.first_name} {supplier.last_name}" for supplier in self.supplier_data.suppliers]
        self.name_combobox = QComboBox(self)
        self.name_combobox.addItems(supplier_names)
        self.name_combobox.currentIndexChanged.connect(self.display_selected_supplier_info)
        self.order_header_section.addWidget(self.name_combobox)

        # Input fields to display and edit supplier info
        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)
        self.email_input = QLineEdit(self)

        self.order_header_section.addWidget(QLabel("First Name:"))
        self.order_header_section.addWidget(self.first_name_input)
        self.order_header_section.addWidget(QLabel("Last Name:"))
        self.order_header_section.addWidget(self.last_name_input)
        self.order_header_section.addWidget(QLabel("Email:"))
        self.order_header_section.addWidget(self.email_input)

        self.main_layout.addLayout(self.order_header_section)
        self.display_selected_supplier_info(0)  # Display info for the first supplier by default

    def display_selected_supplier_info(self, index):
        selected_supplier = self.supplier_data.suppliers[index]
        self.first_name_input.setText(selected_supplier.first_name)
        self.last_name_input.setText(selected_supplier.last_name)
        self.email_input.setText(selected_supplier.email)

