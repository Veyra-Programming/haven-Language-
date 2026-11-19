"""
Ani++ & Haven Geospatial Intelligence Engine (ani.geo / haven.geo)
Standard: Open Digital Continuity Standard (ODCS) Geospatial Subsystem
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Provides Haversine great-circle distance, standard Base32 Geohashing,
geofencing (point-in-polygon ray-casting), bounding boxes, and bearing calculations.
"""

import math
from typing import List, Tuple, Dict, Optional, Union

EARTH_RADIUS_KM = 6371.0
EARTH_RADIUS_MILES = 3958.8
EARTH_RADIUS_METERS = 6371000.0

BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
BASE32_MAP = {c: i for i, c in enumerate(BASE32)}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float, unit: str = "km") -> float:
    """Calculates the great-circle distance between two points on the Earth's surface."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    if unit.lower() in ("m", "meters"):
        return EARTH_RADIUS_METERS * c
    elif unit.lower() in ("mi", "miles"):
        return EARTH_RADIUS_MILES * c
    return EARTH_RADIUS_KM * c


def initial_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the initial compass bearing (azimuth in degrees [0, 360]) from point 1 to point 2."""
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    d_lon = math.radians(lon2 - lon1)

    y = math.sin(d_lon) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(d_lon)
    theta = math.atan2(y, x)
    return (math.degrees(theta) + 360.0) % 360.0


def destination_point(lat: float, lon: float, distance_km: float, bearing_deg: float) -> Tuple[float, float]:
    """Calculates the destination coordinate from a starting point given a distance and bearing."""
    p1 = math.radians(lat)
    l1 = math.radians(lon)
    b = math.radians(bearing_deg)
    d_div_r = distance_km / EARTH_RADIUS_KM

    p2 = math.asin(math.sin(p1) * math.cos(d_div_r) + math.cos(p1) * math.sin(d_div_r) * math.cos(b))
    l2 = l1 + math.atan2(math.sin(b) * math.sin(d_div_r) * math.cos(p1),
                         math.cos(d_div_r) - math.sin(p1) * math.sin(p2))
    return (round(math.degrees(p2), 6), round((math.degrees(l2) + 540.0) % 360.0 - 180.0, 6))


def geohash_encode(lat: float, lon: float, precision: int = 9) -> str:
    """Encodes latitude and longitude into a Base32 Geohash string."""
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    geohash: List[str] = []
    bits = [16, 8, 4, 2, 1]
    bit = 0
    ch = 0
    is_even = True

    while len(geohash) < precision:
        if is_even:
            mid = (lon_interval[0] + lon_interval[1]) / 2.0
            if lon >= mid:
                ch |= bits[bit]
                lon_interval[0] = mid
            else:
                lon_interval[1] = mid
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2.0
            if lat >= mid:
                ch |= bits[bit]
                lat_interval[0] = mid
            else:
                lat_interval[1] = mid

        is_even = not is_even
        if bit < 4:
            bit += 1
        else:
            geohash.append(BASE32[ch])
            bit = 0
            ch = 0

    return "".join(geohash)


def geohash_decode(geohash: str) -> Tuple[float, float]:
    """Decodes a Base32 Geohash string into (latitude, longitude) center coordinates."""
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    is_even = True

    for c in geohash.lower():
        cd = BASE32_MAP.get(c)
        if cd is None:
            raise ValueError(f"Invalid geohash character: {c}")
        for mask in (16, 8, 4, 2, 1):
            if is_even:
                if cd & mask:
                    lon_interval[0] = (lon_interval[0] + lon_interval[1]) / 2.0
                else:
                    lon_interval[1] = (lon_interval[0] + lon_interval[1]) / 2.0
            else:
                if cd & mask:
                    lat_interval[0] = (lat_interval[0] + lat_interval[1]) / 2.0
                else:
                    lat_interval[1] = (lat_interval[0] + lat_interval[1]) / 2.0
            is_even = not is_even

    lat = (lat_interval[0] + lat_interval[1]) / 2.0
    lon = (lon_interval[0] + lon_interval[1]) / 2.0
    return (round(lat, 6), round(lon, 6))


def point_in_polygon(lat: float, lon: float, polygon: List[Tuple[float, float]]) -> bool:
    """
    Ray-casting point-in-polygon algorithm to check if coordinate (lat, lon)
    lies inside a boundary defined by a list of (lat, lon) vertices.
    """
    n = len(polygon)
    inside = False
    p1_lat, p1_lon = polygon[0]
    for i in range(1, n + 1):
        p2_lat, p2_lon = polygon[i % n]
        if lon > min(p1_lon, p2_lon):
            if lon <= max(p1_lon, p2_lon):
                if lat <= max(p1_lat, p2_lat):
                    if p1_lon != p2_lon:
                        xinters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                    if p1_lat == p2_lat or lat <= xinters:
                        inside = not inside
        p1_lat, p1_lon = p2_lat, p2_lon
    return inside


class BoundingBox:
    """Geographic bounding box defined by minimum and maximum latitude and longitude."""

    def __init__(self, min_lat: float, min_lon: float, max_lat: float, max_lon: float):
        self.min_lat = min_lat
        self.min_lon = min_lon
        self.max_lat = max_lat
        self.max_lon = max_lon

    def contains(self, lat: float, lon: float) -> bool:
        return self.min_lat <= lat <= self.max_lat and self.min_lon <= lon <= self.max_lon

    def center(self) -> Tuple[float, float]:
        return ((self.min_lat + self.max_lat) / 2.0, (self.min_lon + self.max_lon) / 2.0)

    def __repr__(self) -> str:
        return f"<BoundingBox lat=[{self.min_lat}, {self.max_lat}], lon=[{self.min_lon}, {self.max_lon}]>"
