"""
Google Statisc Maps Conversion code from:
    http://gis.stackexchange.com/questions/46729/corner-coordinates-of-google-static-map-tile
"""

import math
from collections import namedtuple

BoundingCoordinates = namedtuple('BoundingCoordinates', ['nw', 'ne', 'sw', 'se'])
LatLng = namedtuple('LatLng', ['lat', 'lng'])

tile_size = 256
earth_radius = 6378137  # meters
initial_resolution = 2 * math.pi * earth_radius / tile_size
origin_shift = 2 * math.pi * earth_radius / 2.0


def get_resolution(zoom):
    return initial_resolution / (2 ** zoom)


def lat_lon_to_meters(lat, lon):
    """
    """
    mx = lon * origin_shift / 180.0
    my = math.log( math.tan((90 + lat) * math.pi / 360.0 )) / (math.pi / 180.0)
    my = my * origin_shift / 180.0
    return mx, my


def meters_to_pixels(mx, my, zoom):
    """
    """
    res = get_resolution(zoom)
    px = (mx + origin_shift) / res
    py = (my + origin_shift) / res
    return px, py


def pixels_to_meters(px, py, zoom):
    res = get_resolution(zoom)
    mx = px * res - origin_shift
    my = py * res - origin_shift
    return mx, my


def meters_to_lat_lon(mx, my):
    lon = (mx / origin_shift) * 180.0
    lat = (my / origin_shift) * 180.0

    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
    return lat, lon


def get_image_bounding_coordinates(center_lat, center_lng, image_h, image_w, zoom):
    mx, my = lat_lon_to_meters(center_lat, center_lng)
    pixel_x, pixel_y = meters_to_pixels(mx, my, zoom)
    nw_pixel_x, nw_pixel_y = pixel_x - image_w / 2, pixel_y + image_h / 2
    ne_pixel_x, ne_pixel_y = pixel_x + image_w / 2, pixel_y + image_h / 2
    sw_pixel_x, sw_pixel_y = pixel_x - image_w / 2, pixel_y - image_h / 2
    se_pixel_x, se_pixel_y = pixel_x + image_w / 2, pixel_y - image_h / 2

    nw_meter_x, nw_meter_y = pixels_to_meters(nw_pixel_x, nw_pixel_y, zoom)
    ne_meter_x, ne_meter_y = pixels_to_meters(ne_pixel_x, ne_pixel_y, zoom)
    sw_meter_x, sw_meter_y = pixels_to_meters(sw_pixel_x, sw_pixel_y, zoom)
    se_meter_x, se_meter_y = pixels_to_meters(se_pixel_x, se_pixel_y, zoom)

    nw_lat, nw_lng = meters_to_lat_lon(nw_meter_x, nw_meter_y)
    ne_lat, ne_lng = meters_to_lat_lon(ne_meter_x, ne_meter_y)
    sw_lat, sw_lng = meters_to_lat_lon(sw_meter_x, sw_meter_y)
    se_lat, se_lng = meters_to_lat_lon(se_meter_x, se_meter_y)

    nw = LatLng(nw_lat, nw_lng)
    ne = LatLng(ne_lat, ne_lng)
    sw = LatLng(sw_lat, sw_lng)
    se = LatLng(se_lat, se_lng)

    return BoundingCoordinates(nw, ne, sw, se)


def get_google_static_maps_url(lat, lng, zoom=20, height=640, width=640):
    """Prepare a GMaps static image url

    URL Example: https://maps.googleapis.com/maps/api/staticmap?center=38.910779,%20-77.046662&zoom=20&size=1000x1000&maptype=satellite&key=YOUR_KEY

    Reference:
    https://developers.google.com/maps/documentation/static-maps/intro

    :param lat:
    :param lng:
    :param zoom:
    :param height:
    :param width:
    :return:
    """
    url = "https://maps.googleapis.com/maps/api/staticmap?"
    latlng_center = "center=%s,%s" % (str(lat), str(lng))
    zoom = "zoom=%s" % str(zoom)
    size = "size=%sx%s" % (str(height), str(width))
    map_type = "maptype=satellite"
    key = "AIzaSyAErrAIxL1j5_h3AMjWCuaHdAiy3Em5Erg"
    parameters = [latlng_center, zoom, size, map_type, key]

    print(parameters)
    url += "&".join(parameters)
    return url


def save_google_static_maps_image(url, output_dir="./data/output/"):
    """Save Google Static Maps image

    :param url:
    :return:
    """

    parameters = url.split("&")
    center_parameter = next(filter(lambda parameter: "center" in parameter, parameters))
    latlng = center_parameter.split("=")[1].replace(",", "_")

    output_filename = output_dir + "coord_" + latlng + ".png"
    print(output_filename)
    urllib.request.urlretrieve(url, output_filename)


def fetch_google_static_maps_image():
    """Fetch Google Static Maps Image
    """
    url = get_google_static_maps_url(38.910779, -77.046662)
    save_google_static_maps_image(url)

