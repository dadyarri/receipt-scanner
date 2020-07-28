import logging
import warnings
from pathlib import Path

from tabulate import tabulate

import utils
import logger

########################
# receipt-scanner v3.0 (c) 2020 dadyarri
# MIT License
#
# TODO:
#   1. Написать консольный интерфейс
#   2. Переписать некоторые утилиты
#
########################


def main(root_dir: Path = Path("source")):
    week = ""
    month = ""

    logger = logging.getLogger("rc")

    while not week:
        week = input("Номер недели: ")

    while not month:
        month = input("Номер месяца: ")

    week = int(week)
    month = int(month)

    print("-----------")

    date = f"{week}-{month}"

    source_path = Path(root_dir, date)

    logger.info("Сбор данных...")
    receipt = utils.collect_data(source_path)
    receipt = receipt[["name", "quantity", "price", "sum"]]

    logger.info("Сортировка покупок...")
    categories = utils.sort_purchases(receipt)

    if not receipt.dropna().empty:

        logger.info("Отсортированные элементы:")

        logger.info(
            "\n"
            + tabulate(
                receipt.dropna(),
                headers="keys",
                tablefmt="psql",
                numalign="center",
                stralign="center",
            )
        )

    if not receipt[receipt.isnull().any(axis=1)].empty:

        logger.info("Несортированные элементы:")

        logger.info(
            "\n"
            + tabulate(
                receipt[receipt.isnull().any(axis=1)].loc[
                    :, receipt.columns != "category"
                ],
                headers="keys",
                tablefmt="psql",
                numalign="center",
                stralign="center",
            )
        )

    logger.info("Построение диаграммы...")

    text_of_summ = utils.get_text_of_summ(
        receipt["sum"].sum(), categories["value"].sum()
    )

    plt = utils.build_diagram(week, month, text_of_summ, categories)

    try:
        plt.savefig(
            fname=f"/run/user/1000/d2f8b09b693b47c4/primary/DCIM/Camera/figure_{date}.png",
        )
    except FileNotFoundError:
        logger.warning("Не могу подключиться к целевому устройству")

    plt.show()


if __name__ == "__main__":

    warnings.simplefilter(action="ignore", category=UserWarning)
    logger = logger.init()

    try:
        main()
    except Exception as err:
        logger.error(f"\n\t{utils.get_class_name(err)}: {err}")
