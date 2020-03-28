import os
import sys
import fileinput

import hashlib
from PIL import Image
from ftplib import FTP 
import qrcode
import requests
import json
import base64
from pibooth.utils import LOGGER

 
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
        img = qr.make_image(fill_color="white", back_color="black")
    else:
        img = qr.make_image(fill_color="black", back_color="white")
    img.save(filepath, "JPEG", quality=80, optimize=True, progressive=True)
    return

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

def web_upload(file, crypt_name, url, pwd):
    """Upload a file to an ssh server
    param filename: Name and path of local file
    param url: The server address
    param pwd: Password for the user on the server 
    """
    upload_status=False
    try:

        with open(file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            payload = {'pass': pwd, 'image': encoded_string, 'filename' : crypt_name}
        response = requests.post(url, json=payload)
        if response.ok and response.text == 'OK':
                upload_status = True
        else:
            LOGGER.error(response.text.encode('utf8'))
    except Exception as e:
        LOGGER.error("upload failed! " + str(e))
    return upload_status

    
def gen_hash_filename(filename):
    """Generates an hashed filename as an unique picture ID
    param filename: Filename that schould be hashed
    """
    return hashlib.sha224(str(filename).encode("utf-8")).hexdigest() + ".jpg"
