import time
import re
import urllib
from urllib.parse import urlencode
from downloader import deofuscator_helpers

_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/108.0.0.0 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br',
}


def get_content_info(session, cid):
    base_api_link = 'https://booklive.jp/bib-api/'
    timestamp = str(int(time.time()))
    key = deofuscation_helpers.generate_key(cid)

    url = f'{base_api_link}bibGetCntntInfo?cid={cid}&k={key}&dmytime={timestamp}'

    response = session.get(url, headers=_headers)

    if response.status_code == 200:
        result_json = response.json()
        result_json['items'][0]['seed'] = deofuscation_helpers.get_seed(cid + ":" + key)
        return result_json
    else:
        print(f'Failed to fetch content info with status code: {response.status_code}')
        return None


def get_content(session, cid, p, suid, content_date):
    base_api_link = 'https://binb.booklive.jp/bib-deliv/'
    callback_method = 'Z630XI'

    url = (f'{base_api_link}sbcGetCntnt.php?callback={callback_method}&'
           f'cid={cid}&p={p}&suid={suid}&dmytime={content_date}')

    response = session.get(url, headers=_headers)

    if response.status_code == 200:
        return response.text
    else:
        print(f'Failed to fetch content with status code: {response.status_code}')
        return None


def login(session, email, password):
    login_page = "https://booklive.jp/login"

    response = session.get(login_page, headers=_headers)

    if response.status_code != 200:
        print(f'Failed to fetch login page with status code: {response.status_code}')
        return

    token_pattern = r'<input type="hidden" name="token" value="([^"]+)">'

    match = re.search(token_pattern, response.text)
    if match:
        token_value = match.group(1)
    else:
        print("Token not found.")
        return

    payload = {
        'token': token_value,
        'mail_addr': email,
        'pswd': password,
        'from': ''
    }
    payload = urlencode(payload)
    headers = _headers
    headers['Content-Type'] = 'application/x-www-form-urlencoded'

    response = session.post(login_page + "/index", headers=headers, data=payload)

    if 'BL_LI' in session.cookies:
        print("We've logged in hehe")
    else:
        print("Incorrect credentials?")


def get_img(session, cid, src, p, content_date):
    base_api_link = 'https://binb.booklive.jp/bib-deliv/'

    url = f'{base_api_link}sbcGetImg.php?cid={cid}&src={src}&p={p}&dmytime={content_date}'

    response = session.get(url, headers=_headers)

    if response.status_code == 200:
        return response.content
    else:
        print(f'Failed to fetch img with status code: {response.status_code}')
        return None
