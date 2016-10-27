class BoundingBox(object):
    def __init__(self, south: float, west: float, north: float, east: float):
        self.south = south
        self.west = west
        self.north = north
        self.east = east
