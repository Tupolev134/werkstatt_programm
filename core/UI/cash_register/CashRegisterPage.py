from datetime import datetime

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QScrollArea, QTableWidget, QTableWidgetItem, \
    QApplication, QDateEdit, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox

from core.UI.NavigationBar import NavigationBar
from core.UI.cash_register.CashRegisterData import CashRegisterData

import os
from dotenv import load_dotenv

from core.UI.cash_register.Transaction import Transaction

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
        self.resize(600,900)

        # ------------------ create and add NavigationBar ------------------
        self.window_manager = window_manager
        self.nav_bar = NavigationBar(self.window_manager)  # Assuming NavigationBar is imported
        self.main_layout.addWidget(self.nav_bar)
        self.main_layout.setAlignment(self.nav_bar, Qt.AlignmentFlag.AlignTop)

        # ------------------ create Expense List ------------------
        self.create_expense_list_section()
        self.create_insert_section()
        self.register_data = CashRegisterData(REGISTER_PATH)
        self.populate_expense_table()

    def create_expense_list_section(self):
        self.expense_table = QTableWidget(self)
        self.expense_table.setColumnCount(4)  # Date, Name, Expense Type, Amount
        self.expense_table.setHorizontalHeaderLabels(["Date", "Name", "Expense Type", "Amount"])
        self.expense_table.horizontalHeader().setStretchLastSection(True)

        self.main_layout.addWidget(self.expense_table)
        self.expense_table.itemChanged.connect(self.handle_item_changed)

    def populate_expense_table(self):
        # Clear the table first
        self.expense_table.setRowCount(0)

        # Iterate through transactions and populate the table
        for transaction in self.register_data.transactions:
            row_position = self.expense_table.rowCount()
            self.expense_table.insertRow(row_position)

            self.expense_table.setItem(row_position, 0, QTableWidgetItem(transaction.date.strftime('%dd-%mm-%YYYY')))
            self.expense_table.setItem(row_position, 1, QTableWidgetItem(transaction.name))
            self.expense_table.setItem(row_position, 2, QTableWidgetItem(transaction.expense_type))
            self.expense_table.setItem(row_position, 3, QTableWidgetItem(str(transaction.amount)))

    def create_insert_section(self):
        # Layout to hold input widgets
        input_layout = QVBoxLayout()

        # Date selection widget
        self.date_edit = QDateEdit(self)
        self.date_edit.setDate(QDate.currentDate())
        input_layout.addWidget(QLabel("Date:"))
        input_layout.addWidget(self.date_edit)

        # Name selection widget (QComboBox with hardcoded names)
        self.name_combobox = QComboBox(self)
        self.name_combobox.addItems(['Felix Tappert', 'Szymon Goral', 'Steve Knauff', 'Leonardo Smura', 'Jonas Glöckner'])  # Hardcoded names
        input_layout.addWidget(QLabel("Name:"))
        input_layout.addWidget(self.name_combobox)

        # Expense type input widget
        self.expense_type_edit = QLineEdit(self)
        input_layout.addWidget(QLabel("Expense Type:"))
        input_layout.addWidget(self.expense_type_edit)

        # Amount input widget
        self.amount_edit = QLineEdit(self)
        input_layout.addWidget(QLabel("Amount:"))
        input_layout.addWidget(self.amount_edit)

        # Submit buttons
        self.incoming_button = QPushButton("Add Incoming Payment", self)
        self.incoming_button.clicked.connect(self.add_transaction)
        self.outgoing_button = QPushButton("Add Outgoing Payment", self)
        self.outgoing_button.clicked.connect(lambda: self.add_transaction(ingoing=False))
        input_layout.addWidget(self.incoming_button)
        input_layout.addWidget(self.outgoing_button)

        self.date_edit.setDisplayFormat("d.M.y")
        self.expense_type_edit.returnPressed.connect(self.amount_edit.setFocus)
        self.amount_edit.returnPressed.connect(self.add_transaction)  # pressing enter on amount adds the transaction

        # Add the input layout to the main layout
        self.main_layout.addLayout(input_layout)

    def add_transaction(self, ingoing=True):
        # Gather data from input widgets
        date = self.date_edit.date().toPyDate()
        name = self.name_combobox.currentText()
        expense_type = self.expense_type_edit.text()
        try:
            if ingoing:
                amount = float(self.amount_edit.text())
            else:
                amount = -float(self.amount_edit.text())
        except ValueError:
            QMessageBox.critical(self, "Error", "Amount must be a number")
            return

        # Create a new transaction and add it to the register data
        new_transaction = Transaction(date, name, expense_type, amount)
        self.register_data.add_transaction(new_transaction)

        # Refresh the table to display the new transaction
        self.populate_expense_table()

        # Optionally: clear the input fields
        self.expense_type_edit.clear()
        self.amount_edit.clear()
        self.register_data.save_data()

    def handle_item_changed(self, item: QTableWidgetItem):
        # Get the row of the changed item
        row = item.row()

        # Check if the row exceeds the number of transactions (shouldn't happen, but safety check)
        if row >= len(self.register_data.transactions):
            return

        # Get the corresponding transaction from the data model
        transaction = self.register_data.transactions[row]

        # Check which column was changed and update the respective attribute
        if item.column() == 0:  # Date column
            date = datetime.strptime(item.text(), '%dd.%mm.%YYYY').date()  # Convert string to date
            transaction.date = date
        elif item.column() == 1:  # Name column
            transaction.name = item.text()
        elif item.column() == 2:  # Expense Type column
            transaction.expense_type = item.text()
        elif item.column() == 3:  # Amount column
            transaction.amount = item.text()

        # Save the updated data to the JSON file
        self.register_data.save_data()
