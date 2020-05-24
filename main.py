import os
from pathlib import Path

from PIL import Image

from nalog import Nalog
from utils import generate_colors
from utils import get_summ_of_purchases
from utils import scan_qr
from utils import sort_purchases
from utils.data import Purchase
from matplotlib import pyplot as plt

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

    if round(get_summ_of_purchases(receipt)) > sum(categories.value):
        text_of_summ = (
            f"Сумма покупок: {round(sum(categories.value))} / "
            f"{round(get_summ_of_purchases(receipt))} руб."
        )
    else:
        text_of_summ = f"Сумма покупок: {round(sum(categories.value))} руб."

    fig1, ax1 = plt.subplots()
    ax1.pie(
        categories.value,
        colors=generate_colors(len(categories)),
        startangle=90,
        pctdistance=0.9,
        labeldistance=None,
        explode=tuple([0.1] * len(categories)),
    )

    ax1.axis("off")

    centre_circle = plt.Circle((0, 0), 0.8, fc="white")
    fig = plt.gcf()
    fig.set_size_inches(8, 8)
    fig.gca().add_artist(centre_circle)

    month_word = "мая"

    plt.title(label=f"Покупки по категориям в {week} неделю {month_word}", loc="center")
    plt.text(
        x=1, y=-1.5, s=text_of_summ,
    )
    plt.legend(
        labels=[
            f"{value.category.capitalize()} {round(value.value)} руб. "
            f"({round(value.value / sum(categories.value) * 100, 2)}%)"
            for index, value in categories.iterrows()
        ],
        bbox_to_anchor=(1, 0.8),
    )
    plt.axis("equal")
    plt.tight_layout()

    plt.show()
