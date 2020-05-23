class Receipt:
    items = []

    def __str__(self):
        return "\n".join([str(item) for item in self.items])

    def __len__(self):
        return len(self.items)


class Purchase:
    def __init__(self, name: str, price: int, quantity: float, sum: int, **_):
        self.name: str = name
        self.price: float = price / 100
        self.quantity: float = quantity
        self.sum: float = sum / 100
        self.category: str = ""

    def __str__(self):
        return f"{self.name} ({self.price}*{self.quantity} = {self.sum})"
