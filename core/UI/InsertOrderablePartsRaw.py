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
    QComboBox, QLineEdit, QFileDialog, QMessageBox, QFrame, QHBoxLayout, QGridLayout, QCompleter, QScrollArea, QTextEdit
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel, QDate

from core.UI.NavigationBar import NavigationBar

ORDERABLE_PART_ENDPOINT = "http://localhost:8080/api/orderable_parts"


def _get_line_widget():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    return line


class InsertOrderablePartsRaw(QMainWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.setWindowTitle("Import OrderablePart Raw")
        self.resize(950, 800)

        self.backend_profile = Profile()

        # Naming
        self.naming_section_layout = QGridLayout()

        # Kategorie
        self.last_imported_data = QLabel("No data imported yet.")
        self.raw_data_label = QLabel("Raw JSON:")
        self.raw_data_input = QTextEdit(self)
        self.raw_data_input.setFixedHeight(200)

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
        self.create_import_section()

        self.main_layout.addLayout(self.naming_section_layout)
        self.main_layout.addWidget(_get_line_widget())

        self.raise_()

    # ------------------ Sections ------------------

    def create_import_section(self):
        self.naming_section_layout.addWidget(self.last_imported_data, 0, 0)
        self.naming_section_layout.addWidget(self.raw_data_label, 1, 0)
        self.naming_section_layout.addWidget(self.raw_data_input, 1, 1)
        # self.raw_data_input.returnPressed.connect(self.import_data_btn.setFocus)

        self.naming_section_layout.addWidget(self.import_data_btn)
        self.import_data_btn.clicked.connect(self.insert_new_orderable_part)

    # ------------------ Utils ------------------

    def insert_new_orderable_part(self):
        try:
            # Convert the raw JSON string to a Python dictionary
            data = json.loads(self.raw_data_input.toPlainText())

            # Send the Python dictionary to the server
            response = requests.post(ORDERABLE_PART_ENDPOINT, json=data)

            if response.status_code == 201:
                self.reset_inputs(last_response=response)
            else:
                QMessageBox.warning(self, "Error", "Error while inserting new OrderablePart: " + response.text)

        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", "Invalid JSON format.")

    def reset_inputs(self, last_response=None):
        if last_response is not None:
            data = json.loads(last_response.text)
            formatted_data = json.dumps(data, indent=4)

            self.last_imported_data.setText(formatted_data)
        self.raw_data_input.setText("")
