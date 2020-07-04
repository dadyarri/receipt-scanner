import csv
import os
import re
from math import ceil
from pathlib import Path

import pandas as pd
import yaml
from PIL import Image
from pyzbar.pyzbar import decode

from nalog import Nalog


def scan_qr(img: Image):
    """
    Сканирует QR-код на изображении
    Args:
        img: Объект изображения

    Returns:
        str: Расшифрованный текст
    """

    qr = decode(img)
    if qr:
        return qr[0].data.decode("UTF-8")
    return ""


def sort_purchases(receipt: pd.DataFrame) -> pd.DataFrame:
    """
    Сортирует покупки по категориям
    Args:
        receipt: Список покупок

    Returns:
        DataFrame: Упорядоченный по сумме трат датафрейм с категориями

    TODO:
        Рефактор с использованием фич Pandas
    """
    categories = pd.DataFrame(columns=["category", "value"])
    products = yaml.full_load(open("products.yml", "r"))
    found = False
    for ind, purchase in receipt.iterrows():
        for category, filters in products.items():
            for fltr in filters[:-1]:
                matches = re.fullmatch(rf".*\b({fltr})\b.*", purchase["name"], re.I)
                if matches is not None:
                    if categories[categories["category"].str.contains(category)].empty:
                        categories = categories.append(
                            {"category": category, "value": 0.0}, ignore_index=True
                        )
                    categories.loc[categories["category"] == category, "value"] += ceil(
                        purchase["sum"]
                    )
                    receipt.at[ind, "category"] = category
                    found = True
                    break
            if found:
                found = False
                break
        else:
            print(f"* {purchase['name']}")
    return categories.sort_values(by="value")


def get_previous_date(week: int, month: int):
    if n := week - 1:
        return f"{n}-{month}"
    path = Path("source")
    weeks = []
    for p in path.glob("*"):
        weeks.append(int(str(p).replace("source/", "").split("-")[0]))
    return f"{max(weeks)}-{month - 1}"


def get_name_of_month(number):
    months = "|января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря".split(
        "|"
    )
    return months[number]


def collect_data(path):

    decoded = []
    receipt = pd.DataFrame(columns=["name", "quantity", "price", "sum", "category"])

    for file in path.rglob("*.jpg"):
        img = Image.open(file)
        img.save(str(file)[:-3] + "png")
        file.unlink()

    for file in path.rglob("*.png"):
        img = Image.open(file)
        if qr := scan_qr(img):
            decoded.append(qr)
        else:
            print(f"Невозможно прочесть {file}")

    txt = Path(path, "goods.csv")
    if txt.exists():
        with open(txt, "r") as file:
            reader = csv.reader(file)
            for line in reader:
                name = line[0]
                quantity = float(line[1])
                price = float(line[2])
                receipt = receipt.append(
                    {
                        "name": name,
                        "quantity": quantity,
                        "price": price / 100,
                        "sum": (quantity * price) / 100,
                    },
                    ignore_index=True,
                )

    if decoded:

        nalog = Nalog(os.environ["phone"], os.environ["password"])

        for rec in decoded:
            receipt_data = dict(
                [tuple(j.replace("\n", "").split("=")) for j in rec.split("&")]
            )
            receipt_data["s"] = receipt_data["s"].replace(".", "")

            if nalog.exist_receipt(**receipt_data):
                receipt = receipt.append(
                    nalog.get_full_data_of_receipt(**receipt_data), ignore_index=True
                )
    return receipt


def get_difference_of_dataframes(old_frame: pd.DataFrame, new_frame: pd.DataFrame):
    df = old_frame.merge(new_frame, "left", on="category")
    df.columns = ["category", "old", "new"]
    df = df.dropna()
    df["delta"] = df["new"] - df["old"]
    return df


def get_legend(categories, diff):

    legend = []
    colors = []
    products = yaml.full_load(open("products.yml", "r"))
    for index, value in categories.iterrows():
        title = value.category
        summ = r" $\bf{" + str(round(value.value)) + "  руб.}$"
        percentage = round(value.value / sum(categories.value) * 100, 2)
        item = diff.loc[diff["category"] == title]
        if len(item.index) > 0:
            d = int(item["delta"].item())
            if d > 0:
                delta = f" +{d} руб."
            else:
                delta = f" {d} руб."
        else:
            delta = ""

        legend.append(f"{title.capitalize()} {summ} ({percentage}%){delta}")
        colors.append(products[title][-1])
    return legend, colors
