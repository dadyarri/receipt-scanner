from pathlib import Path

from matplotlib import pyplot as plt

from utils import collect_data
from utils import generate_colors
from utils import get_difference_of_dataframes
from utils import get_legend
from utils import get_previous_date
from utils import get_summ_of_purchases
from utils import sort_purchases

if __name__ == "__main__":
    week = int(input("Номер недели: "))
    month = int(input("Номер месяца: "))

    print("-----------")

    date = f"{week}-0{month}"
    old_date = get_previous_date(week, month)

    source_path = Path(f"source/{date}")
    old_source_path = Path(f"source/{old_date}")

    old_receipt = collect_data(old_source_path)
    receipt = collect_data(source_path)

    old_categories = sort_purchases(old_receipt)
    categories = sort_purchases(receipt)

    diff = get_difference_of_dataframes(old_categories, categories)

    for p in receipt:
        print(p)

    print("-----------")

    for item in get_legend(categories, diff):
        print(item)

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
        labels=get_legend(categories, diff), bbox_to_anchor=(1, 0.8),
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
