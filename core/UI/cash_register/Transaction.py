from datetime import datetime


class Transaction:
    def __init__(self, date, name, expense_type, amount: float):
        self.date = date
        self.name = name
        self.expense_type = expense_type
        self.amount = amount

    def to_dict(self):
        """Convert the transaction to a dictionary format."""
        return {
            "date": self.date.strftime('%Y-%m-%d'),
            "name": self.name,
            "expense_type": self.expense_type,
            "amount": self.amount
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Transaction instance from a dictionary."""
        date = datetime.strptime(data["date"], '%Y-%m-%d').date()
        return cls(date, data["name"], data["expense_type"], float(data["amount"]))
