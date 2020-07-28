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
    logger.debug("Ошибка расшифровки")
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


def get_previous_date(week: int, month: int, root_dir: str = "source") -> str:
    if n := week - 1:
        return f"{n}-{month}"
    path = Path("source")
    weeks = []
    for p in path.glob(f"*-{month - 1}"):
        weeks.append(int(str(p).replace(f"{root_dir}/", "").split("-")[0]))
    return f"{max(weeks)}-{month - 1}"


def _get_name_of_month(number: int) -> str:
    import locale
    import calendar

    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
    return calendar.month_name[number]


def collect_data(path: Path) -> pd.DataFrame:

    decoded = []
    logger = logging.getLogger("rc")
    files = [f for f in path.rglob("*.png")]

    for file in path.rglob("*.jpg"):
        img = Image.open(file)
        img.save(str(file)[:-3] + "png")
        file.unlink()

    for file in files:
        img = Image.open(file)
        if qr := scan_qr(img):
            decoded.append(qr)
        else:
            logger.warning(f"Невозможно прочесть {file}")

    frames = [
        pd.read_csv(file, names=["name", "quantity", "price"])
        for file in path.rglob("*.csv")
    ]
    if frames:
        receipt = pd.concat(frames)
        receipt["sum"] = receipt["price"] * receipt["quantity"]
    else:
        receipt = pd.DataFrame(columns=["name", "quantity", "price", "sum", "category"])

    if decoded:

        nalog = FTD(os.environ["phone"], os.environ["password"])

        for ind, rec in enumerate(decoded):

            receipt_data = parse_qr(rec)

            if nalog.is_receipt_exists(**receipt_data):
                r = nalog.get_full_data_of_receipt(**receipt_data)
                if r:
                    receipt = receipt.append(r, ignore_index=True)
                else:
                    print(f"Чек {files[ind]} не найден")
    return receipt


def get_difference_of_dataframes(
    old_frame: pd.DataFrame, new_frame: pd.DataFrame
) -> pd.DataFrame:
    df = old_frame.merge(new_frame, "left", on="category")
    df.columns = ["category", "old", "new"]
    df = df.dropna()
    df["delta"] = df["new"] - df["old"]
    return df


def _get_legend(categories: pd.DataFrame, diff: pd.DataFrame) -> (list, list):
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
            elif d < 0:
                delta = f" {d} руб."
            else:
                delta = ""
        else:
            delta = ""

        legend.append(f"{title.capitalize()} {summ} ({percentage}%){delta}")
        colors.append(products[title][-1])
    return legend, colors


def get_text_of_summ(receipt_summ, cat_summ):
    if (total := round(receipt_summ)) > round(cat_summ):
        return f"Сумма покупок: {round(cat_summ)} / {total} руб."

    return f"Сумма покупок: {round(cat_summ)} руб."


def build_diagram(
    week: int,
    month: int,
    text_of_summ: str,
    categories: pd.DataFrame,
    diff: pd.DataFrame,
):
    legend, colors = _get_legend(categories, diff)

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

    month_word = _get_name_of_month(month)

    plt.title(label=f"Покупки по категориям в {week} неделю {month_word}", loc="center")
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
