class Purchase:
    def __init__(self, name: str, price: int, quantity: float, sum: int, **_):
        self.name: str = name.capitalize()
        self.price: float = price / 100
        self.quantity: float = quantity
        self.sum: float = sum / 100
        self.category: str = ""

    def __str__(self):
        return f"{self.name} ({self.price}*{self.quantity} = {self.sum})"
