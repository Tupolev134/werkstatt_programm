import json
from typing import List

from core.UI.cash_register.Transaction import Transaction


class CashRegisterData:
    def __init__(self, filename="cash_register_data.json"):
        self.filename = filename
        self.transactions = self.load_data()

    def load_data(self) -> List[Transaction]:
        """Load transactions from the JSON file."""
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
                return [Transaction.from_dict(item) for item in data]
        except FileNotFoundError:
            return []

    def save_data(self):
        """Save transactions to the JSON file."""
        with open(self.filename, "w") as file:
            data = [transaction.to_dict() for transaction in self.transactions]
            json.dump(data, file, indent=4)

    def add_transaction(self, transaction: Transaction):
        """Add a new transaction and save the data."""
        self.transactions.append(transaction)
        self.save_data()

    def delete_transaction(self, row):
        del self.transactions[row]