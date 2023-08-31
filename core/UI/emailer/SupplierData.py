import json
from typing import List

from core.UI.emailer.Supplier import Supplier

class SupplierData:
    def __init__(self, filename):
        self.filename = filename
        self.suppliers = self.load_data()

    def load_data(self) -> List[Supplier]:
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
                return [Supplier.from_dict(item) for item in data]
        except FileNotFoundError:
            return []

    def save_data(self):
        with open(self.filename, "w") as file:
            data = [supplier.to_dict() for supplier in self.suppliers]
            json.dump(data, file, indent=4)

    def add_supplier(self, supplier: Supplier):
        self.suppliers.append(supplier)
        self.save_data()
