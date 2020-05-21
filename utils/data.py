class Receipt:
    items = []


class Purchase:
    def __init__(self, name: str, price: int, quantity: float, sum: int):
        self.name: str = name
        self.price: float = price / 100
        self.quantity: float = quantity
        self.sum: float = sum / 100
        self.category: str = ""
