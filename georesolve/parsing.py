from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

from georesolve.models import Coordinates

COORDINATE_PAIR_RE = re.compile(
    r"^\s*([+-]?\d{1,2}(?:\.\d+)?)\s*[, ]\s*([+-]?\d{1,3}(?:\.\d+)?)\s*$"
)
URL_AT_COORDINATES_RE = re.compile(r"@([+-]?\d{1,2}(?:\.\d+)?),([+-]?\d{1,3}(?:\.\d+)?)")
URL_GOOGLE_MARKER_RE = re.compile(r"!3d([+-]?\d{1,2}(?:\.\d+)?)!4d([+-]?\d{1,3}(?:\.\d+)?)")
QUERY_COORDINATE_RE = re.compile(r"([+-]?\d{1,2}(?:\.\d+)?)\s*,\s*([+-]?\d{1,3}(?:\.\d+)?)")
URL_COORDINATE_KEYS = ("q", "query", "ll", "sll", "center", "viewpoint", "destination", "origin")
SUPPORTED_URL_SCHEMES = {"http", "https"}


def parse_coordinates(value: str) -> Coordinates | None:
    stripped = value.strip()
    return _match_to_coordinates(COORDINATE_PAIR_RE.match(stripped))


def parse_coordinates_from_url(value: str) -> Coordinates | None:
    parsed = urlparse(value.strip())
    if not parsed.scheme or not parsed.netloc:
        return None
    if parsed.scheme.lower() not in SUPPORTED_URL_SCHEMES:
        return None

    coordinates = _match_to_coordinates(URL_AT_COORDINATES_RE.search(value))
    if coordinates is not None:
        return coordinates

    coordinates = _match_to_coordinates(URL_GOOGLE_MARKER_RE.search(value))
    if coordinates is not None:
        return coordinates

    query_values = parse_qs(parsed.query)
    for key in URL_COORDINATE_KEYS:
        for candidate in query_values.get(key, []):
            coordinates = _match_to_coordinates(QUERY_COORDINATE_RE.search(candidate))
            if coordinates is not None:
                return coordinates

    return None


def parse_query_coordinates(value: str) -> Coordinates | None:
    return parse_coordinates(value) or parse_coordinates_from_url(value)


def _match_to_coordinates(match: re.Match[str] | None) -> Coordinates | None:
    if match is None:
        return None

    latitude = float(match.group(1))
    longitude = float(match.group(2))
    if not _valid_latitude(latitude) or not _valid_longitude(longitude):
        return None
    return Coordinates(latitude=latitude, longitude=longitude)


def _valid_latitude(value: float) -> bool:
    return -90.0 <= value <= 90.0


def _valid_longitude(value: float) -> bool:
    return -180.0 <= value <= 180.0
