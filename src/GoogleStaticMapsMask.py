import numpy as np
import os
import rasterio
from geoalchemy2.shape import to_shape
from rasterio import features, Affine
from GoogleStaticMaps import GoogleStaticMaps
from RoadPolygon import RoadPolygon
from SidewalkPolygon import SidewalkPolygon

class GoogleStaticMapsMask(object):

    def __init__(self, google_static_maps: GoogleStaticMaps) -> None:
        self.google_static_maps = google_static_maps
        return

    def _get_affine_transform(self, bounding_box):
        lng1, lng2 = bounding_box.west, bounding_box.east
        lat1, lat2 = bounding_box.south, bounding_box.north
        x_scale = self.google_static_maps.image_w / (lng2 - lng1)
        y_scale = - self.google_static_maps.image_h / (lat2 - lat1)

        affine_translate = Affine.translation(-lng1, -lat2)
        affine_scale = Affine.scale(x_scale, y_scale)
        # affine_mirror = Affine(1, 0, 0, 0, -1, image_h)
        affine_transform = affine_scale * affine_translate
        return affine_transform

    def save_google_static_maps_mask_image(self, output_dir="../data/output/google_static_maps/masks/"):
        """Save the mask image"""
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        bounding_box = self.google_static_maps.get_image_bounding_box()

        # Get road polygons
        query = RoadPolygon.fetch_polygons_intersecting(bounding_box)
        road_polygons = [to_shape(poly.geom) for poly in query]

        # Get sidewalk polygons
        query = SidewalkPolygon.fetch_polygons_intersecting(bounding_box)
        sidewalk_polygons = [to_shape(poly.geom) for poly in query]

        from functools import partial
        import pyproj
        from shapely.ops import transform
        proj4 = '+proj=lcc +lat_1=38.3 +lat_2=39.45 +lat_0=37.66666666666666 +lon_0=-77 +x_0=400000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
        sidewalk_projection = partial(
            pyproj.transform,
            pyproj.Proj(proj4),  # source coordinate system
            pyproj.Proj(init='epsg:4326')
        )  # destination coordinate system

        sidewalk_polygons = [transform(sidewalk_projection, polygon) for polygon in sidewalk_polygons]

        # Rasterize polygons
        affine_transform = self._get_affine_transform(bounding_box=bounding_box)
        inverse_transform = affine_transform.__invert__()

        road_raster = self._rasterize_polygons(road_polygons, inverse_transform)
        road_raster *= 1
        sidewalk_raster = self._rasterize_polygons(sidewalk_polygons, inverse_transform)
        sidewalk_raster *= 2

        road_raster[np.where(sidewalk_raster > 0)] = sidewalk_raster[np.where(sidewalk_raster > 0)]

        # Save file
        identifier = self.google_static_maps.get_identifier()
        filename = output_dir + identifier + '.png'
        with rasterio.open(
                filename,
                'w',
                driver='PNG',
                dtype=rasterio.uint8,
                count=1,
                width=self.google_static_maps.image_w,
                height=self.google_static_maps.image_h,
                transform=inverse_transform) as dst:
            dst.write(road_raster, indexes=1)
        return

    def _rasterize_polygons(self, polygons, affine):
        out = features.rasterize(
            polygons,
            transform=affine,
            out_shape=(
                self.google_static_maps.image_w,
                self.google_static_maps.image_h
            )
        )
        return out



if __name__ == '__main__':
    gsm = GoogleStaticMaps(38.910779, -77.046662)
    # gsm.fetch_google_static_maps_image()
    gsmm = GoogleStaticMapsMask(gsm)
    gsmm.save_google_static_maps_mask_image()