from pathlib import Path

from matplotlib import pyplot as plt
from tabulate import tabulate

import utils

if __name__ == "__main__":
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

    print("Вычисление разницы между неделями...")

    diff = utils.get_difference_of_dataframes(old_categories, categories)

    print(tabulate(receipt, headers="keys", tablefmt="psql"))

    print("-----------")

    print("Построение диаграммы...")

    for item in utils.get_legend(categories, diff)[0]:
        print(item)

    print("-----------")

    if (summ := round(utils.get_summ_of_purchases(receipt))) > sum(categories.value):
        text_of_summ = (
            f"Сумма покупок: {round(sum(categories.value))} / " f"{summ} руб."
        )
    else:
        text_of_summ = f"Сумма покупок: {round(sum(categories.value))} руб."

    legend, colors = utils.get_legend(categories, diff)

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

    month_word = utils.get_name_of_month(month)

    plt.title(label=f"Покупки по категориям в {week} неделю {month_word}", loc="center")
    plt.text(
        x=1, y=1.5, s=text_of_summ,
    )
    plt.legend(
        labels=legend, bbox_to_anchor=(1, 0.8),
    )
    plt.axis("equal")
    plt.tight_layout()

    try:
        plt.savefig(
            fname=f"/run/user/1000/d2f8b09b693b47c4/primary/DCIM/Camera/figure_{date}.png",
        )
    except FileNotFoundError:
        print()
        print("Не могу подключиться к целевому устройству")

    plt.show()
