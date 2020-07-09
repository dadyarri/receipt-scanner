import os
from math import ceil
from pathlib import Path

import pandas as pd
import yaml
from PIL import Image
from pyzbar.pyzbar import decode

from ftd import FTD


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

    """
    categories = pd.DataFrame(columns=["category", "value"])
    products = yaml.full_load(open("products.yml", "r"))
    for category, filters in products.items():
        for fltr in filters[:-1]:
            slc = receipt.name.str.contains(fltr, regex=True, na=False, case=False)
            if slc.any():
                if categories[categories["category"].str.contains(category)].empty:
                    categories = categories.append(
                        {"category": category, "value": 0.0}, ignore_index=True
                    )
                categories.loc[categories["category"] == category, "value"] += ceil(
                    receipt[slc]["sum"].sum()
                )
                receipt.loc[slc, "category"] = category
    return categories.sort_values(by="value")


def get_previous_date(week: int, month: int) -> str:
    if n := week - 1:
        return f"{n}-{month}"
    path = Path("source")
    weeks = []
    for p in path.glob(f"*-{month - 1}"):
        weeks.append(int(str(p).replace("source/", "").split("-")[0]))
    return f"{max(weeks)}-{month - 1}"


def get_name_of_month(number: int) -> str:
    import locale
    import calendar

    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
    return calendar.month_name[number]


def collect_data(path: Path) -> pd.DataFrame:

    decoded = []

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

    frames = [
        pd.read_csv(file, names=["name", "quantity", "price"])
        for file in path.rglob("*.csv")
    ]
    if frames:
        receipt = pd.concat(frames)
        receipt["sum"] = receipt["price"] * receipt["quantity"] / 100
    else:
        receipt = pd.DataFrame(columns=["name", "quantity", "price", "sum", "category"])

    if decoded:

        nalog = FTD(os.environ["phone"], os.environ["password"])

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


def get_difference_of_dataframes(
    old_frame: pd.DataFrame, new_frame: pd.DataFrame
) -> pd.DataFrame:
    df = old_frame.merge(new_frame, "left", on="category")
    df.columns = ["category", "old", "new"]
    df = df.dropna()
    df["delta"] = df["new"] - df["old"]
    return df


def get_legend(categories: pd.DataFrame, diff: pd.DataFrame) -> (list, list):

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
