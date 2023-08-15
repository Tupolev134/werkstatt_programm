import json
import requests
from PyQt6.QtWidgets import QMessageBox

PATH_TO_BACKEND = "http://localhost:8080/api/{}"
MANUFACTURER_PART_NUMBER_ENDPOINT = "orderable_parts/manufacturer_part_number"
MANUFACTURER_PART_DESCRIPTION_ENDPOINT = "orderable_parts/manufacturer_part_description"
MANUFACTURER_NAME_ENDPOINT = "manufacturers/list_names"
PROJECT_NAME_ENDPOINT = "projects/list_names"

class Profile:
    def __init__(self, path=PATH_TO_BACKEND):
        self.path_to_backend = path
        self.kategorie = [
            "ANBAUTEILE KAROSSERIE",
            "ANTRIEBSTRANG",
            "BREMSE",
            "Fahrwerk",
            "KUPPLUNG",
            "LENKUNG",
            "MOTOR",
            "INNENRAUM",
            "AUSPUFF",
            "KRAFTSTOFFSYSTEM",
            "SCHEIBENWISCHER",
            "VERTEILERGETRIEBE",
            "ACHSEN",
            "BELEUCHTUNG",
            "GETRIEBE",
            "KÜHLER/SCHLÄUCHE",
            "TANK",
            "KAROSSERIE",
            "Schrauben Halter Edelstahl",
            "EDELSTAHLSCHRAUBEN",
            "BREMSEbzh"]
        self.artikelnummer = None
        self.projekte = None
        self.beschreibung = None
        self.haendler = None

        self.populate_data()

    def populate_data(self):
        self._populate_artikelnummer()
        self._populate_beschreibung()
        self._populate_haendler()
        self._populate_projekte()

    def _populate_projekte(self):
        response = requests.get(self.path_to_backend.format(PROJECT_NAME_ENDPOINT))
        if response.status_code == 200:
            self.projekte = response.json()

    def _populate_artikelnummer(self):
        response = requests.get(self.path_to_backend.format(MANUFACTURER_PART_NUMBER_ENDPOINT))
        if response.status_code == 200:
            self.artikelnummer = response.json()

    def _populate_beschreibung(self):
        response = requests.get(self.path_to_backend.format(MANUFACTURER_PART_DESCRIPTION_ENDPOINT))
        if response.status_code == 200:
            self.beschreibung = response.json()

    def _populate_haendler(self):
        response = requests.get(self.path_to_backend.format(MANUFACTURER_NAME_ENDPOINT))
        if response.status_code == 200:
            self.haendler = response.json()

if __name__ == '__main__':
    pr = Profile()
    pr.populate_data()
    print(pr)