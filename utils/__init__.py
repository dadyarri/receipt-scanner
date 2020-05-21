from pathlib import Path

from PIL import Image
from pyzbar.pyzbar import decode


def scan_qr(img: Image):
    """
    Сканирует QR-код на изображении
    Args:
        img: Объект изображения

    Returns:
        str: Расшифрованный текст
    """

    qr = decode(img)
    if qr:
        return qr[0].data.decode("UTF-8")
    return ""


