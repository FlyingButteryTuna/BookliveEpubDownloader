import re
import cv2
import numpy as np

tnp_constants = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
                 -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 62, -1, -1, 52, 53, 54, 55,
                 56, 57, 58, 59, 60, 61, -1, -1, -1, -1, -1, -1, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, -1, -1, -1, -1, 63, -1, 26, 27, 28, 29, 30, 31, 32, 33, 34,
                 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, -1, -1, -1, -1, -1]


def cp_index(f_name):
    c = 0
    p = 0

    if f_name is not None and f_name != "":
        start_pos = f_name.rfind('/') + 1
        length = len(f_name) - start_pos

        if length > 0:
            for i in range(length):
                if i % 2 == 0:
                    p += ord(f_name[i + start_pos])
                else:
                    c += ord(f_name[i + start_pos])

            p %= 8
            c %= 8

    return {"c": c, "p": p}


class DescrabmlerType1:
    def __init__(self, stbl_arr, dtbl_arr, f_name, img_request):
        self.f_name = f_name
        cp = cp_index(f_name)
        stbl = stbl_arr[cp['c']]
        dtbl = dtbl_arr[cp['p']]

        self.valid = False
        pattern = re.compile(r'^=([0-9]+)-([0-9]+)([-+])([0-9]+)-([-_0-9A-Za-z]+)$')

        ms = pattern.match(stbl)
        md = pattern.match(dtbl)

        if ms is None or md is None:
            return

        if ms[1] != md[1] or ms[2] != md[2] or ms[4] != md[4] or ms[3] != '+' or md[3] != '-':
            return

        self.h = int(ms[1])
        self.v = int(ms[2])
        self.padding = int(ms[4])

        if self.h > 8 or self.v > 8 or self.h * self.v > 64:
            return

        rlen = self.h + self.v + self.h * self.v

        if len(ms[5]) != rlen or len(md[5]) != rlen:
            return

        self.s_str = ms[5]
        self.d_str = md[5]
        self.sn = None
        self.st = None
        self.dn = None
        self.dt = None
        self.p = None
        self.valid = True

        image_array = np.frombuffer(img_request, dtype=np.uint8)
        self.img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    def is_scrambled(self, width, height):
        aw = self.h * 2 * self.padding
        ah = self.v * 2 * self.padding
        return width >= 64 + aw and height >= 64 + ah and width * height >= (320 + aw) * (320 + ah)

    def calculate_size(self, width, height):
        if not self.is_scrambled(width, height):
            return {"width": width, "height": height}

        return {
            "width": width - self.h * 2 * self.padding,
            "height": height - self.v * 2 * self.padding
        }

    def tnp(self, input_str):
        t = [tnp_constants[ord(input_str[i])] for i in range(self.h)]
        n = [tnp_constants[ord(input_str[self.h + i])] for i in range(self.v)]
        p = [tnp_constants[ord(input_str[self.h + self.v + i])] for i in range(self.h * self.v)]

        return {"t": t, "n": n, "p": p}

    def calculate_coords(self, width, height):
        if self.p is None:
            s = self.tnp(self.s_str)
            d = self.tnp(self.d_str)
            self.sn = s['n']
            self.st = s['t']
            self.dn = d['n']
            self.dt = d['t']
            self.p = [s['p'][d['p'][i]] for i in range(self.h * self.v)]
            del s
            del d

        w = width - self.h * 2 * self.padding
        h = height - self.v * 2 * self.padding
        ww = (w + self.h - 1) // self.h
        nw = w - (self.h - 1) * ww
        hh = (h + self.v - 1) // self.v
        th = h - (self.v - 1) * hh

        coords = []
        for k in range(self.h * self.v):
            dpx = k % self.h
            dpy = k // self.h
            dx = self.padding + dpx * (ww + 2 * self.padding) + (self.dn[dpy] < dpx) * (nw - ww)
            dy = self.padding + dpy * (hh + 2 * self.padding) + (self.dt[dpx] < dpy) * (th - hh)
            spx = self.p[k] % self.h
            spy = self.p[k] // self.h
            sx = spx * ww + (self.sn[spy] < spx) * (nw - ww)
            sy = spy * hh + (self.st[spx] < spy) * (th - hh)
            pw = nw if self.dn[dpy] == dpx else ww
            ph = th if self.dt[dpx] == dpy else hh

            if w > 0 and h > 0:
                coords.append({"dx": sx, "dy": sy, "sx": dx, "sy": dy, "w": pw, "h": ph})

        return coords

    def descrabmble_img(self):
        original_height, original_width, _ = self.img.shape
        rectangles = self.calculate_coords(original_width, original_height)
        true_size = self.calculate_size(original_width, original_height)

        blank_image = 255 * np.ones((true_size['height'], true_size['width'], 3), dtype=np.uint8)

        for rect in rectangles:
            print(rect)
            piece = self.img[rect['sy']:rect['sy'] + rect['h'], rect['sx']:rect['sx'] + rect['w']].copy()
            blank_image[rect['dy']:rect['dy'] + rect['h'], rect['dx']:rect['dx'] + rect['w']] = piece

        return blank_image


def get_descrabmler(ctbl, ptbl, f_name, img):
    if ctbl[0] == "=" and ptbl[0] == "=":
        return DescrabmlerType1(ctbl, ptbl, f_name, img)
    # elif stbl[0].isdigit() and dtbl[0].isdigit():
    #    return Z1Z2CQ(stbl, dtbl)
    # elif stbl == "" and dtbl == "":
    #    return ZVA2CM()
    return None


# def desc_img(img, ctbl, ptbl):
#     tIdx = ZIX04A(img.ZKV1AZ)
#     descrambler = get_descrabmler(ctbl[tIdx["c"]], ptbl[tIdx["p"]])
#
#     if descrambler.is_valid_size(img.width, img.height):
#         descsize = descrambler.calculate_size(img.width, img.height)
#         img.orgWidth = descsize["width"]
#         img.orgHeight = descsize["height"]
#         img.descramblekeys = {"c": ctbl[tIdx["c"]], "p": ctbl[tIdx["p"]]}
#     else:
#         img.orgWidth = img.width
#         img.orgHeight = img.height
#         img.descramblekeys = None
#
#     del tIdx
#     del descrambler
