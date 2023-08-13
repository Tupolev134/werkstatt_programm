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


def _get_line_widget():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line


def get_sorted_list(list_of_tuples):
    return [item[0] for item in sorted(list_of_tuples, key=lambda x: x[1], reverse=True)]


class CustomQDateEdit:
    pass

class InsertOrderablePartsMenu(QMainWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.setWindowTitle("Import OrderablePart")
        self.resize(450, 600)

        self.backend_profile = Profile()

        # Naming
        self.naming_section_layout = QGridLayout()

        # Kategorie
        self.kategorie_label = QLabel("Kategorie:")
        self.kategorie_input = QLineEdit()

        # Artikelnummer
        self.artikelnummer_label = QLabel("Artikelnummer:")
        self.artikelnummer_input = QLineEdit()

        # Beschreibung
        self.beschreibung_label = QLabel("Beschreibung:")
        self.beschreibung_input = QLineEdit()

        # Einzelpreis
        self.einzelpreis_label = QLabel("Einzelpreis:")
        self.einzelpreis_input = QLineEdit()

        # Gesamtpreis
        self.gesamtpreis_label = QLabel("Gesamtpreis:")
        self.gesamtpreis_input = QLineEdit()

        # Haendler
        self.haendler_label = QLabel("Haendler:")
        self.haendler_input = QLineEdit()

        self.next_button = QPushButton("Import", self)

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

        # Window Manager
        self.window_manager = window_manager
        self.nav_bar = NavigationBar(self.window_manager)
        self.main_layout.addWidget(self.nav_bar)

        # ------------------ setup Sections ------------------
        self.create_naming_section()

        self.main_layout.addLayout(self.naming_section_layout)
        self.main_layout.addWidget(_get_line_widget())

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
        self.naming_section_layout.addWidget(self.kategorie_label, 0, 0)
        self.naming_section_layout.addWidget(self.kategorie_input, 0, 2)
        self.kategorie_input.returnPressed.connect(self.artikelnummer_input.setFocus)

        # Artikelnummer
        self.naming_section_layout.addWidget(self.artikelnummer_label, 1, 0)
        self.naming_section_layout.addWidget(self.artikelnummer_input, 1, 2)
        self.artikelnummer_input.returnPressed.connect(self.beschreibung_input.setFocus)

        # Beschreibung
        self.naming_section_layout.addWidget(self.beschreibung_label, 2, 0)
        self.naming_section_layout.addWidget(self.beschreibung_input, 2, 2)
        self.beschreibung_input.returnPressed.connect(self.einzelpreis_input.setFocus)

        # Einzelpreis
        self.naming_section_layout.addWidget(self.einzelpreis_label, 5, 0)
        self.naming_section_layout.addWidget(self.einzelpreis_input, 5, 2)
        self.einzelpreis_input.returnPressed.connect(self.gesamtpreis_input.setFocus)

        def calculate_and_set_gesamtpreis():
            if self.einzelpreis_input.text() and (self.menge_darlene_input.text() or self.menge_diana_input.text()):
                einzelpreis_cleaned = self.einzelpreis_input.text().replace(',', '.')
                self.einzelpreis_input.setText(einzelpreis_cleaned)
                gesamtpreis = float(einzelpreis_cleaned) * (int(self.menge_darlene_input.text()) + int(self.menge_diana_input.text()))
                gesamtpreis_rounded = round(gesamtpreis, 2)
                self.gesamtpreis_input.setText(str(gesamtpreis_rounded))
        self.einzelpreis_input.returnPressed.connect(calculate_and_set_gesamtpreis)

        # Gesamtpreis
        self.naming_section_layout.addWidget(self.gesamtpreis_label, 6, 0)
        self.naming_section_layout.addWidget(self.gesamtpreis_input, 6, 2)
        self.gesamtpreis_input.returnPressed.connect(self.haendler_input.setFocus)

        # Haendler
        self.naming_section_layout.addWidget(self.haendler_label, 7, 0)
        self.naming_section_layout.addWidget(self.haendler_input, 7, 2)
        self.haendler_input.returnPressed.connect(self.next_button.setFocus)

        self.naming_section_layout.addWidget(self.next_button)
        self.next_button.clicked.connect(self.insert_new_orderable_part)

    # ------------------ Utils ------------------

    def insert_new_orderable_part(self):
        pass
        # response = requests.post()


    def reset_inputs(self):
        self.kategorie_input.setText("")
        self.artikelnummer_input.setText("")
        self.beschreibung_input.setText("")
        self.einzelpreis_input.setText("")
        self.gesamtpreis_input.setText("")
        self.haendler_input.setText("")