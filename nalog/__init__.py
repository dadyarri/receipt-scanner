import requests


class Nalog:
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

    def exist_receipt(self, fn, n, i, fp, t, s):
        """
        Проверка существования чека

        Args:
            fn: Фискальный номер. 16-значное число
            i: Фискальный документ: Число до 10 знаков
            fp: Фискальный признак документа: Число до знаков
            n: Вид кассового чека (1 - приход, 2 - возрат прихода)
            t: Дата совершения покупки
            s: Сумма чека в копейках
        """
        exist_url = (
            f"https://proverkacheka.nalog.ru:9999/v1/ofds/*/inns/*/fss/"
            f"{fn}/operations/{n}/tickets/{i}"
        )
        receipt_data = {
            "fiscalSign": fp,
            "date": t,
            "sum": s,
        }
        query = requests.get(exist_url, receipt_data, auth=(self.phone, self.password))

        if query.status_code == 204:
            return True
        if query.status_code == 406:
            return False

    def get_full_data_of_receipt(self, fn, i, fp, **_):
        """Получение подробной информации о чеке
        Arguments:
            fn: Фискальный номер. 16-значное число
            i: Фискальный документ: Число до 10 знаков
            fp: Фискальный признак документа: Число до знаков
        """
        full_url = (
            f"https://proverkacheka.nalog.ru:9999/v1/inns/*/kkts/*/fss"
            f"/{fn}/tickets/{i}?fiscalSign={fp}&sendToEmail=no"
        )

        query = requests.get(
            full_url,
            headers={"device-id": "", "device-os": ""},
            auth=(self.phone, self.password),
        )

        if query.status_code == 406:
            print("Чек не найден")
            receipt = []
        elif query.status_code == 202:
            print("Существование чека не было проверено")
            receipt = []
        elif query.status_code == 200:
            receipt = []
            for item in query.json()["document"]["receipt"]["items"]:
                item["price"] /= 100
                item["sum"] /= 100
                receipt.append(item)
        else:
            receipt = []
        return receipt
