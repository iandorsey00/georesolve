# georesolve

`georesolve` is a sibling project to `geocompare`.

Its job is narrow and explicit:

- address -> latitude/longitude
- parse direct latitude/longitude input and coordinate-bearing map URLs
- latitude/longitude -> Census-oriented geographies
- return a stable JSON contract that downstream tools can consume

It does not do demographic comparison, ACS querying, or higher-level analytics.

## Recommendation

The best first version is `library-first`, with:

- a small Python package as the core integration surface
- a thin CLI for local workflows and scripts
- an optional FastAPI layer for frontend or remote use later

That keeps local development simple, avoids forcing service deployment too early,
and still leaves a clean path to an API when needed.

## Recommended Architecture

Use a two-stage pipeline with explicit provider boundaries:

1. `address -> lat/lon`
   - implemented through a geocoding provider abstraction
   - first provider: Census Geocoder
   - future providers: Google, Mapbox, Pelias, Geocodio, etc.
2. `lat/lon -> geographies`
   - implemented through a geography lookup abstraction
   - first provider: Census Geocoder geoLookup with explicit geography layers

This gives us a practical first release with one public upstream while keeping
the contract independent of any single provider.

## Why This Direction

- Smallest useful version: one provider can already return tract, county, state,
  and related geography metadata.
- Clean adapter boundary: if you later want rooftop-quality coordinates from a
  commercial geocoder, the output contract does not need to change.
- Good `geocompare` fit: downstream code can consume stable GEOIDs instead of
  provider-specific raw payloads.

## Stack

- Python 3.11+
- stdlib core for the first pass
- optional `FastAPI` + `uvicorn` for API mode
- `unittest` for offline tests
- optional `ruff` for linting

The core package intentionally stays light.

## Output Contract

The canonical result shape is:

```json
{
  "input": {
    "address": "1600 Pennsylvania Ave NW, Washington, DC 20500"
  },
  "matched_address": "1600 PENNSYLVANIA AVE NW, WASHINGTON, DC, 20500",
  "coordinates": {
    "latitude": 38.898754,
    "longitude": -77.036545
  },
  "geographies": {
    "state": {
      "kind": "state",
      "name": "District of Columbia",
      "geoid": "11",
      "summary_level": "040",
      "source_layer": "States"
    },
    "county": {
      "kind": "county",
      "name": "District of Columbia",
      "geoid": "11001",
      "summary_level": "050",
      "source_layer": "Counties"
    },
    "place": {
      "kind": "place",
      "name": "Washington",
      "geoid": "1150000",
      "summary_level": "160",
      "source_layer": "Incorporated Places"
    },
    "zcta": {
      "kind": "zcta",
      "name": "20500",
      "geoid": "20500",
      "summary_level": "860",
      "source_layer": "2020 Census ZIP Code Tabulation Areas"
    },
    "tract": {
      "kind": "tract",
      "name": "001001",
      "geoid": "11001001001",
      "summary_level": "140",
      "source_layer": "Census Tracts"
    }
  },
  "geoids": {
    "state": "11",
    "county": "11001",
    "place": "1150000",
    "zcta": "20500",
    "tract": "11001001001"
  },
  "metadata": {
    "geocoder": "census",
    "geography_source": "census",
    "benchmark": "Public_AR_Current",
    "vintage": "Current_Current"
  }
}
```

`geoids` is the main downstream handoff for future `geocompare` integration.

When resolving current location instead of an address, `input` contains
`coordinates` and `matched_address` is `null`.

## Current Provider Strategy

The scaffold includes a Census-backed provider because it can already support:

- address geocoding
- coordinate geoLookup
- tract/state/county/place lookup
- ZCTA lookup when explicitly requested via layers

Recommended medium-term evolution:

- keep Census as the default geography authority
- optionally add a second geocoding provider for better address precision
- preserve the same result schema regardless of provider choice

## Quick Start

Install in editable mode:

```bash
python3 -m pip install -e .
```

Resolve an address:

```bash
georesolve resolve "4600 Silver Hill Rd, Washington, DC 20233"
```

Resolve a direct lat/lon pair:

```bash
georesolve resolve "38.8899, -77.0091"
```

Resolve a coordinate-bearing Google Maps URL:

```bash
georesolve resolve "https://www.google.com/maps/@38.8899,-77.0091,15z"
```

Resolve caller-supplied current coordinates:

```bash
georesolve resolve-coordinates 38.8899 -77.0091
```

Select provider-facing options explicitly:

```bash
georesolve resolve \
  "4600 Silver Hill Rd, Washington, DC 20233" \
  --provider census \
  --benchmark Public_AR_Current \
  --vintage Current_Current
```

Run the optional API:

```bash
python3 -m pip install -e ".[web]"
georesolve-api
```

Configure the API provider settings with environment variables:

```bash
export GEORESOLVE_PROVIDER=census
export GEORESOLVE_BENCHMARK=Public_AR_Current
export GEORESOLVE_VINTAGE=Current_Current
georesolve-api
```

Resolve through the API with either an address-style query or a coordinate URL:

```bash
curl "http://127.0.0.1:8080/resolve?query=38.8899,-77.0091"
curl "http://127.0.0.1:8080/resolve?query=https://www.google.com/maps/@38.8899,-77.0091,15z"
```

Run live smoke tests against the Census service only when wanted:

```bash
GEORESOLVE_RUN_LIVE_TESTS=1 python3 -m unittest tests.test_live_census_smoke
```

## CLI Notes

- `georesolve resolve` is the main smart entrypoint for addresses, direct
  `lat,lon` input, and supported coordinate-bearing map URLs.
- `georesolve resolve-coordinates` is the preferred explicit coordinate
  command.
- `georesolve resolve-current-location` remains available as a compatibility
  alias.
- Exit codes are stable and automation-friendly:
  - `0` success
  - `1` provider or upstream error
  - `2` usage error
  - `3` no match

## Repository Layout

```text
georesolve/
  interfaces/
  providers/
  services/
  models.py
tests/
```

## Notes

- The current scaffold is designed for U.S.-focused resolution.
- `resolve` accepts an address, a direct `lat,lon` pair, or a supported map URL
  that includes coordinates.
- `resolve-coordinates` is the preferred explicit-coordinate CLI command.
- `resolve-current-location` remains available as a compatibility alias.
- API `/resolve` accepts either `query` or `address`, but rejects requests that
  send both fields at once.
- "Current location" means coordinates supplied by the caller, typically from a
  browser or mobile geolocation API.
- `place` prefers incorporated places and falls back to Census designated
  places.
- ZCTA is treated as an approximate Census geography, not a USPS ZIP guarantee.
