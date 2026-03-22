from __future__ import annotations

import argparse
import json

from georesolve.providers import NoMatchError, ProviderError
from georesolve.providers.factory import SUPPORTED_PROVIDERS, create_provider
from georesolve.services import Resolver


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="georesolve")
    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve_parser = subparsers.add_parser("resolve", help="Resolve an address into coordinates and geographies")
    resolve_parser.add_argument("address", help="Street address to resolve")
    resolve_parser.add_argument(
        "--provider",
        default="census",
        choices=SUPPORTED_PROVIDERS,
        help="Geocoding and geography provider",
    )
    resolve_parser.add_argument(
        "--benchmark",
        default="Public_AR_Current",
        help="Census benchmark to use when the provider supports it",
    )
    resolve_parser.add_argument(
        "--vintage",
        default="Current_Current",
        help="Census vintage to use when the provider supports it",
    )
    resolve_parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=15.0,
        help="HTTP timeout for provider requests",
    )
    resolve_parser.add_argument("--indent", type=int, default=2, help="JSON indentation level")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "resolve":
        provider = create_provider(
            args.provider,
            benchmark=args.benchmark,
            vintage=args.vintage,
            timeout_seconds=args.timeout_seconds,
        )
        resolver = Resolver(provider)
        try:
            result = resolver.resolve(args.address)
        except NoMatchError as exc:
            parser.exit(2, f"{exc}\n")
        except ProviderError as exc:
            parser.exit(1, f"{exc}\n")

        print(json.dumps(result.to_dict(), indent=args.indent, sort_keys=True))
        return 0

    parser.exit(2, "Unknown command\n")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
