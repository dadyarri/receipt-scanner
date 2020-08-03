import logging
from datetime import datetime

import requests


class FTD:
    """Реализация подключения к API Налоговой службы

    Args:
        phone: Номер телефона для авторизации в сервисах ФНС
        password: Пароль для авторизации в сервисах ФНС
    """

    def __init__(self, phone: str, password: str):
        """
        Инициализация API.
        """
        self.phone = phone
        self.password = password

    def is_receipt_exists(
        self,
        fiscal_number: str,
        receipt_type: str,
        fiscal_doc: str,
        fiscal_sign: str,
        datetime: str,
        summ: str,
    ):
        """
        Проверка существования чека

        Args:
            fiscal_number: Фискальный номер. 16-значное число
            fiscal_doc: Фискальный документ: Число до 10 знаков
            fiscal_sign: Фискальный признак документа: Число до 10 знаков
            receipt_type: Вид кассового чека (1 - приход, 2 - возврат прихода)
            datetime: Дата совершения покупки
            summ: Сумма чека в копейках

        TODO:
            1. Понять чем отличаются непроверенные чеки от проверенных (нужен новый чек)
            2. Сканироваать трафик приложения "Проверка чеков" для получения новой
            информации об API
        """
        exist_url = (
            f"https://proverkacheka.nalog.ru:9999/v1/ofds/*/inns/*/fss/"
            f"{fiscal_number}/operations/{receipt_type}/tickets/{fiscal_doc}"
        )
        receipt_data = {
            "fiscalSign": fiscal_sign,
            "date": datetime,
            "sum": summ,
        }
        query = requests.get(exist_url, receipt_data, auth=(self.phone, self.password))

        if query.status_code == 204:
            return True
        if query.status_code == 406:
            return False

    def get_full_data_of_receipt(
        self, fiscal_number: str, fiscal_doc: str, fiscal_sign: str, **_
    ) -> list:
        """Получение подробной информации о чеке
        Arguments:
            fiscal_number: Фискальный номер. 16-значное число
            fiscal_doc: Фискальный документ: Число до 10 знаков
            fiscal_sign: Фискальный признак документа: Число до 10 знаков
        """
        full_url = (
            f"https://proverkacheka.nalog.ru:9999/v1/inns/*/kkts/*/fss"
            f"/{fiscal_number}/tickets/{fiscal_doc}?fiscalSign={fiscal_sign}&sendToEmail=no"
        )

        query = requests.get(
            full_url,
            headers={"device-id": "", "device-os": ""},
            auth=(self.phone, self.password),
        )

        receipt = []
        bill = query.json()["document"]["receipt"]
        date = datetime.strptime(bill["dateTime"], "%Y-%m-%dT%H:%M:%S").date()
        if query.status_code == 200:
            for item in bill["items"]:
                item["price"] /= 100
                item["sum"] /= 100
                item["date"] = date
                receipt.append(item)
        return receipt
