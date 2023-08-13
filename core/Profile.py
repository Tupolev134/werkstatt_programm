import json


class Profile:
    def __init__(self, name=None, path=None, path_to_excel=None):
        self.name = name
        self.path_to_profile = path
        self.kategorie = list()
        self.artikelnummer = list()
        self.beschreibung = list()
        self.haendler = list()

    def to_dict(self):
        return {
            "name": self.name,
            "path_to_profile": self.path_to_profile,
            "kategorie": self.kategorie,
            "artikelnummer": self.artikelnummer,
            "beschreibung": self.beschreibung,
            "haendler": self.haendler,
        }

    @classmethod
    def from_dict(cls, data: dict):
        profile = cls(data["name"], data["path_to_profile"], data["path_to_excel"])
        profile.kategorie = data.get("kategorie", [])
        profile.artikelnummer = data.get("artikelnummer", [])
        profile.beschreibung = data.get("beschreibung", [])
        profile.haendler = data.get("haendler", [])
        return profile

    def save_to_json(self, filename: str):
        with open(filename, "w") as file:
            json.dump(self.to_dict(), file)

    @classmethod
    def load_from_json(cls, filename: str):
        with open(filename, "r") as file:
            data = json.load(file)
        return cls.from_dict(data)

    def add_kategorie(self, kategorie):
        for i, (rec, count) in enumerate(self.kategorie):
            if rec == kategorie:
                self.kategorie[i] = (rec, count + 1)
                return
        self.kategorie.append((kategorie, 1))

    def add_artikelnummer(self, artikelnummer):
        for i, (org, count) in enumerate(self.artikelnummer):
            if org == artikelnummer:
                self.artikelnummer[i] = (org, count + 1)
                return
        self.artikelnummer.append((artikelnummer, 1))

    def add_beschreibung(self, beschreibung):
        for i, (ref, count) in enumerate(self.beschreibung):
            if ref == beschreibung:
                self.beschreibung[i] = (ref, count + 1)
                return
        self.beschreibung.append((beschreibung, 1))

    def add_haendler(self, haendler):
        for i, (iden, count) in enumerate(self.haendler):
            if iden == haendler:
                self.haendler[i] = (iden, count + 1)
                return
        self.haendler.append((haendler, 1))
