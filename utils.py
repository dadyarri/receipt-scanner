import logging
import os
from math import ceil
from pathlib import Path

import pandas as pd
import yaml
from PIL import Image
from pyzbar.pyzbar import decode

from ftd import FTD
from matplotlib import pyplot as plt


def scan_qr(img: Image):
    """
    Сканирует QR-код на изображении
    Args:
        img: Объект изображения

    Returns:
        str: Расшифрованный текст
    """
    logger = logging.getLogger("rc")
    qr = decode(img)
    if qr:
        decoded = qr[0].data.decode("UTF-8")
        logger.debug(f"Расшифрованный QR-код: {decoded}")
        return decoded
    return ""


def parse_qr(data: str) -> dict:
    """
    Приводит данные с QR-кода в читаемый формат
    Args:
        data: Данные с QR-кода

    Returns:
        dict: Читаемый формат
    """
    receipt_data = dict(
        [tuple(j.replace("\n", "").split("=")) for j in data.split("&")]
    )
    receipt_data["s"] = receipt_data["s"].replace(".", "")

    keys = {
        "t": "datetime",
        "s": "summ",
        "fn": "fiscal_number",
        "i": "fiscal_doc",
        "fp": "fiscal_sign",
        "n": "receipt_type",
    }

    receipt_data = dict((keys[key], value) for (key, value) in receipt_data.items())
    return receipt_data


def sort_purchases(receipt: pd.DataFrame) -> pd.DataFrame:
    """
    Сортирует покупки по категориям
    Args:
        receipt: Список покупок

    Returns:
        DataFrame: Упорядоченный по сумме трат датафрейм с категориями

    """
    logger = logging.getLogger("rc")
    categories = pd.DataFrame(columns=["category", "value"])
    products = yaml.full_load(open("products.yml", "r"))
    for category, filters in products.items():
        for fltr in filters[:-1]:
            slc = receipt.name.str.contains(fltr, regex=True, na=False, case=False)
            if slc.any():
                logger.debug(f'Найдены элементы, подходящие фильтру "{fltr}"')
                if categories[categories["category"].str.contains(category)].empty:
                    logger.debug(f'Создана категория "{category.capitalize()}"')
                    categories = categories.append(
                        {"category": category, "value": 0.0}, ignore_index=True
                    )
                categories.loc[categories["category"] == category, "value"] += ceil(
                    receipt[slc]["sum"].sum()
                )
                logger.debug(
                    f"Сумма по категории \"{category}\": {receipt[slc]['sum'].sum()} "
                    f"руб."
                )
                receipt.loc[slc, "category"] = category
    return categories.sort_values(by="value")


def collect_data(path: Path) -> pd.DataFrame:

    logger = logging.getLogger("rc")
    ftd = FTD(os.getenv("phone"), os.getenv("password"))

    frames = [
        pd.read_csv(file, names=["name", "quantity", "price"])
        for file in path.rglob("*.csv")
    ]
    if frames:
        receipt = pd.concat(frames)
        receipt["sum"] = receipt["price"] * receipt["quantity"]
    else:
        receipt = pd.DataFrame(columns=["name", "quantity", "price", "sum", "category"])

    for file in path.rglob("*.png"):
        img = Image.open(file)
        if qr := scan_qr(img):
            data = parse_qr(qr)
            if ftd.is_receipt_exists(**data):
                if r := ftd.get_full_data_of_receipt(**data):
                    receipt = receipt.append(r, ignore_index=True)
                else:
                    logger.warning(f"Данные по чеку {file} не пришли")
            else:
                logger.warning(f"Чек {file} не существует")
        else:
            logger.warning(f"Невозможно прочесть {file}")
    return receipt


def _get_legend(categories: pd.DataFrame) -> (list, list):
    legend = []
    colors = []
    products = yaml.full_load(open("products.yml", "r"))
    for index, value in categories.iterrows():
        title = value.category
        summ = r" $\bf{" + str(round(value.value)) + "  руб.}$"
        percentage = round(value.value / sum(categories.value) * 100, 2)

        legend.append(f"{title.capitalize()} {summ} ({percentage}%)")
        colors.append(products[title][-1])
    return legend, colors


def get_text_of_summ(receipt_summ, cat_summ):
    if (total := round(receipt_summ)) > round(cat_summ):
        return f"Сумма покупок: {round(cat_summ)} / {total} руб."

    return f"Сумма покупок: {round(cat_summ)} руб."


def build_diagram(
    text_of_summ: str, categories: pd.DataFrame,
):
    legend, colors = _get_legend(categories)

    fig1, ax1 = plt.subplots()
    ax1.pie(
        categories.value,
        colors=colors,
        startangle=90,
        pctdistance=0.9,
        labeldistance=None,
        explode=tuple([0.1] * len(categories)),
    )

    ax1.axis("off")

    centre_circle = plt.Circle((0, 0), 0.85, fc="white")
    fig = plt.gcf()
    fig.set_size_inches(8, 8)
    fig.gca().add_artist(centre_circle)

    plt.title(label=f"Покупки по категориям", loc="center")
    plt.text(
        x=1, y=1.5, s=text_of_summ,
    )
    plt.legend(
        labels=legend, bbox_to_anchor=(1, 0.8),
    )
    plt.axis("equal")
    plt.tight_layout()

    return plt


def get_class_name(err):
    return type(err).__name__
