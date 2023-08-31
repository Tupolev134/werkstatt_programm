from datetime import datetime

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QScrollArea, QTableWidget, QTableWidgetItem, \
    QApplication, QDateEdit, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox, QHBoxLayout

from core.UI.MainMenu import _get_line_widget
from core.UI.NavigationBar import NavigationBar

import os
from dotenv import load_dotenv
load_dotenv()
SUPPLIER_DATA_PATH = os.getenv("SUPPLIER_DATA_PATH")

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

        self.parts_list = []

        self.create_parts_table()
        self.main_layout.addWidget(_get_line_widget())
        self.create_order_header_section()
        self.main_layout.addWidget(_get_line_widget())
        self.create_input_parts_section()

    def create_order_header_section(self):
        self.order_header_section = QVBoxLayout()

        # Load suppliers and populate dropdown
        self.supplier_data = SupplierData(SUPPLIER_DATA_PATH)
        supplier_handles = [f"{supplier.handle}" for supplier in self.supplier_data.suppliers]
        self.name_combobox = QComboBox(self)
        self.name_combobox.addItems(supplier_handles)
        self.name_combobox.currentIndexChanged.connect(self.display_selected_supplier_info)
        self.order_header_section.addWidget(self.name_combobox)

        # Input fields to display and edit supplier info
        self.internal_handle = QLineEdit(self)
        self.first_name_input = QLineEdit(self)
        self.last_name_input = QLineEdit(self)
        self.email_input = QLineEdit(self)

        self.order_header_section.addWidget(QLabel("Internal Handle:"))
        self.order_header_section.addWidget(self.internal_handle)
        self.order_header_section.addWidget(QLabel("First Name:"))
        self.order_header_section.addWidget(self.first_name_input)
        self.order_header_section.addWidget(QLabel("Last Name:"))
        self.order_header_section.addWidget(self.last_name_input)
        self.order_header_section.addWidget(QLabel("Email:"))
        self.order_header_section.addWidget(self.email_input)

        self.main_layout.addLayout(self.order_header_section)
        self.display_selected_supplier_info(0)

    def display_selected_supplier_info(self, index):
        selected_supplier = self.supplier_data.suppliers[index]
        self.internal_handle.setText(selected_supplier.handle)
        self.first_name_input.setText(selected_supplier.first_name)
        self.last_name_input.setText(selected_supplier.last_name)
        self.email_input.setText(selected_supplier.email)

    def create_input_parts_section(self):
        self.input_parts_section = QVBoxLayout()

        # Field for chassis number
        self.chassis_input = QLineEdit(self)
        self.input_parts_section.addWidget(QLabel("Chassis Number:"))
        self.input_parts_section.addWidget(self.chassis_input)
        self.input_parts_section.addWidget(_get_line_widget())

        # Input fields for parts details
        self.parts_layout = QVBoxLayout()
        self.parts_number_input = QLineEdit(self)
        self.part_description_input = QLineEdit(self)
        self.quantity_input = QLineEdit(self)
        self.additional_info_input = QLineEdit(self)

        # Horizontal layout for parts inputs
        self.parts_inputs_hlayout = QHBoxLayout()
        self.parts_inputs_hlayout.addWidget(QLabel("Parts Number:"))
        self.parts_inputs_hlayout.addWidget(self.parts_number_input)
        self.parts_inputs_hlayout.addWidget(QLabel("Part Description:"))
        self.parts_inputs_hlayout.addWidget(self.part_description_input)
        self.parts_inputs_hlayout.addWidget(QLabel("Quantity:"))
        self.parts_inputs_hlayout.addWidget(self.quantity_input)
        self.parts_inputs_hlayout.addWidget(QLabel("Additional Info:"))
        self.parts_inputs_hlayout.addWidget(self.additional_info_input)

        # Add button
        self.add_parts_button = QPushButton("Add", self)
        self.add_parts_button.clicked.connect(self.add_part)
        self.parts_inputs_hlayout.addWidget(self.add_parts_button)
        self.parts_layout.addLayout(self.parts_inputs_hlayout)
        self.input_parts_section.addLayout(self.parts_layout)

        self.main_layout.addLayout(self.input_parts_section)

    def add_part(self):
        part = {
            "parts_number": self.parts_number_input.text(),
            "part_description": self.part_description_input.text(),
            "quantity": self.quantity_input.text(),
            "additional_info": self.additional_info_input.text(),
        }
        self.parts_list.append(part)

        # Clear input fields after adding
        self.parts_number_input.clear()
        self.part_description_input.clear()
        self.quantity_input.clear()
        self.additional_info_input.clear()

        self.populate_parts_table()

    def create_parts_table(self):
        # Create the table with headers
        self.parts_table = QTableWidget(0, 4)  # 0 rows initially, 4 columns
        self.parts_table.setHorizontalHeaderLabels(["Parts Number", "Part Description", "Quantity", "Additional Info"])
        self.parts_table.itemChanged.connect(self.handle_parts_item_changed)
        self.parts_table.setFixedHeight(600)
        self.main_layout.addWidget(self.parts_table)

    def populate_parts_table(self):
        # Clear the table first
        self.parts_table.setRowCount(0)

        # Populate the table with parts from parts_list
        for part in self.parts_list:
            row_position = self.parts_table.rowCount()
            self.parts_table.insertRow(row_position)

            self.parts_table.setItem(row_position, 0, QTableWidgetItem(part["parts_number"]))
            self.parts_table.setItem(row_position, 1, QTableWidgetItem(part["part_description"]))
            self.parts_table.setItem(row_position, 2, QTableWidgetItem(part["quantity"]))
            self.parts_table.setItem(row_position, 3, QTableWidgetItem(part["additional_info"]))

    def handle_parts_item_changed(self, item: QTableWidgetItem):
        # Get the row of the changed item
        row = item.row()

        # Check if the row exceeds the number of parts (safety check)
        if row >= len(self.parts_list):
            return

        # Get the corresponding part from parts_list
        part = self.parts_list[row]

        # Check which column was changed and update the respective attribute
        if item.column() == 0:  # Parts Number column
            part["parts_number"] = item.text()
        elif item.column() == 1:  # Part Description column
            part["part_description"] = item.text()
        elif item.column() == 2:  # Quantity column
            part["quantity"] = item.text()
        elif item.column() == 3:  # Additional Info column
            part["additional_info"] = item.text()
