from __future__ import print_function
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float
from geoalchemy2 import Geometry

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func

from geoalchemy2.shape import to_shape

from BoundingBox import BoundingBox

engine = create_engine('postgresql://sidewalk:sidewalk@localhost/sidewalk_dataset', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class SidewalkPolygon(Base):
    __tablename__ = 'sidewalk_polygon'
    sidewalk_polygon_id = Column('sidewalk_polygon_id', Integer, primary_key=True)
    geom = Column('geom', Geometry('MULTIPOLYGON', srid=100000))
    gis_id = Column('gis_id', Integer)
    feature_code = Column('feature_code', Integer)
    description = Column('description', String)
    capture_year = Column('capture_year', Date)
    captureact = Column('captureact', String)
    shape_area = Column('shape_area', Float)
    shape_len = Column('shape_len', Float)

    @staticmethod
    def fetch_polygons_intersecting(bounding_box: BoundingBox):
        """Fetch all the polygons intersecting the given rectangular bounding box

        Reference
        http://geoalchemy-2.readthedocs.io/en/0.3/orm_tutorial.html#spatial-query
        """
        envelope = """POLYGON(( %f %f, %f %f, %f %f, %f %f, %f %f ))""" % (
                    bounding_box.west, bounding_box.south,
                    bounding_box.west, bounding_box.north,
                    bounding_box.east, bounding_box.north,
                    bounding_box.east, bounding_box.south,
                    bounding_box.west, bounding_box.south
                )
        envelope_geom = func.ST_GeomFromText(envelope, 4326)
        query = session.query(SidewalkPolygon).filter(
            func.ST_Intersects(
                func.ST_Transform(SidewalkPolygon.geom, 4326),
                envelope_geom
            )
        )
        return query


def main():
    bounding_box = BoundingBox(38.910, -77.0475, 38.9115, -77.0460)
    query = SidewalkPolygon.fetch_polygons_intersecting(bounding_box)
    for poly in query:
        # http://gis.stackexchange.com/questions/119752/reading-postgis-geometry-with-shapely
        print(to_shape(poly.geom))

if __name__ == '__main__':
    main()
