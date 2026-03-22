from __future__ import annotations

from typing import Protocol

from georesolve.models import GeocodedAddress, GeographyMatch


class ProviderError(RuntimeError):
    pass


class NoMatchError(ProviderError):
    pass


class GeocodeProvider(Protocol):
    name: str

    def geocode(self, address: str) -> GeocodedAddress:
        ...


class GeographyProvider(Protocol):
    name: str

    def reverse_geographies(self, latitude: float, longitude: float) -> dict[str, GeographyMatch | None]:
        ...
