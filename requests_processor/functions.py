# coding: utf-8


def f1_score(a, b):
    return 2 * a * b / float(a + b) if (a + b) != 0 else 0.0


def lat_lng_to_grid(lat, lng):
    lng_letter_A = chr(64 + int((lng + 180) / 20) + 1)
    remainder = (lng + 180) % 20
    lng_num = int(remainder / 2)
    remainder %= 2
    lng_letter_a = chr(96 + int(remainder * 12 + 1))

    lat_letter_A = chr(64 + int((lat + 90) / 10) + 1)
    remainder = (lat + 90) % 10
    lat_num = int(remainder)
    remainder -= lat_num
    lat_letter_a = chr(96 + int(remainder * 24 + 1))
    return u"%s%s%s%s%s%s" % (
        lng_letter_A, lat_letter_A, lng_num, lat_num, lng_letter_a, lat_letter_a
    )
