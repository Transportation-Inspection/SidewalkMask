from __future__ import print_function
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP
from geoalchemy2 import Geometry

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func

from geoalchemy2.shape import to_shape

from BoundingBox import BoundingBox

engine = create_engine('postgresql://sidewalk:sidewalk@localhost/sidewalk_dataset', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class StreetEdge(Base):
    """
    Mapping to the street_edge table.
    """
    __tablename__ = "street_edge"
    street_edge_id = Column(Integer, primary_key=True, name="street_edge_id")
    geom = Column(Geometry("LineString", srid=4326), name="geom")
    x1 = Column(Float, name="x1")
    y1 = Column(Float, name="y1")
    x2 = Column(Float, name="x2")
    y2 = Column(Float, name="y2")
    way_type = Column(String, name="way_type")
    source = Column(Integer, name="source")
    target = Column(Integer, name="target")
    deleted = Column(Boolean, name="deleted")
    timestamp = Column(TIMESTAMP, name="timestamp")

    def __repr__(self):
        return "StreetEdge(street_edge_id=%s, x1=%s, y1=%s, x2=%s, y2=%s, way_type=%s, source=%s, target=%s, deleted=%s)" % \
               tuple(map(str, (self.street_edge_id, self.x1, self.y1, self.x2, self.y2, self.way_type, self.source, self.target, self.deleted)))

    @classmethod
    def select_street_edge(cls, session, street_edge_id):
        street_edge = session.query(StreetEdge).filter_by(street_edge_id=street_edge_id).first()
        return street_edge

    @staticmethod
    def fetch_street_edges_intersecting(bounding_box: BoundingBox):
        """Fetch all the polygons intersecting the given rectangular bounding box

        Reference
        http://geoalchemy-2.readthedocs.io/en/0.3/orm_tutorial.html#spatial-query
        """
        envelope_geom = StreetEdge._envelope(bounding_box, geom=True)
        query = session.query(StreetEdge).filter(
            func.ST_Intersects(
                func.ST_Transform(StreetEdge.geom, 4326),
                envelope_geom
            )
        )
        return query

    @staticmethod
    def fetch_street_edges_within(bounding_box):
        envelope_geom = StreetEdge._envelope(bounding_box, geom=True)
        query = session.query(StreetEdge).filter(
            func.ST_Within(
                func.ST_Transform(StreetEdge.geom, 4326),
                envelope_geom
            )
        )
        return query

    @staticmethod
    def _envelope(bounding_box, geom=True):
        envelope = """POLYGON(( %f %f, %f %f, %f %f, %f %f, %f %f ))""" % (
            bounding_box.west, bounding_box.south,
            bounding_box.west, bounding_box.north,
            bounding_box.east, bounding_box.north,
            bounding_box.east, bounding_box.south,
            bounding_box.west, bounding_box.south
        )
        if geom:
            return func.ST_GeomFromText(envelope, 4326)
        else:
            return envelope
        return



def main():
    bounding_box = BoundingBox(38.890, -77.040, 38.911, -77.005)
    query = StreetEdge.fetch_street_edges_intersecting(bounding_box)
    for poly in query:
        print(to_shape(poly.geom))

if __name__ == '__main__':
    main()
