# coding: utf-8

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from PIL.Image import LANCZOS


def _get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item.
    Also converts the GPS Tags
    """
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data


def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the
    EXIF to degress in float format
    """
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def _get_lat_lon_from_exif(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data
    (obtained through get_exif_data above)
    """
    lat = None
    lon = None

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        def _get_if_exist(data, key):
            return data[key] if key in data else None

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon
    return lat, lon


def get_lat_lon(image_path):
    with Image.open(image_path) as im:
        exif_data = _get_exif_data(im)
    return _get_lat_lon_from_exif(exif_data)


def shape_image(img_path, max_shape):
    with Image.open(img_path) as im:
        width, height = im.size

        # resizing
        if width > max_shape[0] or height > max_shape[1]:
            ratio = max(
                float(width) / max_shape[0],
                float(height) / max_shape[1]
            )
            width, height = int(width / ratio), int(height / ratio)

            # saving exif
            exif = im.info['exif']

            res_im = im.resize((width, height), LANCZOS)
            res_im.save(img_path, exif=exif, quality=0.9)
            res_im.close()
