from BoundingBox import BoundingBox

import math
import os
import urllib.request
from collections import namedtuple
import logging

BoundingCoordinates = namedtuple('BoundingCoordinates', ['nw', 'ne', 'sw', 'se'])
LatLng = namedtuple('LatLng', ['lat', 'lng'])

tile_size = 256
earth_radius = 6378137  # meters
initial_resolution = 2 * math.pi * earth_radius / tile_size
origin_shift = 2 * math.pi * earth_radius / 2.0


class GoogleStaticMaps(object):

    def __init__(self, center_lat: float, center_lng: float, image_w: int=640, image_h: int=640, zoom: int=20) -> None:
        self.center_lat, self.center_lng = center_lat, center_lng
        self.image_w, self.image_h, self.zoom = image_w, image_h, zoom
        return

    def _get_google_static_maps_url(self) -> str:
        """Prepares and returns a Google Maps static image url
        URL Example: https://maps.googleapis.com/maps/api/staticmap?center=38.910779,%20-77.046662&zoom=20&size=1000x1000&maptype=satellite&key=YOUR_KEY

        Reference:
        https://developers.google.com/maps/documentation/static-maps/intro
        """
        url = "https://maps.googleapis.com/maps/api/staticmap?"
        latlng_center = "center=%f,%f" % (self.center_lat, self.center_lng)
        zoom = "zoom=%d" % self.zoom
        size = "size=%dx%d" % (self.image_h, self.image_w)
        map_type = "maptype=satellite"
        key = "key=AIzaSyBM-B6iLF3Mm8eeHf1oyWKplx8O4SkiqGE"
        parameters = [latlng_center, zoom, size, map_type, key]

        url += "&".join(parameters)
        return url

    def fetch_google_static_maps_image(self, output_dir="../data/output/google_static_maps/images/") -> None:
        """Download and save an aerial image"""
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        url = self._get_google_static_maps_url()
        identifier = self.get_identifier()
        output_filename = output_dir + identifier + ".png"

        if os.path.isfile(output_filename):
            logging.info("The file already exists: %s" % output_filename)
        else:
            urllib.request.urlretrieve(url, output_filename)
        return

    def _get_resolution(self, zoom: int) -> float:
        return initial_resolution / (2 ** zoom)

    def _pixels_to_meters(self, px: int, zoom: int) -> float:
        res = self._get_resolution(zoom)
        return px * res - origin_shift

    def _meters_to_lat_lon(self, mx: float, my: float) -> (float, float):
        lon = (mx / origin_shift) * 180.0
        lat = (my / origin_shift) * 180.0

        lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
        return lat, lon

    def _meters_to_pixels(self, mx, my):
        res = self._get_resolution(self.zoom)
        px = (mx + origin_shift) / res
        py = (my + origin_shift) / res
        return px, py

    def _lat_lon_to_meters(self, lat, lon):
        mx = lon * origin_shift / 180.0
        my = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
        my = my * origin_shift / 180.0
        return mx, my

    def get_image_bounding_box(self) -> BoundingBox:
        mx, my = self._lat_lon_to_meters(self.center_lat, self.center_lng)
        pixel_x, pixel_y = self._meters_to_pixels(mx, my)
        w_pixel_x, e_pixel_x = pixel_x - self.image_w / 2, pixel_x + self.image_w / 2
        s_pixel_y, n_pixel_y = pixel_y - self.image_h / 2, pixel_y + self.image_h / 2

        w_meter_x = self._pixels_to_meters(w_pixel_x, self.zoom)
        e_meter_x = self._pixels_to_meters(e_pixel_x, self.zoom)
        s_meter_y = self._pixels_to_meters(s_pixel_y, self.zoom)
        n_meter_y = self._pixels_to_meters(n_pixel_y, self.zoom)

        s_lat, w_lng = self._meters_to_lat_lon(w_meter_x, s_meter_y)
        n_lat, e_lng = self._meters_to_lat_lon(e_meter_x, n_meter_y)

        return BoundingBox(s_lat, w_lng, n_lat, e_lng)

    def get_identifier(self):
        return "gsm_ll%f,%f_z%d_wh%dx%d" % (self.center_lat, self.center_lng, self.zoom, self.image_w, self.image_h)

    def describe(self) -> str:
        bounding_box = self.get_image_bounding_box()
        identifier = self.get_identifier()
        description = "id:%s\n" % identifier
        description += "center:%f,%f\n" % (self.center_lat, self.center_lng)
        description += "south_west:%f,%f\n" % (bounding_box.south, bounding_box.west)
        description += "north_east:%f,%f\n" % (bounding_box.north, bounding_box.east)
        description += "image_w:%d\n" % (self.image_w,)
        description += "image_h:%d\n" % (self.image_h,)
        description += "zoom:%d\n" % (self.zoom,)
        description += "url:%s" % self._get_google_static_maps_url()
        return description

    def save_meta_data(self, output_dir="../data/output/google_static_maps/info/") -> None:
        """Save the meta data for this aerial image"""
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        description = self.describe()
        identifier = self.get_identifier()
        filename = output_dir + identifier + ".txt"

        if os.path.isfile(filename):
            logging.info("The file already exists: %s" % filename)
        else:
            with open(filename, 'w') as f:
                f.write(description)
        return


if __name__ == '__main__':
    gsm = GoogleStaticMaps(38.910779, -77.046662)


