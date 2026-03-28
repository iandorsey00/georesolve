# georesolve Handoff

## Snapshot

- Project: `georesolve`
- Handoff date: 2026-03-28
- Version: `0.3.0`

## Decisions Made

- Product direction: `library-first` with optional API
- Default geography authority: U.S. Census geocoder/geoLookup
- Scope boundary:
  - `georesolve`: address resolution and geography assignment
  - `geocompare`: querying, analytics, comparisons, and data products

## Current Scaffold

- Python package with typed models
- CLI entrypoint: `georesolve resolve "<address-or-latlon-or-url>"`
- Current-location CLI entrypoint: `georesolve resolve-current-location <lat> <lon>`
- Optional API entrypoint: `georesolve-api`
- Census-backed provider abstraction
- Provider/config factory for benchmark and vintage selection
- Offline unit tests for normalization and resolver orchestration
- Opt-in live Census smoke test coverage

## Contract Priority

The main downstream contract is the stable JSON response plus flat `geoids`:

- `state`
- `county`
- `place`
- `zcta`
- `tract`

Those IDs are the intended handoff surface for later `geocompare` integration.

The repo also supports coordinate-driven resolution for browser or device
geolocation flows.

The main `resolve` path now also accepts direct lat/lon strings and
coordinate-bearing map URLs such as Google Maps URLs that contain embedded
coordinates.

API input handling now rejects ambiguous requests that send both `query` and
`address`, and URL parsing is limited to `http`/`https` inputs.

## Recommended Next Steps

1. Exercise the live Census provider against real addresses.
2. Decide whether rooftop-quality coordinates are needed for the frontend path.
3. If yes, add a second geocoding provider while keeping Census as the
   geography lookup authority.
4. Add request logging, retries, and rate-limit-aware error handling before
   production API use.
