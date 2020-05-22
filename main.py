from pathlib import Path

from PIL import Image

from utils import scan_qr
from utils.data import Purchase
from utils.data import Receipt

if __name__ == '__main__':
    week = int(input("Номер недели: "))
    month = int(input("Номер месяца: "))

    date = f"{week}-0{month}"

    source_path = Path(f"source/{date}")

    decoded = []
    receipts = []

    for file in source_path.rglob("*.png"):
        img = Image.open(file)
        if qr := scan_qr(img):
            decoded.append(qr)

    txt = Path(source_path, "goods.txt")
    if txt.exists():
        receipts.append(Receipt())
        with open(txt, "r") as file:
            for line in file.readlines():
                item = line.split(":")
                name = item[0]
                quantity = float(item[1])
                price = float(item[2])
                receipts[-1].items.append(Purchase(name=name, quantity=quantity,
                                                   price=price, sum=quantity * price))
