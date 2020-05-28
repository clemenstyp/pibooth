import os
import sys
import fileinput

import hashlib
from PIL import Image, ImageDraw
from ftplib import FTP 
import qrcode
import requests
import json
import base64
from pibooth.utils import LOGGER
import threading
from pibooth import fonts
import zlib
import datetime

def generate_qr_code(data,filepath, inverted = False):
    """Generates a qr code
    param data: The data for the qr code
    param filename: filename for the image file
    param path: Path where the code image schould be stored
    """
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,)
    qr.add_data(data)
    qr.make(fit=True)
    if inverted:
        img = qr.make_image(fill_color="white", back_color="black").convert('RGB')
    else:
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    img.save(filepath, "JPEG", quality=80, optimize=True, progressive=True)
    return

def create_qr_code_print(qr_code_image, result_image, texts, pic_crypt_name):
    width = 580
    background = Image.new('RGB', (width, 650), color=(255, 255, 255))
    img_qr = Image.open(qr_code_image)

    qr_size = (int(400), int(400))

    resized_img_qr = img_qr.resize(qr_size, Image.ANTIALIAS)

    background.paste(resized_img_qr, (90 + 30,0))

    #('Amatic-Bold', 'AmaticSC-Regular'),
    draw = ImageDraw.Draw(background)

    text_y = 370

    font_string = 'Roboto-Light'
    help = ["http://example.org", "Code: {}".format(pic_crypt_name)]

    max_width = 500
    max_height = 50

    color = (0, 0, 0)

    font_name = fonts.get_filename(font_string)
    # Use PIL to draw text because better support for fonts than OpenCV
    font = fonts.get_pil_font(help[0], font_name, max_width, max_height)
    for text in help:
        text_x = 70
        _, text_height = font.getsize(text)
        (text_width, _baseline), (offset_x, offset_y) = font.font.getsize(text)
        text_x += (max_width - text_width) // 2
        draw.text((text_x - offset_x // 2,
                   text_y + (max_height - text_height) // 2 - offset_y // 2),
                  text, color, font=font)
        text_y += text_height


    # text_y = 400
    font_string = 'Amatic-Bold'
    max_height = (650 - text_y )/2
    for text in texts:
        if not text:  # Empty string: go to next text position
            continue
        max_width = 520
        text_x = 60
        color = (0, 0, 0)

        font_name = fonts.get_filename(font_string)
        # Use PIL to draw text because better support for fonts than OpenCV
        font = fonts.get_pil_font(text, font_name, max_width, max_height)
        _, text_height = font.getsize(text)
        (text_width, _baseline), (offset_x, offset_y) = font.font.getsize(text)
        text_x += (max_width - text_width) // 2

        draw.text((text_x - offset_x // 2,
                   text_y + (max_height - text_height) // 2 - offset_y // 2),
                  text, color, font=font)
        text_y += text_height


    background.save(result_image)
    return background


def add_qr_code_to_image(qr_code_image, base_image, result_image):
    img_bg = Image.open(base_image)
    img_qr = Image.open(qr_code_image)

    qr_image_width = img_bg.size[0] * 0.4
    if img_qr.size[1] == 0:
        qr_image_height = qr_image_width
    else:
        qr_image_height = qr_image_width * img_qr.size[0] / img_qr.size[1]

    qr_size = (int(qr_image_width), int(qr_image_height))

    resized_img_qr = img_qr.resize(qr_size, Image.ANTIALIAS)

    # pos_x = (img_bg.size[0] - qr_image_width )/ 2
    # pos_y = self.size[1] * 0.1
    #
    # pos = (int(pos_x), int(pos_y))
    # self.surface.blit(small_rotated_qr_code, pos)

    #pos = (img_bg.size[0] - qr_size[0], img_bg.size[1] - qr_size[1]) # bottom right
    pos = (img_bg.size[0] - qr_size[0],0) # top right

    img_bg.paste(resized_img_qr, pos)
    img_bg.save(result_image)
    return img_bg

def black_white_image(file, black_white_file):
    image_file = Image.open(file)  # open colour image
    image_file = image_file.convert('L')  # convert image to black and white
    image_file.save(black_white_file)
    return image_file

def upload_now(file, crypt_name, url, pwd, app):
    """Upload a file to an ssh server
       param filename: Name and path of local file
       param url: The server address
       param pwd: Password for the user on the server
       """
    upload_status = False
    try:

        with open(file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            payload = {'pass': pwd, 'image': encoded_string, 'filename': crypt_name}
        response = requests.post(url, json=payload)
        if response.ok and response.text == 'OK':
            upload_status = True
        else:
            LOGGER.error(response.text.encode('utf8'))
    except Exception as e:
        LOGGER.error("upload failed! " + str(e))

    app.web_upload_sucessful = upload_status


def web_upload(file, crypt_name, url, pwd, app):
    """Upload a file to an ssh server
    param filename: Name and path of local file
    param url: The server address
    param pwd: Password for the user on the server 
    """
    upload_thread = threading.Thread(target=upload_now, args=(file, crypt_name, url, pwd, app))
    upload_thread.start()



    
def gen_hash_filename(filename):
    """Generates an hashed filename as an unique picture ID
    param filename: Filename that schould be hashed
    """
    #return hashlib.sha224(str(filename).encode("utf-8")).hexdigest()

    ts = str(int(datetime.datetime.now().timestamp()))
    hash = str(zlib.adler32(str(filename).encode("utf-8")))

    return hash[-5:] +"-" +  ts[-5:]
