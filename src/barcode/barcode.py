# functions to generate a qr code for a url

import qrcode
import tempfile
from PIL import Image, ImageDraw, ImageFont
from flask import send_file

# border margin for text in pixels
MARGIN = 10

def create_qr_code(full_url, caption):
    """
    Generates a QR code image with a caption.

    Args:
        full_url (str): The URL to encode in the QR code.
        caption (str): The text to display below the QR code.

    Returns:
        Response: A Flask response object that sends the QR code image as a PNG file.
    """
    # create the qr code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(full_url)
    qr.make(fit=True)
    
    # create the qr code image
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.convert("RGBA")
    width, height = img.size
    
    # Create a new image with extra space at the bottom
    new_height = height + 80
    new_img = Image.new("RGBA", (width, new_height), (255, 255, 255, 255))
    new_img.paste(img, (0, 0))

    # Prepare to draw text
    d = ImageDraw.Draw(new_img)
    fnt = ImageFont.load_default().font_variant(size=40)

    text = caption
    text_bbox = d.textbbox((0, 0), text, font=fnt)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((width - text_width) // 2, (height + (50 - text_height) // 2) - MARGIN)
    d.text(text_position, text, font=fnt, fill=(0, 0, 0, 255))

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        new_img.save(tmp_file, format="PNG")
        tmp_file_path = tmp_file.name

    # Return the temporary file
    return send_file(tmp_file_path, mimetype="image/png")

def generate_qr_code(base_url, site_name, language):
    """
    Generates a QR code for the translation-demo app for a a given site and language.

    Args:
        base_url (str): The base URL of the translation website.
        site_name (str): A name to distinguish the translation session (perhaps a physical site).
        language (str): The shorthand language parameter to identify the language (e.g., fr for French).

    Returns:
        Response: A Flask response object that sends the QR code image as a PNG file.
    """
    # create the url
    url = base_url + "/" + site_name + "?language=" + language
    caption = f"{site_name}\n{language}"
    return create_qr_code(url, caption)

def generate_qr_code_speaker(base_url, site_name):
    """
    Generates a QR code for the speaker page of the translation-demo app for a given site.

    Args:
        base_url (str): The base URL of the translation website.
        site_name (str): A name to distinguish the translation session (perhaps a physical site).

    Returns:
        Response: A Flask response object that sends the QR code image as a PNG file.
    """
    # create the url
    url = base_url + "/" + site_name + "/speaker"
    caption = f"{site_name}\nspeaker"
    return create_qr_code(url, caption)
