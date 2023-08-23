import json
import os
import re
import subprocess
import sys
from datetime import date

import requests as requests

from core.Profile import Profile
from core.ProfileController import ProfileController
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QProgressBar, \
    QComboBox, QLineEdit, QFileDialog, QMessageBox, QFrame, QHBoxLayout, QGridLayout, QCompleter, QScrollArea, \
    QDateEdit, QInputDialog, QTextEdit, QCheckBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel, QDate

from core.UI.NavigationBar import NavigationBar

ORDER_BULK_ENDPOINT = "http://localhost:8080/api/orders/parts"
WIDTH=600
HEIGHT=900


def _get_line_widget():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line


def get_sorted_list(list_of_strings):
    return sorted(list_of_strings, reverse=True)


class CustomQDateEdit(QDateEdit):
    enter_pressed = pyqtSignal()  # create a custom signal

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Return:
            self.enter_pressed.emit()


class InsertOrderPage(QMainWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.setWindowTitle("Import OrderablePart")
        self.resize(WIDTH, HEIGHT)

        self.backend_profile = Profile()
        if self.backend_profile.artikelnummer is None:
            QMessageBox.warning(self, "Profile could not Reach Backend",
                                "No Parts Suggestions will be available. Import might fail.")

        self.parts_list = []

        # ------------------ init Header fields ------------------
        self.last_imported_part = QLabel("No data imported yet.")
        self.last_imported_order = QLabel("No data imported yet.")
        self.raw_data_label = QLabel("Raw JSON:")
        self.raw_data_input = QTextEdit(self)
        self.raw_data_input.setFixedHeight(200)

        # ------------------ init Order fields ------------------

        self.order_name_label = QLabel("Name der Bestellung:")
        self.order_name_input = QLineEdit(self)

        self.order_number_label = QLabel("Rechnungsnummer:")
        self.order_number_input = QLineEdit(self)

        self.order_status_label = QLabel("Status der Bestellung")
        self.order_status_dropdown = QComboBox(self)
        self.order_status_dropdown.addItems(["UNINITIALIZED", "INITIALIZED", "IN_PROGRESS", "SHIPPED", "IN_DELIVERY",
                                             "DELIVERED","SORTED","PARTIALLY_DELIVERED",
                                             "CANCELLED","RETURNED","REFUNDED"])

        self.order_notes_label = QLabel("Anmerkungen:")
        self.order_notes_input = QLineEdit(self)

        self.order_time_taken_label = QLabel("Lieferzeit in ganzen Tagen:")
        self.order_time_taken_input = QLineEdit(self)

        self.order_porto_label = QLabel("Porto:")
        self.order_porto_input = QLineEdit(self)
        self.order_porto_qurrency_dropdown = QComboBox(self)
        self.order_porto_qurrency_dropdown.addItems(["€", "$", "£"])
        self.vst_included_checkbox = QCheckBox(self)

        self.order_invoice_date_label = QLabel("Rechnungsdatum:")
        self.order_invoice_date_input = CustomQDateEdit()
        self.order_invoice_date_input.setDate(QDate.currentDate())
        self.order_invoice_date_input.setDisplayFormat("dd.MM.yyyy")

        # ------------------ init Parts fields ------------------

        # Projekt
        self.project_label = QLabel("Projekt:")
        self. project_dropdown = QComboBox(self)
        for key, value in self.backend_profile.projekte.items():
            self.project_dropdown.addItem(key, value)
        self.kategorie_label = QLabel("Kategorie:")
        self.kategorie_input = QLineEdit(self)

        # Artikelnummer
        self.artikelnummer_label = QLabel("Artikelnummer:")
        self.artikelnummer_input = QLineEdit(self)

        # Beschreibung
        self.beschreibung_label = QLabel("Beschreibung:")
        self.beschreibung_input = QLineEdit(self)

        # Einzelpreis
        self.einzelpreis_label = QLabel("Einzelpreis:")
        self.einzelpreis_input = QLineEdit(self)

        self.currency_dropdown = QComboBox(self)
        self.currency_dropdown.addItems(["€", "$", "£"])

        # Haendler
        self.haendler_label = QLabel("Haendler:")
        self.haendler_input = QLineEdit(self)

        self.part_amount_label = QLabel("Stückzahl:")
        self.part_amount_input = QLineEdit(self)

        self.append_part_btn = QPushButton("Teil Hinzufügen:", self)
        self.import_otder_btn = QPushButton("Bestellung Importieren", self)

        # ------------------ setup Window ------------------
        central_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(central_widget)

        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        self.setMaximumHeight(rect.height())

        self.setCentralWidget(scroll_area)
        self.main_layout = QVBoxLayout(central_widget)

        # Window Manager
        self.window_manager = window_manager
        self.nav_bar = NavigationBar(self.window_manager)
        self.main_layout.addWidget(self.nav_bar)
        self.main_layout.setAlignment(self.nav_bar, Qt.AlignmentFlag.AlignTop)

        # ------------------ setup Sections ------------------
        self.feedback_section_layout = QVBoxLayout()
        self.create_feedback_section()
        self.main_layout.addLayout(self.feedback_section_layout)

        self.main_layout.addWidget(_get_line_widget())
        self.order_fields_section_layout = QGridLayout()
        self.create_order_fields_section()
        self.main_layout.addLayout(self.order_fields_section_layout)

        self.main_layout.addWidget(_get_line_widget())
        self.naming_section_layout = QGridLayout()
        self.create_part_fields_section()
        self.main_layout.addLayout(self.naming_section_layout)

        self.init_autofill_from_profile()

        self.raise_()

    def init_autofill_from_profile(self):
        kategorie_list = get_sorted_list(self.backend_profile.kategorie)
        kategorie_list_model = QStringListModel(kategorie_list, self)
        kategorie_completer = QCompleter()
        kategorie_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        kategorie_completer.setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        kategorie_completer.setModel(kategorie_list_model)
        self.kategorie_input.setCompleter(kategorie_completer)

        artikelnummer_list = get_sorted_list(self.backend_profile.artikelnummer)
        artikelnummer_list_model = QStringListModel(artikelnummer_list, self)
        artikelnummer_completer = QCompleter()
        artikelnummer_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        artikelnummer_completer.setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        artikelnummer_completer.setModel(artikelnummer_list_model)
        self.artikelnummer_input.setCompleter(artikelnummer_completer)

        beschreibung_list = get_sorted_list(self.backend_profile.beschreibung)
        beschreibung_list_model = QStringListModel(beschreibung_list, self)
        beschreibung_completer = QCompleter()
        beschreibung_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        beschreibung_completer.setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        beschreibung_completer.setModel(beschreibung_list_model)
        self.beschreibung_input.setCompleter(beschreibung_completer)

        haendler_list = get_sorted_list(self.backend_profile.haendler)
        haendler_list_model = QStringListModel(haendler_list, self)
        haendler_completer = QCompleter()
        haendler_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        haendler_completer.setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        haendler_completer.setModel(haendler_list_model)
        self.haendler_input.setCompleter(haendler_completer)

    # ------------------ Sections ------------------

    # Order Section
    def create_order_fields_section(self):
        self.order_fields_section_layout.addWidget(self.order_name_label, 0, 0)
        self.order_fields_section_layout.addWidget(self.order_name_input, 0, 2)
        self.order_name_input.returnPressed.connect(self.order_number_input.setFocus)

        self.order_fields_section_layout.addWidget(self.order_number_label, 1, 0)
        self.order_fields_section_layout.addWidget(self.order_number_input, 1, 2)
        self.order_number_input.returnPressed.connect(self.order_notes_input.setFocus)

        self.order_fields_section_layout.addWidget(self.order_status_label, 2, 0)
        self.order_fields_section_layout.addWidget(self.order_status_dropdown, 2, 2)

        self.order_fields_section_layout.addWidget(self.order_notes_label, 3, 0)
        self.order_fields_section_layout.addWidget(self.order_notes_input, 3, 2)
        self.order_notes_input.returnPressed.connect(self.order_time_taken_input.setFocus)

        self.order_fields_section_layout.addWidget(self.order_time_taken_label, 4, 0)
        self.order_fields_section_layout.addWidget(self.order_time_taken_input, 4, 2)
        self.order_time_taken_input.returnPressed.connect(self.order_porto_input.setFocus)

        self.order_fields_section_layout.addWidget(self.order_porto_label, 5, 0)
        self.order_fields_section_layout.addWidget(self.order_porto_qurrency_dropdown, 5, 1)
        self.order_fields_section_layout.addWidget(self.order_porto_input, 5, 2)
        self.order_fields_section_layout.addWidget(self.vst_included_checkbox, 5, 3)
        self.order_porto_input.returnPressed.connect(self.kategorie_input.setFocus)

        self.order_fields_section_layout.addWidget(self.order_invoice_date_label, 6, 0)
        self.order_fields_section_layout.addWidget(self.order_invoice_date_input, 6, 2)

    # Part Section
    def create_part_fields_section(self):
        # Project
        self.naming_section_layout.addWidget(self.project_label, 0, 0)
        self.naming_section_layout.addWidget(self.project_dropdown, 0, 2)

        # Kategorie
        self.naming_section_layout.addWidget(self.kategorie_label, 1, 0)
        self.naming_section_layout.addWidget(self.kategorie_input, 1, 2)
        self.kategorie_input.returnPressed.connect(self.haendler_input.setFocus)

        # Haendler
        self.naming_section_layout.addWidget(self.haendler_label, 2, 0)
        self.naming_section_layout.addWidget(self.haendler_input, 2, 2)
        self.haendler_input.returnPressed.connect(self.artikelnummer_input.setFocus)

        # Artikelnummer
        self.naming_section_layout.addWidget(self.artikelnummer_label, 3, 0)
        self.naming_section_layout.addWidget(self.artikelnummer_input, 3, 2)
        self.artikelnummer_input.returnPressed.connect(self.beschreibung_input.setFocus)

        # Beschreibung
        self.naming_section_layout.addWidget(self.beschreibung_label, 4, 0)
        self.naming_section_layout.addWidget(self.beschreibung_input, 4, 2)
        self.beschreibung_input.returnPressed.connect(self.einzelpreis_input.setFocus)

        # Einzelpreis
        self.naming_section_layout.addWidget(self.einzelpreis_label, 5, 0)
        self.naming_section_layout.addWidget(self.einzelpreis_input, 5, 2)
        self.einzelpreis_input.returnPressed.connect(self.part_amount_input.setFocus)
        self.naming_section_layout.addWidget(self.currency_dropdown, 5, 1)

        self.naming_section_layout.addWidget(self.part_amount_label, 8, 0)
        self.naming_section_layout.addWidget(self.part_amount_input, 8, 2)
        self.part_amount_input.returnPressed.connect(self.append_part_btn.setFocus)

        self.naming_section_layout.addWidget(self.append_part_btn, 9,0)
        self.append_part_btn.setAutoDefault(True)
        self.append_part_btn.clicked.connect(self.append_new_orderable_part)

        self.naming_section_layout.addWidget(self.import_otder_btn, 9, 2)
        self.import_otder_btn.setAutoDefault(True)
        self.import_otder_btn.clicked.connect(self.post_order)

    def create_feedback_section(self):
        self.feedback_section_layout.addWidget(self.raw_data_label)
        self.feedback_section_layout.addWidget(self.raw_data_input)

        self.feedback_section_layout.addWidget(self.last_imported_order)
        self.feedback_section_layout.addWidget(self.last_imported_part)

    # ------------------ Utils ------------------

    def append_new_orderable_part(self):
        beschreibung = self.beschreibung_input.text()
        kategorie = self.kategorie_input.text()
        artikelnummer = self.artikelnummer_input.text()
        haendler = self.haendler_input.text()
        vst_included = self.vst_included_checkbox.isChecked()
        try:
            einzelpreis = float(self.einzelpreis_input.text())
        except ValueError:
            preis_sting = QInputDialog.getText(self, "Error", "Bitte einen gültigen Preis eingeben!")
            einzelpreis = float(preis_sting[0])
        selected_currency = self.currency_dropdown.currentText()
        try:
            amount = int(self.part_amount_input.text())
        except ValueError:
            amount = int(QInputDialog.getText(self, "Error", "Bitte eine gültige Stückzahl eingeben!")[0])

        if not vst_included:
            einzelpreis = einzelpreis * 1.19
        # Construct the JSON payload
        orderablePart = \
        {
            "orderablePart":{
                "name": beschreibung if beschreibung else "no name entered",  # set the value to None if empty
                "category": kategorie if kategorie else "NOT_SPECIFIED",
                "price": {
                    "priceEuro": einzelpreis if selected_currency == "€" else None,
                    "priceDollar": einzelpreis if selected_currency == "$" else None,
                    "pricePound": einzelpreis if selected_currency == "£" else None,
                },
                "manufacturerInfo": {
                    "manufacturerPartDescription": beschreibung if beschreibung else None,
                    "manufacturerPartNumber": artikelnummer if artikelnummer else None,
                    "manufacturerName": haendler if haendler else None
                }
            },
            "quantity": amount if amount else 0,
            "projectId": self.project_dropdown.currentData() if self.project_dropdown.currentData() else None
        }

        self.parts_list.append(orderablePart)

        self.reset_part_inputs(orderablePart)

    def post_order(self):
        if self.raw_data_input.toPlainText():
            self.post_raw_order()
        else:
            self.parse_and_post_order_from_inputs()

    def parse_and_post_order_from_inputs(self):
        name = self.order_name_input.text()
        order_number = self.order_number_input.text()
        order_status = self.order_status_dropdown.currentText()
        notes = self.order_notes_input.text()
        order_time_taken = self.order_time_taken_input.text()
        invoice_date_qdatetime = self.order_invoice_date_input.dateTime()
        invoice_date_iso = invoice_date_qdatetime.toString(Qt.DateFormat.ISODateWithMs)
        selected_currency = self.order_porto_qurrency_dropdown.currentText()
        try:
            porto = float(self.order_porto_input.text())
        except ValueError:
            preis_tuple = QInputDialog.getText(self, "Error", "Bitte einen gültigen Preis mit PUNKT eingeben!")
            porto = float(preis_tuple[0])

        if not self.vst_included_checkbox.isChecked():
            porto = porto * 1.19

        payload = {
            "name": name if name else "no name entered",
            "orderNumber": order_number if order_number else "no order number entered",
            "orderStatus": order_status if order_status else "NOT_SPECIFIED",
            "notes": notes if notes else None,
            "orderTimeTakenInDays": order_time_taken if order_time_taken else None,
            "orderableParts": self.parts_list,
            "porto": {
                "priceEuro": porto if selected_currency == "€" else None,
                "priceDollar": porto if selected_currency == "$" else None,
                "pricePound": porto if selected_currency == "£" else None,
            },
            "invoiceDate": invoice_date_iso if invoice_date_iso else None
        }

        formatted_payload = json.dumps(payload, indent=4)
        wrapped_payload = f"<div style='max-width:800px; word-wrap:break-word;'>{formatted_payload}</div>"
        confirmation = QMessageBox.question(self, "Confirm Payload", wrapped_payload,
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        # If the user clicked 'Yes', send the request
        if confirmation == QMessageBox.StandardButton.Yes:
            response = requests.post(ORDER_BULK_ENDPOINT, json=payload)
            if response.status_code == 201:
                self.reset_page(response)
            else:
                QMessageBox.warning(self, "Error", "Error while inserting new OrderablePart: " + response.text)
        else:
            pass

    def post_raw_order(self):
        raw_data = self.raw_data_input.toPlainText()
        # remove leading and trailing newline and or spaces from raw_data
        raw_data = raw_data.strip()
        payload = json.loads(raw_data)
        formatted_payload = json.dumps(payload, indent=4)
        wrapped_payload = f"<div style='max-width:800px; word-wrap:break-word;'>{formatted_payload}</div>"
        confirmation = QMessageBox.question(self, "Confirm Payload", wrapped_payload,
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        # If the user clicked 'Yes', send the request
        if confirmation == QMessageBox.StandardButton.Yes:
            response = requests.post(ORDER_BULK_ENDPOINT, json=payload)
            if response.status_code == 201:
                self.reset_page(response)
            else:
                QMessageBox.warning(self, "Error", "Error while inserting new OrderablePart: " + response.text)
        else:
            pass

    def save_response_to_file(self, response):
        data = json.loads(response.text)
        formatted_data = json.dumps(data, indent=4)

        filename = data["name"] + ".json"
        if filename[0]:
            with open(filename[0], 'w') as f:
                f.write(formatted_data)

    def reset_page(self, response):

        self.order_name_input.setText("")
        self.order_number_input.setText("")
        self.order_status_dropdown.setCurrentIndex(0)
        self.order_notes_input.setText("")
        self.order_time_taken_input.setText("")
        self.order_invoice_date_input.setDate(QDate.currentDate())
        self.parts_list = []

        response_data = json.loads(response.text)
        self.reset_part_inputs(response_data)

        formatted_data = json.dumps(response_data, indent=4)
        self.last_imported_order.setText(f"Imported Last order price: {response_data['price']}")
        self.last_imported_part.setText(f"Number of imported Parts: {len(response_data['orderableParts'])}")
        self.order_name_input.setFocus()
        self.raw_data_input.setText("")
        # self.save_response_to_file(response)

    def reset_part_inputs(self, response_data=None):
        if response_data is not None:
            formatted_data = json.dumps(response_data, indent=4)
            self.last_imported_part.setText(f"Number of Parts: {len(self.parts_list)}")
        self.artikelnummer_input.setText("")
        self.beschreibung_input.setText("")
        self.einzelpreis_input.setText("")
        self.part_amount_input.setText("")
        self.artikelnummer_input.setFocus()
