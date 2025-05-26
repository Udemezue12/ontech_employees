from io import BytesIO
import qrcode
from reportlab.lib.units import inch
from reportlab.platypus import Image


def generate_qr_code(data: str) -> Image:
    qr = qrcode.QRCode(box_size=2, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    temp = BytesIO()
    img.save(temp)
    temp.seek(0)
    return Image(temp, width=1*inch, height=1*inch)
