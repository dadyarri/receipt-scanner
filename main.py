import os
from pathlib import Path

from PIL import Image

from nalog import Nalog
from utils import scan_qr
from utils import sort_purchases
from utils.data import Purchase

if __name__ == "__main__":
    week = int(input("Номер недели: "))
    month = int(input("Номер месяца: "))

    print("-----------")

    date = f"{week}-0{month}"

    source_path = Path(f"source/{date}")

    decoded = []
    receipt = []

    for file in source_path.rglob("*.png"):
        img = Image.open(file)
        if qr := scan_qr(img):
            decoded.append(qr)

    txt = Path(source_path, "goods.txt")
    if txt.exists():
        with open(txt, "r") as file:
            for line in file.readlines():
                item = line.split(":")
                name = item[0]
                quantity = float(item[1])
                price = float(item[2])
                receipt.append(
                    Purchase(
                        name=name, quantity=quantity, price=price, sum=quantity * price
                    )
                )

    if decoded:

        nalog = Nalog(os.environ["phone"], os.environ["password"])

        for rec in decoded:
            receipt_data = dict(
                [tuple(j.replace("\n", "").split("=")) for j in rec.split("&")]
            )
            receipt_data["s"] = receipt_data["s"].replace(".", "")

            if nalog.exist_receipt(**receipt_data):
                receipt += nalog.get_full_data_of_receipt(**receipt_data)

    for p in receipt:
        print(p)

    print("-----------")

    categories = sort_purchases(receipt)

    for index, row in categories.iterrows():
        print(
            f"{row.category.capitalize()}: {row.value} ("
            f"{round((row.value / sum(categories.value)) * 100, 2)}%)"
        )

    print("-----------")
