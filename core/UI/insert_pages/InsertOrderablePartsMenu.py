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
    QComboBox, QLineEdit, QFileDialog, QMessageBox, QFrame, QHBoxLayout, QGridLayout, QCompleter, QScrollArea
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel, QDate

from core.UI.NavigationBar import NavigationBar

ORDERABLE_PART_ENDPOINT = "http://localhost:8080/api/orderable_parts"

def _get_line_widget():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line


def get_sorted_list(list_of_strings):
    return sorted(list_of_strings, reverse=True)


class InsertOrderablePartsMenu(QMainWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.setWindowTitle("Import OrderablePart")
        self.resize(450, 600)

        self.backend_profile = Profile()
        if self.backend_profile.artikelnummer is None:
            QMessageBox.warning(self, "Profile could not Reach Backend",
                                "No Parts Suggestions will be available. Import might fail.")

        # Naming
        self.last_imported_data = QLabel("No data imported yet.")

        # Kategorie
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

        # Create a dropdown for currency selection
        self.currency_dropdown = QComboBox(self)
        self.currency_dropdown.addItems(["€", "$", "£"])

        # Haendler
        self.haendler_label = QLabel("Haendler:")
        self.haendler_input = QLineEdit(self)

        self.import_data_btn = QPushButton("Import", self)

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
        self.feedback_section_layout = QHBoxLayout()
        self.create_feedback_section()
        self.main_layout.addLayout(self.feedback_section_layout)

        self.main_layout.addWidget(_get_line_widget())
        self.naming_section_layout = QGridLayout()
        self.create_naming_section()
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

    def create_naming_section(self):

        # Kategorie
        self.naming_section_layout.addWidget(self.kategorie_label, 1, 0)
        self.naming_section_layout.addWidget(self.kategorie_input, 1, 2)
        self.kategorie_input.returnPressed.connect(self.artikelnummer_input.setFocus)

        # Artikelnummer
        self.naming_section_layout.addWidget(self.artikelnummer_label, 2, 0)
        self.naming_section_layout.addWidget(self.artikelnummer_input, 2, 2)
        self.artikelnummer_input.returnPressed.connect(self.beschreibung_input.setFocus)

        # Beschreibung
        self.naming_section_layout.addWidget(self.beschreibung_label, 3, 0)
        self.naming_section_layout.addWidget(self.beschreibung_input, 3, 2)
        self.beschreibung_input.returnPressed.connect(self.einzelpreis_input.setFocus)

        # Einzelpreis
        self.naming_section_layout.addWidget(self.einzelpreis_label, 5, 0)
        self.naming_section_layout.addWidget(self.einzelpreis_input, 5, 2)
        self.einzelpreis_input.returnPressed.connect(self.haendler_input.setFocus)
        self.naming_section_layout.addWidget(self.currency_dropdown, 5, 1)

        # Haendler
        self.naming_section_layout.addWidget(self.haendler_label, 7, 0)
        self.naming_section_layout.addWidget(self.haendler_input, 7, 2)
        self.haendler_input.returnPressed.connect(self.import_data_btn.setFocus)

        self.naming_section_layout.addWidget(self.import_data_btn)
        self.import_data_btn.clicked.connect(self.insert_new_orderable_part)

    def create_feedback_section(self):
        self.feedback_section_layout.addWidget(self.last_imported_data)

    # ------------------ Utils ------------------

    def insert_new_orderable_part(self):
        # Get the values from the QLineEdit widgets
        beschreibung = self.beschreibung_input.text()
        kategorie = self.kategorie_input.text()
        artikelnummer = self.artikelnummer_input.text()
        haendler = self.haendler_input.text()
        einzelpreis = float(self.einzelpreis_input.text())
        selected_currency = self.currency_dropdown.currentText()

        # Construct the JSON payload
        payload = {
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
        }

        # Send the JSON payload using the requests.post method
        response = requests.post(ORDERABLE_PART_ENDPOINT, json=payload)

        # Handle the response
        if response.status_code == 201:
            pass
        else:
            QMessageBox.warning(self, "Error", "Error while inserting new OrderablePart: " + response.text)
        self.reset_inputs(response)

    def reset_inputs(self, last_response=None):
        if last_response is not None:
            data = json.loads(last_response.text)
            formatted_data = json.dumps(data, indent=4)

            self.last_imported_data.setText(formatted_data)
        self.kategorie_input.setText("")
        self.artikelnummer_input.setText("")
        self.beschreibung_input.setText("")
        self.einzelpreis_input.setText("")
        self.haendler_input.setText("")