import math
import dataclasses


@dataclasses.dataclass(order=True, eq=True)
class GeoCoordinate:
    """
    Coordinate set: latitude, longitude, altitude
    """
    lat: int | float | str = 0.0
    lon: int | float | str = 0.0
    alt: int | float | str = 0.0

    def __post_init__(self):
        """
        Convert to float

        :return:
        """

        try:
            if self.lat is None:
                self.lat = 0.0
            else:
                self.lat = float(self.lat)
        except ValueError:
            self.lat = 0.0

        try:
            if self.lon is None:
                self.lon = 0.0
            else:
                self.lon = float(self.lon)
        except ValueError:
            self.lon = 0.0

        try:
            if self.alt is None:
                self.alt = 0.0
            else:
                self.alt = float(self.alt)
        except ValueError:
            self.alt = 0.0

    def __bool__(self):
        return self.__len__() > 0

    def __len__(self):
        return sum((x is not None for x in dataclasses.asdict(self).values()))

    def __str__(self):
        return f'({self.lat}, {self.lon}, {self.alt})'

    def __repr__(self):
        self.__str__()

    def valid(self) -> bool:
        if self.lat is None or self.lon is None or self.alt is None:
            return False
        return 1 <= math.fabs(self.lat) <= 90 and 1 <= math.fabs(self.lon) <= 180


class GeoPair:
    def __init__(self, coord_0: GeoCoordinate, coord_1: GeoCoordinate):
        self.lat0 = math.radians(coord_0.lat)
        self.lat1 = math.radians(coord_1.lat)
        self.lon0 = math.radians(coord_0.lon)
        self.lon1 = math.radians(coord_1.lon)

        self.dlat = self.lat1 - self.lat0
        self.dlon = self.lon1 - self.lon0

        self.a0 = coord_0.alt
        self.a1 = coord_1.alt
        self.alt = self.a1 - self.a0

    @property
    def arc_radians(self):
        """
        Calculate arc angle in radians

        :return: Arc angle in radians
        """
        a = (math.sin(self.dlat / 2) ** 2)
        a += (math.cos(self.lat0) * math.cos(self.lat1) * ((math.sin(self.dlon / 2)) ** 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return c

    @property
    def arc_degrees(self):
        """
        Calculate arc angle in degrees

        :return: Arc angle in degrees
        """
        return math.degrees(self.arc_radians)

    @property
    def arc_length(self, r0=6_371_000):
        """
        Calculate arc length in meters respect to earth radius

        :param r0: Radius
        :return: Arc length
        """
        return r0 * self.arc_radians

    @property
    def ground_distance(self):
        """
        Ground distance, alias for arc length

        :return: Ground distance in meters
        """
        return self.arc_length

    @property
    def line_of_sight(self, r0=6_371_000) -> float:
        """
        Calculate line of sight in meters respect to earth radius

        :param r0: Radius
        :return: Line of sight distance
        """
        r = r0 + self.a1
        ar = self.arc_radians
        base_length = 2 * r * math.cos((math.pi - ar) / 2)

        los = base_length ** 2 + self.alt ** 2 - 2 * base_length * self.alt * math.cos(
            (math.pi + ar) / 2)

        return math.sqrt(math.fabs(los))

    @property
    def azimuth(self):
        """
        Calculate azimuth angle in degrees

        :return: Azimuth angle in degrees
        """
        a = math.sin(self.dlon) * math.cos(self.lat1)
        b = math.cos(self.lat0) * math.sin(self.lat1) - math.sin(self.lat0) * math.cos(self.lat1) * math.cos(self.dlon)
        return math.degrees(math.atan2(a, b))

    @property
    def elevation_approx(self):
        """
        Calculate elevation angle by triangle approximation

        :return: Elevation angle in degrees
        """
        return math.degrees(math.atan2(self.alt, self.arc_length))


if __name__ == '__main__':
    g1 = GeoCoordinate()
    g2 = GeoCoordinate()
    gp = GeoPair(g1, g2)

    print(gp.ground_distance)
    print(gp.line_of_sight)
    print(gp.azimuth)
    print(gp.elevation_approx)
