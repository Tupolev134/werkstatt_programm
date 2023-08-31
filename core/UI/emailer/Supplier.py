class Supplier:
    def __init__(self, handle: str, first_name: str, last_name: str, email: str, salutation: str = "Herr"):
        self.handle = handle
        self.salutation = salutation
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def to_dict(self):
        return {
            'handle': self.handle,
            'salutation': self.salutation,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data['handle'], data['first_name'], data['last_name'], data['email'], data['salutation'])
