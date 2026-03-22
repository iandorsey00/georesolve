from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from georesolve.models import Coordinates, GeocodedAddress, GeographyMatch
from georesolve.providers.base import NoMatchError, ProviderError

SUMMARY_LEVELS = {
    "state": "040",
    "county": "050",
    "place": "160",
    "zcta": "860",
    "tract": "140",
}

PLACE_LAYER_NAMES = ("Incorporated Places", "Census Designated Places")
TARGET_GEOGRAPHIES = ("state", "county", "place", "zcta", "tract")


@dataclass(frozen=True)
class CensusConfig:
    benchmark: str = "Public_AR_Current"
    vintage: str = "Current_Current"
    base_url: str = "https://geocoding.geo.census.gov/geocoder"
    timeout_seconds: float = 15.0

    @property
    def layers(self) -> str:
        return ",".join(
            [
                "States",
                "Counties",
                "Census Tracts",
                "Incorporated Places",
                "Census Designated Places",
                "2020 Census ZIP Code Tabulation Areas",
            ]
        )


class CensusGeocoderProvider:
    name = "census"

    def __init__(self, config: CensusConfig | None = None):
        self.config = config or CensusConfig()

    def geocode(self, address: str) -> GeocodedAddress:
        payload = self._request_json(
            "/geographies/onelineaddress",
            {
                "address": address,
                "benchmark": self.config.benchmark,
                "vintage": self.config.vintage,
                "layers": self.config.layers,
                "format": "json",
            },
        )
        result = payload.get("result", {})
        matches = result.get("addressMatches", [])
        if not matches:
            raise NoMatchError(f"No Census geocoding match found for address: {address}")

        match = matches[0]
        coords = match.get("coordinates") or {}
        geographies = self._normalize_geographies(match.get("geographies") or {})
        return GeocodedAddress(
            provider=self.name,
            matched_address=match.get("matchedAddress", address),
            coordinates=Coordinates(
                latitude=float(coords["y"]),
                longitude=float(coords["x"]),
            ),
            geographies=geographies,
            benchmark=self.config.benchmark,
            vintage=self.config.vintage,
        )

    def reverse_geographies(self, latitude: float, longitude: float) -> dict[str, GeographyMatch | None]:
        payload = self._request_json(
            "/geographies/coordinates",
            {
                "x": longitude,
                "y": latitude,
                "benchmark": self.config.benchmark,
                "vintage": self.config.vintage,
                "layers": self.config.layers,
                "format": "json",
            },
        )
        geographies = payload.get("result", {}).get("geographies") or {}
        return self._normalize_geographies(geographies)

    def _request_json(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.config.base_url}{path}?{urlencode(params)}"
        try:
            with urlopen(url, timeout=self.config.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except NoMatchError:
            raise
        except Exception as exc:  # pragma: no cover - exercised only on live failures
            raise ProviderError(f"Census request failed for {url}") from exc

    @classmethod
    def _normalize_geographies(cls, geographies: dict[str, list[dict[str, Any]]]) -> dict[str, GeographyMatch | None]:
        state_row = cls._first_row(geographies, "States")
        county_row = cls._first_row(geographies, "Counties")
        tract_row = cls._first_row(geographies, "Census Tracts")
        zcta_row = cls._first_row(geographies, "2020 Census ZIP Code Tabulation Areas")
        place_layer, place_row = cls._first_available_row(geographies, PLACE_LAYER_NAMES)

        return {
            "state": cls._build_match("state", "States", state_row),
            "county": cls._build_match("county", "Counties", county_row),
            "place": cls._build_match("place", place_layer, place_row),
            "zcta": cls._build_match("zcta", "2020 Census ZIP Code Tabulation Areas", zcta_row),
            "tract": cls._build_match("tract", "Census Tracts", tract_row),
        }

    @staticmethod
    def _first_row(geographies: dict[str, list[dict[str, Any]]], layer_name: str) -> dict[str, Any] | None:
        rows = geographies.get(layer_name) or []
        return rows[0] if rows else None

    @classmethod
    def _first_available_row(
        cls,
        geographies: dict[str, list[dict[str, Any]]],
        layer_names: tuple[str, ...],
    ) -> tuple[str, dict[str, Any] | None]:
        for layer_name in layer_names:
            row = cls._first_row(geographies, layer_name)
            if row is not None:
                return layer_name, row
        return layer_names[0], None

    @classmethod
    def _build_match(
        cls,
        kind: str,
        layer_name: str,
        row: dict[str, Any] | None,
    ) -> GeographyMatch | None:
        if row is None:
            return None
        return GeographyMatch(
            kind=kind,
            name=cls._extract_name(kind, row),
            geoid=cls._extract_geoid(kind, row),
            summary_level=SUMMARY_LEVELS[kind],
            source_layer=layer_name,
        )

    @staticmethod
    def _extract_name(kind: str, row: dict[str, Any]) -> str | None:
        if kind == "zcta":
            return row.get("BASENAME") or row.get("NAME") or row.get("GEOID")
        return row.get("NAME") or row.get("BASENAME") or row.get("GEOID")

    @staticmethod
    def _extract_geoid(kind: str, row: dict[str, Any]) -> str | None:
        direct = row.get("GEOID")
        if direct:
            return str(direct)

        state = str(row.get("STATE", "")).zfill(2) if row.get("STATE") is not None else ""
        county = str(row.get("COUNTY", "")).zfill(3) if row.get("COUNTY") is not None else ""

        if kind == "state":
            return state or None
        if kind == "county":
            return f"{state}{county}" if state and county else None
        if kind == "tract":
            tract = row.get("TRACT") or row.get("BASENAME")
            if tract:
                tract_value = str(tract).replace(".", "").zfill(6)
                return f"{state}{county}{tract_value}" if state and county else tract_value
            return None
        if kind == "place":
            place = row.get("PLACE") or row.get("PLACEFP")
            if place:
                return f"{state}{str(place).zfill(5)}" if state else str(place).zfill(5)
            return None
        if kind == "zcta":
            zcta = row.get("ZCTA5") or row.get("BASENAME")
            return str(zcta).zfill(5) if zcta else None
        return None
