import json
import urllib.parse
import random
import math


def generate_key(book_cid):
    length = 16
    rstr = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    cid = urllib.parse.quote(book_cid, safe='')

    r = ''

    for kIdx in range(length):
        r += rstr[random.randint(0, len(rstr) - 1)]

    c = cid + cid
    s = c[:length]
    t = c[-length:]

    x = 0
    y = 0
    z = 0

    key = ''
    for i, ch in enumerate(r):
        x ^= ord(r[i])
        y ^= ord(s[i])
        z ^= ord(t[i])
        key += r[i] + rstr[x + y + z & 63]

    return key


def _get_seed(input_str):
    seed = 0
    length = len(input_str)

    for i in range(length):
        seed += ord(input_str[i]) << (i % 16)

    seed &= 2147483647

    if seed == 0:
        seed = 305419896

    return seed


def _get_array(input_str, seed):
    out_str = ''
    lfsr = seed
    length = len(input_str)

    for i in range(length):
        lfsr = (lfsr >> 1) ^ (-(lfsr & 1) & 1210056708)
        char_code = ord(input_str[i]) - 32
        n = (char_code + lfsr) % 94 + 32
        out_str += chr(n)

    try:
        result = json.loads(out_str)
    except Exception as err:
        result = None
        print(err)

    return result


def _get_unicode_decimal(char, arr1, arr2):
    base = 64
    num_36 = int(char, 36)
    index = num_36 % base
    val1 = arr1[index]
    val2 = arr2[index]
    unicode_decimal = math.floor(((num_36 - index) / base - val2) / val1)
    return unicode_decimal


def deobfuscate_char(char, content_info_json):
    items = content_info_json['items'][0]
    seed = _get_seed(items['ContentID'] + ":" + items['key'])
    arr1 = _get_array(items['stbl'], seed)
    arr2 = _get_array(items['ttbl'], seed)

    return chr(_get_unicode_decimal(char, arr1, arr2))
