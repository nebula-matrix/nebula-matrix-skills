#!/usr/bin/env python3
"""reg_to_json.py - CLI to convert register xlsx to JSON."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from parsers.reg_parser import parse_register_xlsx


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Convert register xlsx to JSON")
    parser.add_argument("input", help="Input xlsx file path")
    parser.add_argument("-o", "--output", help="Output JSON file path")
    parser.add_argument("-m", "--module", help="Module name override")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        return 1

    result = parse_register_xlsx(input_path)

    if args.module:
        result["module_name"] = args.module

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Written: {output_path}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
