import json

import requests

import epub_builder
from downloader import deofuscator_helpers
from downloader import api_requests
from bs4 import BeautifulSoup
from downloader import img_descrambler
from PIL import Image
import cv2
import numpy as np
from downloader import deofuscator


session = requests.Session()
cid = '149603_001'
api_requests.login(session, 'miller.tanaka@yandex.ru', '10012001f')

content_info_json = api_requests.get_content_info(session, cid)
arrays = [deofuscator_helpers.get_array(content_info_json['items'][0]['stbl'], content_info_json['items'][0]['seed']),
         deofuscator_helpers.get_array(content_info_json['items'][0]['ttbl'], content_info_json['items'][0]['seed'])]

content = api_requests.get_content(session, cid,
                              content_info_json['items'][0]['p'],
                              content_info_json['ShopUserID'],
                              content_info_json['items'][0]['ContentDate'])

content = json.loads(content)



content = deofuscator.process_html(content['ttx'], content_info_json)
with open('arifureta.html', 'w', encoding='utf-8') as file:
    soup = BeautifulSoup(content, 'html.parser')
    file.write(soup.prettify())
epub_builder.construct_epub(session, content, content_info_json)

# soup = BeautifulSoup(content, 'html.parser')
#
# with open('index2.xhtml', 'w', encoding='utf-8') as output_file:
#     output_file.write(content)
#
#
# with open('gakuentoshi2.xhtml', 'w', encoding='utf-8') as output_file:
#     output_file.write(soup.prettify())

# ctbl = deofuscator_helpers.get_array(content_info_json['items'][0]['ctbl'], content_info_json['items'][0]['seed'])
# ptbl = deofuscator_helpers.get_array(content_info_json['items'][0]['ptbl'], content_info_json['items'][0]['seed'])
#
#
# img = api_requests.get_img(session, '13400_001','pages/gqxEBtxq.jpg', content_info_json['items'][0]['p'],
#                      content_info_json['items'][0]['ContentDate'])
#
# desc = img_descrambler.DescrabmlerType1(ctbl, ptbl, "pages/gqxEBtxq.jpg", img)
# blank_image = desc.descrabmble_img()
# cv2.imwrite('test.jpg', blank_image)

