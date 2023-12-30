import json

import requests

from downloader import deofuscator_helpers
from downloader import api_requests
from bs4 import BeautifulSoup
from downloader import img_descrambler
from PIL import Image
import cv2
import numpy as np

# session = requests.Session()
# api_requests.login(session, 'miller.tanaka@yandex.ru', '10012001f')
#
# content_info_json = api_requests.get_content_info(session, "13400_001")
# arrays = [deofuscator_helpers.get_array(content_info_json['items'][0]['stbl'], content_info_json['items'][0]['seed']),
#          deofuscator_helpers.get_array(content_info_json['items'][0]['ttbl'], content_info_json['items'][0]['seed'])]
#
# print(content_info_json)
#
# print(deofuscator_helpers.deobfuscate_char("4fwu8", arrays[0], arrays[1]))
#
# print(api_requests.get_content(session, "60005391_001",
#                               content_info_json['items'][0]['p'],
#                               content_info_json['ShopUserID'],
#                               content_info_json['items'][0]['ContentDate']))

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

