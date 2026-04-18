"""Command-line interface for ClearHealth.

Usage:
    clearhealth analyse document.txt
    clearhealth analyse document.txt --format json
    clearhealth analyse document.txt --format summary
    cat document.txt | clearhealth analyse -
    echo "Patient has hypertension" | clearhealth analyse -
"""

from __future__ import annotations

import argparse
import json
import sys

from clearhealth.analyzer import ClearHealthAnalyzer


def main(argv: list[str] | None = None) -> int:
    """Entry point for the clearhealth CLI."""
    parser = argparse.ArgumentParser(
        prog="clearhealth",
        description="Analyse health and education documents for accessibility.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # analyse command
    analyse_parser = subparsers.add_parser(
        "analyse",
        aliases=["analyze"],
        help="Analyse a document for accessibility.",
    )
    analyse_parser.add_argument(
        "file",
        help="Path to the text file to analyse, or '-' to read from stdin.",
    )
    analyse_parser.add_argument(
        "--format",
        choices=["summary", "json"],
        default="summary",
        help="Output format (default: summary).",
    )
    analyse_parser.add_argument(
        "--threshold",
        type=float,
        default=12.0,
        help="Grade level above which a sentence is flagged as complex (default: 12.0).",
    )

    # version command
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit.",
    )

    args = parser.parse_args(argv)

    if args.version:
        from clearhealth import __version__
        print(f"clearhealth {__version__}")
        return 0

    if not args.command:
        parser.print_help()
        return 0

    # Read input
    if args.file == "-":
        text = sys.stdin.read()
    else:
        try:
            with open(args.file, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 1
        except OSError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 1

    if not text.strip():
        print("Error: Input is empty.", file=sys.stderr)
        return 1

    # Run analysis
    analyzer = ClearHealthAnalyzer(complex_sentence_threshold=args.threshold)
    report = analyzer.analyse(text)

    # Output
    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.summary())

    return 0


if __name__ == "__main__":
    sys.exit(main())
