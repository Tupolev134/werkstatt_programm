from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QScrollArea, QTableWidget, QTableWidgetItem, QApplication

from core.UI.NavigationBar import NavigationBar
from core.UI.cash_register.CashRegisterData import CashRegisterData

import os
from dotenv import load_dotenv
load_dotenv()
REGISTER_PATH=os.getenv("REGISTER_PATH")

class CashRegisterPage(QMainWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.setWindowTitle("Cash Register")

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

        # ------------------ create and add NavigationBar ------------------
        self.window_manager = window_manager
        self.nav_bar = NavigationBar(self.window_manager)  # Assuming NavigationBar is imported
        self.main_layout.addWidget(self.nav_bar)
        self.main_layout.setAlignment(self.nav_bar, Qt.AlignmentFlag.AlignTop)

        # ------------------ create Expense List ------------------
        self.create_expense_list_section()
        self.register_data = CashRegisterData(REGISTER_PATH)

        print(REGISTER_PATH)

    def create_expense_list_section(self):
        self.expense_table = QTableWidget(self)
        self.expense_table.setColumnCount(4)  # Date, Name, Expense Type, Amount
        self.expense_table.setHorizontalHeaderLabels(["Date", "Name", "Expense Type", "Amount"])

        # For the sake of demonstration, let's add a dummy row:
        self.expense_table.insertRow(0)
        self.expense_table.setItem(0, 0, QTableWidgetItem("2023-08-30"))
        self.expense_table.setItem(0, 1, QTableWidgetItem("John Doe"))
        self.expense_table.setItem(0, 2, QTableWidgetItem("Lunch"))
        self.expense_table.setItem(0, 3, QTableWidgetItem("$10.50"))

        self.main_layout.addWidget(self.expense_table)

    def populate_expense_table(self):
        # Clear the table first
        self.expense_table.setRowCount(0)

        # Iterate through transactions and populate the table
        for transaction in self.register_data.transactions:
            row_position = self.expense_table.rowCount()
            self.expense_table.insertRow(row_position)

            self.expense_table.setItem(row_position, 0, QTableWidgetItem(transaction.date.strftime('%Y-%m-%d')))
            self.expense_table.setItem(row_position, 1, QTableWidgetItem(transaction.name))
            self.expense_table.setItem(row_position, 2, QTableWidgetItem(transaction.expense_type))
            self.expense_table.setItem(row_position, 3, QTableWidgetItem(transaction.amount))

