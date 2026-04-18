"""func_writer.py - Write functional features to xlsx.

Uses xlsx_writer for formatting, provides simplified CLI for Ch1-only output.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add skill scripts directory to path for imports
_skill_scripts = Path(__file__).parent.parent / "skills" / "nbl-testplan-generator" / "scripts"
if str(_skill_scripts) not in sys.path:
    sys.path.insert(0, str(_skill_scripts))
from writers.xlsx_writer import write_testpoint_xlsx


def write_func_xlsx(
    func_data: dict[str, Any],
    output_path: str,
    template_path: str,
) -> dict[str, int]:
    """Write Ch1 functional features to xlsx.

    Parameters
    ----------
    func_data : dict
        Ch1 features JSON data with module_name, spec_name, features.
    output_path : str
        Destination xlsx file path.
    template_path : str
        Path to the template xlsx.

    Returns
    -------
    dict[str, int]
        Stats: total_features, total_l1, total_l2, skipped_regs
    """
    chapters = [{"type": "ch1", "data": func_data}]
    return write_testpoint_xlsx(chapters, output_path, template_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Write functional features to xlsx")
    parser.add_argument("--func", required=True, help="Path to Ch1 features JSON")
    parser.add_argument("--output", required=True, help="Output xlsx path")
    parser.add_argument("--template", required=True, help="Template xlsx path")
    args = parser.parse_args()

    with open(args.func, "r", encoding="utf-8") as f:
        func_data = json.load(f)

    stats = write_func_xlsx(func_data, args.output, args.template)
    print(f"Done: {stats}")
