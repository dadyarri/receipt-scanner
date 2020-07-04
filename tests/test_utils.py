from pathlib import Path

import pandas as pd
from PIL import Image
from pyshould import *

import utils


class TestUtils:

    source_data = {
        "name": ["хлеб", "таб", "ручка гел"],
        "quantity": [2, 1, 5],
        "price": [27, 667, 18],
        "sum": [54, 667, 90],
    }
    reference_data = {
        "category": ["хлеб", "аптека", "канцтовары"],
        "value": [54.0, 667.0, 90.0],
    }

    def test_scan_qr(self):
        img = Image.open(Path("source/1-6/0001.png"))

        qr = utils.scan_qr(img)

        qr | should.be_equal(
            "t=20200603T1725&s=198.00&fn=9289000100520657&i=45218&fp=3126471012&n=1"
        )

    def test_sort_purchases(self):
        source = pd.DataFrame(data=self.source_data)
        reference = pd.DataFrame(data=self.reference_data)
        categories = utils.sort_purchases(source)

        categories.equals(pd.DataFrame(data=reference).sort_values(by="value"))

    def test_get_name_of_month(self):
        number = 10

        month = utils.get_name_of_month(number)

        month | should.be_equal("октября")
