import warnings
from pathlib import Path

from tabulate import tabulate

import utils

if __name__ == "__main__":

    warnings.simplefilter(action="ignore", category=UserWarning)

    week = ""
    month = ""

    while not week:
        week = input("Номер недели: ")

    while not month:
        month = input("Номер месяца: ")

    week = int(week)
    month = int(month)

    print("-----------")

    date = f"{week}-{month}"
    old_date = utils.get_previous_date(week, month)

    source_path = Path(f"source/{date}")
    old_source_path = Path(f"source/{old_date}")

    print("Сбор данных...")

    old_receipt = utils.collect_data(old_source_path)
    receipt = utils.collect_data(source_path)

    old_receipt = old_receipt[["name", "quantity", "price", "sum"]]
    receipt = receipt[["name", "quantity", "price", "sum"]]

    print("Сортировка покупок...")

    old_categories = utils.sort_purchases(old_receipt)
    categories = utils.sort_purchases(receipt)

    print(tabulate(receipt, headers="keys", tablefmt="psql", numalign="center"))

    print("Вычисление разницы между неделями...")

    diff = utils.get_difference_of_dataframes(old_categories, categories)

    print("Построение диаграммы...")

    text_of_summ = utils.get_text_of_summ(
        receipt["sum"].sum(), categories["value"].sum()
    )

    plt = utils.build_diagram(week, month, text_of_summ, categories, diff)

    try:
        plt.savefig(
            fname=f"/run/user/1000/d2f8b09b693b47c4/primary/DCIM/Camera/figure_{date}.png",
        )
    except FileNotFoundError:
        print()
        print("Не могу подключиться к целевому устройству")

    plt.show()
