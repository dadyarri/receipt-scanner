import logging
import math
import warnings
from pathlib import Path

import click
from tabulate import tabulate

import utils
import logger

########################
# receipt-scanner v4.0 (c) 2020-2021 dadyarri
# MIT License
########################


@click.command()
@click.option(
    "-p",
    "--path",
    type=click.Path(exists=True),
    default=".",
    help="Относительный путь до папки с данными",
)
@click.option(
    "--nd", "--no-diagram", default=False, is_flag=True, help="Не строить диаграмму"
)
@click.option("-l", "--log-level", default="INFO", help="Уровень логгирования")
def main(path: str, nd: bool, log_level: bool):

    logger = logging.getLogger("rc")
    logger.setLevel(log_level)

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
    if not nd and not receipt.dropna().empty:
        logger.info("Построение диаграммы...")

        text_of_summ = utils.get_text_of_summ(
            receipt["sum"].sum(), categories["value"].sum()
        )

        utils.build_diagram(text_of_summ, categories).show()


if __name__ == "__main__":

    warnings.simplefilter(action="ignore", category=UserWarning)
    logger = logger.init()
    
    try:
        main()
    except Exception as err:
        logger.error(f"\n\t{utils.get_class_name(err)}: {err}")

