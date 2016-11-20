class BoundingBox(object):
    def __init__(self, south: float, west: float, north: float, east: float):
        self.south = south
        self.west = west
        self.north = north
        self.east = east

    def to_tuple(self):
        """Return data as a tuple of (x_min, y_min, x_max, y_max)"""
        return (self.west, self.south, self.east, self.north)

    def __str__(self):
        return "(s:%f, w:%f, n:%f, e:%f)" % (self.south, self.west, self.north, self.east)