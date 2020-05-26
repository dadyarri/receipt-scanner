import os
import re
from math import ceil
from pathlib import Path

import pandas as pd
import yaml
from PIL import Image
from pyzbar.pyzbar import decode

from nalog import Nalog
from utils.data import Purchase


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


def find_whole_word(word, string):
    """Ищет в строке шаблон, отделённый пробелами
    Arguments:
        word: Шаблон для поиска
        string: Строка, где искать
    """
    return re.compile(r"\b({0})\b".format(word)).search(string)


def sort_purchases(receipt: list) -> pd.DataFrame:
    """
    Сортирует покупки по категориям
    Args:
        receipt: Список покупок

    Returns:
        DataFrame: Упорядоченный по сумме трат датафрейм с категориями
    """
    categories = {}
    products = yaml.full_load(open("products.yml", "r"))
    for purchase in receipt:
        for k, v in products.items():
            if any(find_whole_word(i, purchase.name.lower()) for i in v):
                if k not in categories:
                    categories[k] = 0.0
                categories[k] += ceil(purchase.sum)
                purchase.category = k
                break
        else:
            print(purchase)

    categories = {k: v for k, v in sorted(categories.items(), key=lambda item: item[1])}

    df = pd.DataFrame(
        {"category": list(categories.keys()), "value": list(categories.values())}
    ).sort_values(by="value")
    return df


def generate_colors(amount: int):
    """Генерирует список цветов в шестнадцатеричном формате в заданном количестве из файла colors.yml

    Arguments:
        amount: Количество цветов

    Returns:
        List[str]: Набор сгенерированных цветов
    """
    result = []
    colors = yaml.full_load(open("colors.yml", "r"))

    for i in range(amount):
        result.append(f"{colors[i]}")

    return result


def get_summ_of_purchases(receipt: list):
    summ = 0
    for purchase in receipt:
        summ += purchase.sum
    return summ


def get_previous_date(week: int, month: int):
    if n := week - 1:
        return f"{n}-{month}"
    path = Path("source")
    weeks = []
    for p in path.glob("*"):
        weeks.append(int(str(p).replace("source/", "").split("-")[0]))
    return f"{max(weeks)}-{month - 1}"


def collect_data(path):

    decoded = []
    receipt = []

    for file in path.rglob("*.png"):
        img = Image.open(file)
        if qr := scan_qr(img):
            decoded.append(qr)

    txt = Path(path, "goods.txt")
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

    return receipt


def get_difference_of_dataframes(old_frame: pd.DataFrame, new_frame: pd.DataFrame):
    df = old_frame.merge(new_frame, "left", on="category")
    df.columns = ["category", "old", "new"]
    df = df.dropna()
    df["delta"] = df["new"] - df["old"]
    return df


def get_legend(categories, diff):

    legend = []
    for index, value in categories.iterrows():
        title = value.category
        summ = round(value.value)
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

        legend.append(f"{title.capitalize()} {summ} руб. ({percentage}%){delta}")
    return legend
