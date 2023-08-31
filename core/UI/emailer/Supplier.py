class Supplier:
    def __init__(self, first_name: str, last_name: str, email: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def to_dict(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data['first_name'], data['last_name'], data['email'])