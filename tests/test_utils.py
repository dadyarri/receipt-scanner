from pathlib import Path

import pandas as pd
from PIL import Image
from pyshould import it

import utils


class TestUtils:

    test_image = Path("source/1-6/0001.png")
    test_image_decoded = (
        "t=20200603T1725&s=198.00&fn=9289000100520657&i=45218&fp=3126471012&n=1"
    )

    test_receipt_data = {
        "datetime": "20200603T1725",
        "summ": "19800",
        "fiscal_number": "9289000100520657",
        "fiscal_doc": "45218",
        "fiscal_sign": "3126471012",
        "receipt_type": "1",
    }

    source_data = {
        "name": ["хлеб", "таб", "ручка гел"],
        "quantity": [2, 1, 5],
        "price": [27, 667, 18],
        "sum": [54, 667, 90],
    }
    source_new_data = {
        "name": ["хлеб", "молоко", "таб"],
        "quantity": [3, 1, 1],
        "price": [27, 37, 36],
        "sum": [81, 37, 36],
    }
    reference_data = {
        "category": ["хлеб", "аптека", "канцтовары"],
        "value": [54.0, 667.0, 90.0],
    }

    def test_scan_qr(self):
        img = Image.open(self.test_image)

        qr = utils.scan_qr(img)

        it(qr).should.be_equal(self.test_image_decoded)

    def test_parse_qr(self):
        data = utils.parse_qr(self.test_image_decoded)

        it(data).should.be_equal(self.test_receipt_data)

    def test_sort_purchases(self):
        source = pd.DataFrame(data=self.source_data)
        reference = pd.DataFrame(data=self.reference_data)
        categories = utils.sort_purchases(source)

        categories.equals(pd.DataFrame(data=reference).sort_values(by="value"))
