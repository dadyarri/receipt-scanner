import re
from math import ceil

import pandas as pd
import yaml
from PIL import Image
from pyzbar.pyzbar import decode


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
                break
        else:
            print(purchase)

    categories = {k: v for k, v in sorted(categories.items(), key=lambda item: item[1])}

    df = pd.DataFrame(
        {"category": list(categories.keys()), "value": list(categories.values())}
    )
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
