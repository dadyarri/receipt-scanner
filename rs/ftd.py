from datetime import datetime
import json
import logging
from pathlib import Path
import yaml

import requests

logger = logging.getLogger("rc")


class FTD:
    """Реализация подключения к API Налоговой службы

    Args:
        keys_path: путь до файла с ключами
    """

    def __init__(self, path: str):
        """
        Инициализация API.
        """
        self.path = Path(path)
        self.url = "https://irkkt-mobile.nalog.ru:8888"

    def get_session_keys(self) -> dict:
        """Получает токены сессии из файла."""
        with open(self.path, "r") as keys_file:
            keys = yaml.safe_load(keys_file)

        return keys

    def update_session_keys(self, keys):
        """Обновляет токены сессии в файле."""
        with open(self.path, "w") as keys_file:
            yaml.dump(keys, keys_file)

    def refresh_session_keys(self):
        """Получает новые ключи сессии."""
        data = self.get_session_keys()
        data.pop("sessionId")
        headers = {
            "Device-OS": "Android",
            "Device-Id": "Samsung",
            "Content-Type": "application/json",
        }

        query = requests.post(
            f"{self.url}/v2/mobile/users/refresh",
            data=json.dumps(data),
            headers=headers,
        )

        data = self.get_session_keys()
        data.update(query.json())
        self.update_session_keys(data)

        return data

    def register_receipt(
        self,
        qr_data: str,
    ):
        """
        Регистрирует чек в системе ФНС

        Args:
            qr_data: Данные из qr-кода

        """
        url = f"{self.url}/v2/ticket"
        receipt_data = {"qr": qr_data}
        headers = {
            "Content-Type": "application/json",
            "sessionId": self.get_session_keys()["sessionId"],
        }
        query = requests.post(url, data=json.dumps(receipt_data), headers=headers)

        return query.json()["id"]

    def get_full_data_of_receipt(self, receipt_id: int) -> list:
        """Получение подробной информации о чеке
        Arguments:
            fiscal_number: Фискальный номер. 16-значное число
            fiscal_doc: Фискальный документ: Число до 10 знаков
            fiscal_sign: Фискальный признак документа: Число до 10 знаков
        """
        full_url = f"{self.url}/v2/tickets/{receipt_id}"

        query = requests.get(
            full_url,
            headers={
                "sessionId": self.get_session_keys()["sessionId"],
                "device-id": "Android",
                "device-os": "Samsung",
            },
        )
        logger.debug(query)
        logger.debug(query.text)
        logger.debug(query.url)
        logger.debug(receipt_id)

        receipt = []
        bill = query.json()["ticket"]["document"]["receipt"]
        date = datetime.strptime(
            query.json()["operation"]["date"], "%Y-%m-%dT%H:%M"
        ).date()
        if query.status_code == 200:
            for item in bill["items"]:
                item["price"] /= 100
                item["sum"] /= 100
                item["date"] = date
                receipt.append(item)
        return receipt
