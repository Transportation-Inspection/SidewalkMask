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


class RoadPolygon(Base):
    __tablename__ = 'road_polygon'
    __table_args__ = {'schema' : 'dc'}
    road_polygon_id = Column('road_polygon_id', Integer, primary_key=True)
    geom = Column('geom', Geometry('MULTIPOLYGON', srid=4326))
    object_id = Column('object_id', Integer)
    gis_id = Column('gis_id', String)
    feature_code = Column('feature_code', Integer)
    description = Column('description', String)
    capture_year = Column('capture_year', String)
    capture_act = Column('capture_act', String)
    shape_length = Column('shape_length', Float)
    shape_area = Column('shape_area', Float)
    capture_date = Column('capture_date', String)

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
        query = session.query(RoadPolygon).filter(
            func.ST_Intersects(
                func.ST_Transform(RoadPolygon.geom, 4326),
                envelope_geom
            )
        )
        return query


def main():
    bounding_box = BoundingBox(38.910, -77.0475, 38.9115, -77.0460)
    query = RoadPolygon.fetch_polygons_intersecting(bounding_box)
    for poly in query:
        # http://gis.stackexchange.com/questions/119752/reading-postgis-geometry-with-shapely
        print(to_shape(poly.geom))

if __name__ == '__main__':
    main()
