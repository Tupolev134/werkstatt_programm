import json
import re
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QGridLayout, QPushButton, QWidget, QScrollArea, QApplication, QVBoxLayout, \
    QCheckBox, QFileDialog, QLabel, QMessageBox
from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side, Alignment
import pandas as pd
import os
from openpyxl.styles import PatternFill
import win32com.client as win32

from core.UI.NavigationBar import NavigationBar
from dotenv import load_dotenv
load_dotenv()
DEFAULT_PARTS_JSON_FOLDER_PATH = os.getenv("DEFAULT_PARTS_JSON_FOLDER_PATH")


class ConvertPartsToExcelList(QMainWindow):
    def __init__(self, window_manager):
        super().__init__()
        self.setWindowTitle("Convert Parts to Excel List")
        self.resize(600, 300)

        # Initialize the folder_path to None
        self.folder_path = None

        # Naming
        self.naming_section_layout = QVBoxLayout()
        self.folder_path_label = QLabel(DEFAULT_PARTS_JSON_FOLDER_PATH, self)
        self.choose_folder_btn = QPushButton("Ordner Auswählen", self)
        self.same_folder_checkbox = QCheckBox("In gleichem Ordner speichern", self)
        self.convert_to_excel_btn = QPushButton("Alle Konvertieren", self)

        self.naming_section_layout.addWidget(self.folder_path_label)
        self.naming_section_layout.addWidget(self.choose_folder_btn)
        self.naming_section_layout.addWidget(self.same_folder_checkbox)
        self.naming_section_layout.addWidget(self.convert_to_excel_btn)

        self.choose_folder_btn.clicked.connect(self.open_folder_dialog)
        self.convert_to_excel_btn.clicked.connect(self.convert_to_excel)

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

        self.main_layout.addLayout(self.naming_section_layout)

        self.show()

    def open_folder_dialog(self):
        file_dialog = QFileDialog()
        json_filter = "JSON (*.json)"
        folder = file_dialog.getExistingDirectory()
        # folder = QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)
        if folder:
            self.folder_path = folder
            self.folder_path_label.text = folder

    def convert_to_excel(self):
        try:
            if self.folder_path:
                create_custom_formatted_excel(self.folder_path)
            else:
                self.folder_path = DEFAULT_PARTS_JSON_FOLDER_PATH
                create_custom_formatted_excel(self.folder_path)
        except Exception as e:
            print(e.__str__())
            QMessageBox.warning(self, "Error", "While parsing Data: " + e.__str__())


def sanitize_content(content):
    """Sanitize content to ensure it's encodable in 'latin-1'."""
    return content.encode('latin-1', 'ignore').decode('latin-1')


def sanitize_filename(filename):
    # Replace non-ASCII characters with their closest ASCII equivalent
    filename = filename.encode('ascii', 'ignore').decode()

    # Replace invalid filename characters with "_"
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)

    # Limit the length of the filename to 200 characters
    if len(filename) > 200:
        filename = filename[:200]

    return filename


def create_custom_formatted_excel(directory_path):
    # List all files in the directory and its subdirectories
    files = []
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in [f for f in filenames if f.endswith(".json")]:
            files.append(os.path.join(dirpath, filename))

    for file in files:
        # Read the JSON content
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract required information and put it into a DataFrame
        df_data = []
        for entry in data:
            index = sanitize_content(entry['values'].get('pos', ''))
            teilenummer = sanitize_content(entry['values'].get('partno', ''))
            name = sanitize_content(entry.get('description', '').replace('\n', ' '))
            kommentar = sanitize_content((entry['values'].get('comment', '').replace('\n', ' ')))
            menge = sanitize_content(entry['values'].get('qty', ''))
            df_data.append([index, teilenummer, name, kommentar, menge])

        # Create a new Excel workbook and worksheet
        wb = Workbook()
        ws = wb.active

        # Apply desired formatting
        font = Font(name='Arial', size=12)
        border = Border(left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin'))
        alignment = Alignment(wrap_text=True)

        # Hardcode column widths
        col_widths = [4, 10, 28, 30, 4]
        for col_index, col_width in enumerate(col_widths, start=1):
            ws.column_dimensions[chr(64 + col_index)].width = col_width

        # Extracting the heading from the filename
        try:
            filename_parts = file.replace(" - ", "_").split("_")
            heading_parts = filename_parts[5:]
            heading_parts[-1] = heading_parts[-1].replace('.json', '')
            heading = sanitize_content(" - ".join(heading_parts))
        except Exception as e:
            heading = file.replace('.json', '')

        # Insert merged cells for heading
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)
        ws['A1'].value = heading
        ws['A1'].font = font
        ws['A1'].alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # Set header background color
        header_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
        headers = ["Position", "Teilenummer", "Name", "Kommentar", "Menge"]
        for col_index, header in enumerate(headers, start=1):
            cell = ws.cell(row=2, column=col_index, value=header)
            cell.font = font
            cell.border = border
            cell.alignment = alignment
            cell.fill = header_fill

        # Write data to Excel worksheet
        row_height = 40
        for row_index, row in enumerate(df_data, start=3):
            for col_index, cell_value in enumerate(row, start=1):
                cell = ws.cell(row=row_index, column=col_index, value=cell_value)
                cell.font = font
                cell.border = border
                cell.alignment = alignment
                if col_index in [3, 4]:  # Name and Kommentar columns
                    if col_index is 3:
                        lines_required = -(-len(cell_value) // 20)
                    else:
                        lines_required = -(-len(cell_value) // 30)
                    calc_row_height = 40 + (max(0, lines_required - 2) * 15)
                    row_height = calc_row_height if calc_row_height > row_height else row_height
                    ws.row_dimensions[row_index].height = row_height
                if col_index is 5:
                    row_height = 40

        # Sanitize the heading for use as a filename
        excel_filename = file.replace('.json','.xlsx')

        # Save the Excel workbook
        wb.save(os.path.join(directory_path, excel_filename))

        # Convert the Excel workbook to PDF
        pdf_filename = sanitize_filename(heading) + ".pdf"
        excel_to_pdf(os.path.join(directory_path, excel_filename), os.path.join(directory_path, pdf_filename))

    return f"Processed {len(files)} files."


def excel_to_pdf(excel_filename, pdf_filename):
    excel = win32.Dispatch('Excel.Application')
    excel.Visible = False

    # Open the Excel workbook
    workbook = excel.Workbooks.Open(excel_filename)

    try:
        # Export the workbook to PDF
        workbook.ExportAsFixedFormat(0, pdf_filename)
    except Exception as e:
        print(f"Failed to convert {excel_filename} to PDF. {str(e)}")
    finally:
        # Close the workbook and quit Excel
        workbook.Close()
        excel.Quit()