from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class GeographyMatch:
    kind: str
    name: str | None
    geoid: str | None
    summary_level: str
    source_layer: str


@dataclass(frozen=True)
class GeocodedAddress:
    provider: str
    matched_address: str
    coordinates: Coordinates
    geographies: dict[str, GeographyMatch | None]
    benchmark: str | None = None
    vintage: str | None = None


@dataclass(frozen=True)
class ResolveResult:
    input_address: str
    matched_address: str
    coordinates: Coordinates
    geographies: dict[str, GeographyMatch | None]
    geocoder: str
    geography_source: str
    benchmark: str | None = None
    vintage: str | None = None

    def geoids(self) -> dict[str, str | None]:
        return {kind: match.geoid if match else None for kind, match in self.geographies.items()}

    def to_dict(self) -> dict[str, Any]:
        return {
            "input": {"address": self.input_address},
            "matched_address": self.matched_address,
            "coordinates": asdict(self.coordinates),
            "geographies": {
                kind: asdict(match) if match is not None else None
                for kind, match in self.geographies.items()
            },
            "geoids": self.geoids(),
            "metadata": {
                "geocoder": self.geocoder,
                "geography_source": self.geography_source,
                "benchmark": self.benchmark,
                "vintage": self.vintage,
            },
        }
