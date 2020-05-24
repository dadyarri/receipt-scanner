from itertools import islice


class Receipt:
    items = []

    def __str__(self):
        return "\n".join([str(item) for item in self.items])

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, item):
        if isinstance(item, int) and item >= 0:
            return self.items[item]
        elif isinstance(item, slice):
            return list(islice(self.items, item.start, item.stop, item.step))
        else:
            raise TypeError("Ключ должен быть типа int или slice")

    def __add__(self, other):
        return self.items + other

    def append(self, item):
        self.items.append(item)


class Purchase:
    def __init__(self, name: str, price: int, quantity: float, sum: int, **_):
        self.name: str = name
        self.price: float = price / 100
        self.quantity: float = quantity
        self.sum: float = sum / 100
        self.category: str = ""

    def __str__(self):
        return f"{self.name} ({self.price}*{self.quantity} = {self.sum})"
