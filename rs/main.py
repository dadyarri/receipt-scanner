import logging
import math
import warnings
from pathlib import Path
import argparse

from tabulate import tabulate

from rs import utils
from rs import logger

########################
# receipt-scanner v4.0 (c) 2020-2021 dadyarri
# MIT License
########################

parser = argparse.ArgumentParser(description="Сканер кассовых чеков")


def handle(path, np):
    
    logger = logging.getLogger("rc")
    logger.setLevel(level="DEBUG")
    
    source_path = Path(path)

    logger.info("Сбор данных...")
    receipt = utils.collect_data(source_path)
    receipt = receipt[["date", "name", "quantity", "price", "sum"]]

    logger.info("Сумма покупок по дням:")

    for date in receipt["date"].unique():
        summ = math.ceil(receipt.loc[receipt["date"] == date, ["sum"]].sum())
        logger.info(f"{date}: {summ} руб.")

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
    if not np and not receipt.dropna().empty:
        logger.info("Построение диаграммы...")

        text_of_summ = utils.get_text_of_summ(
            receipt["sum"].sum(), categories["value"].sum()
        )

        utils.build_diagram(text_of_summ, categories).show()


def main():

    logger = logging.getLogger("rc")
    logging.basicConfig(handlers=[logging.StreamHandler()])

    parser.add_argument("-p", "--path", type=str, help="Путь до папки с чеками", default=".")
    parser.add_argument("--np", "--no-plot", action="store_true", help="Не рисовать диаграмму")

    args = parser.parse_args()

    warnings.simplefilter(action="ignore", category=UserWarning)

    logger.debug(args)    
    try:
        handle(args.path, args.np)
    except Exception as err:
        logger.error(f"\n\t{utils.get_class_name(err)}: {err}")
