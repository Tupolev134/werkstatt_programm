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

        # Add language selection combo box
        self.create_language_section()
        self.create_expense_list_section()
        self.create_balance_table()
        self.create_insert_section()
        self.register_data = CashRegisterData(REGISTER_PATH)
        self.populate_expense_table()

    def create_language_section(self):
        self.language_combo = QComboBox(self)
        self.language_combo.addItems(['English', 'Deutsch', 'Polski'])
        self.language_combo.currentIndexChanged.connect(self.change_language)
        self.main_layout.addWidget(self.language_combo)

    def create_balance_table(self):
        self.balance_table = QTableWidget(self)
        self.balance_table.setColumnCount(2)  # Description and Amount
        self.balance_table.setHorizontalHeaderLabels(["Description", "Amount"])
        self.balance_table.horizontalHeader().setStretchLastSection(True)
        self.balance_table.setRowCount(3)  # Sum Incoming, Sum Outgoing, Total Balance
        self.balance_table.setItem(0, 0, QTableWidgetItem("Sum Incoming"))
        self.balance_table.setItem(1, 0, QTableWidgetItem("Sum Outgoing"))
        self.balance_table.setItem(2, 0, QTableWidgetItem("Total Balance"))
        self.main_layout.addWidget(self.balance_table)

    def update_balance(self):
        sum_incoming = sum([float(transaction.amount) for transaction in self.register_data.transactions if float(transaction.amount) > 0])
        sum_outgoing = sum([float(transaction.amount) for transaction in self.register_data.transactions if float(transaction.amount) < 0])
        total_balance = sum_incoming + sum_outgoing

        self.balance_table.setItem(0, 1, QTableWidgetItem(str(sum_incoming)))
        self.balance_table.setItem(1, 1, QTableWidgetItem(str(sum_outgoing)))
        self.balance_table.setItem(2, 1, QTableWidgetItem(str(total_balance)))



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

            # Fixed the date format here
            self.expense_table.setItem(row_position, 0, QTableWidgetItem(transaction.date.strftime('%d.%m.%Y')))
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

        self.delete_button = QPushButton("Delete Selected", self)
        self.delete_button.clicked.connect(self.delete_transaction)
        self.incoming_button = QPushButton("Add Incoming Payment", self)
        self.incoming_button.clicked.connect(self.add_transaction)
        self.outgoing_button = QPushButton("Add Outgoing Payment", self)
        self.outgoing_button.clicked.connect(lambda: self.add_transaction(ingoing=False))
        input_layout.addWidget(self.incoming_button)
        input_layout.addWidget(self.outgoing_button)

        self.date_edit.setDisplayFormat("dd.MM.yyyy")
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
        self.update_balance()

        # Create a new transaction and add it to the register data
        new_transaction = Transaction(date, name, expense_type, amount)
        self.register_data.add_transaction(new_transaction)

        # Refresh the table to display the new transaction
        self.populate_expense_table()

        # Optionally: clear the input fields
        self.expense_type_edit.clear()
        self.amount_edit.clear()
        self.register_data.save_data()
    
    def delete_transaction(self):
        self.register_data.

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
            try:
                # Fixed the date format here and added error handling
                date = datetime.strptime(item.text(), '%d.%m.%Y').date()
                transaction.date = date
            except ValueError:
                QMessageBox.critical(self, "Error", "Invalid date format. Please use 'dd.mm.yyyy'")
                return
        elif item.column() == 1:  # Name column
            transaction.name = item.text()
        elif item.column() == 2:  # Expense Type column
            transaction.expense_type = item.text()
        elif item.column() == 3:  # Amount column
            transaction.amount = item.text()

        # Save the updated data to the JSON file
        self.update_balance()
        self.register_data.save_data()

    def change_language(self):
        selected_language = self.language_combo.currentText()
        translations = {
            "English": {
                "Description": "Description",
                "Amount": "Amount",
                "Sum Incoming": "Sum Incoming",
                "Sum Outgoing": "Sum Outgoing",
                "Total Balance": "Total Balance"
            },
            "Deutsch": {
                "Description": "Beschreibung",
                "Amount": "Betrag",
                "Sum Incoming": "Summe Eingehend",
                "Sum Outgoing": "Summe Ausgehend",
                "Total Balance": "Gesamtbilanz"
            },
            "Polski": {
                "Description": "Opis",
                "Amount": "Kwota",
                "Sum Incoming": "Suma Przychodów",
                "Sum Outgoing": "Suma Rozchodów",
                "Total Balance": "Saldo Końcowe"
            }
        }

        # Update UI based on the selected language
        current_translations = translations[selected_language]
        self.balance_table.setHorizontalHeaderLabels([current_translations["Description"], current_translations["Amount"]])
        self.balance_table.item(0, 0).setText(current_translations["Sum Incoming"])
        self.balance_table.item(1, 0).setText(current_translations["Sum Outgoing"])
        self.balance_table.item(2, 0).setText(current_translations["Total Balance"])

