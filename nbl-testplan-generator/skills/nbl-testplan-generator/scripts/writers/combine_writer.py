"""combine_writer.py -- Ch2 register filtering, grouping, cross-reference, and CLI."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


CH2_EXCLUDE_PATTERNS: list[str] = [
    r".*_int_status$",
    r".*_int_mask$",
    r".*_int_set$",
    r".*_car_ctrl$",
    r".*_fifo_th$",
    r".*_spare\d*$",
    r".*_cnt$",
    r".*_fifo_full$",
    r".*_fifo_empty$",
    r".*_fifo_overflow$",
    r".*_fifo_underflow$",
    r".*_fsm\d*$",
    r".*_err_info$",
    r".*_bp_state$",
    r".*_bp_history$",
    r".*_test$",
    r".*_init_done$",
    r".*_init_start$",
]

_CH2_EXCLUDE_COMPILED = [re.compile(p) for p in CH2_EXCLUDE_PATTERNS]


def _is_excluded_register(reg_name: str) -> bool:
    for pat in _CH2_EXCLUDE_COMPILED:
        if pat.match(reg_name):
            return True
    return False


def filter_ch2_registers(registers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in registers if not _is_excluded_register(r["name"])]


def group_similar_registers(
    registers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Group registers that differ only by a trailing numeric suffix.

    E.g. upa_fwd_type_stage_0, upa_fwd_type_stage_1, upa_fwd_type_stage_2
    are merged into upa_fwd_type_stage_0/1/2.
    """
    groups: dict[str, list[dict[str, Any]]] = {}
    order: list[str] = []

    for reg in registers:
        name = reg["name"]
        m = re.match(r"^(.+?)_(\d+)$", name)
        if m:
            base = m.group(1)
        else:
            base = name

        if base not in groups:
            groups[base] = []
            order.append(base)
        groups[base].append(reg)

    result: list[dict[str, Any]] = []
    for base in order:
        members = groups[base]
        if len(members) == 1:
            result.append(members[0])
        else:
            suffixes = []
            for m_reg in members:
                m_match = re.match(r"^.+?_(\d+)$", m_reg["name"])
                suffixes.append(m_match.group(1) if m_match else "")
            merged_name = f"{base}_{'/'.join(suffixes)}"

            all_fields: list[dict[str, Any]] = []
            seen: set[str] = set()
            for m_reg in members:
                for field in m_reg.get("fields", []):
                    key = field.get("name", "")
                    if key and key not in seen:
                        seen.add(key)
                        all_fields.append(field)

            result.append({
                "name": merged_name,
                "offset": members[0].get("offset", ""),
                "fields": all_fields,
                "description": members[0].get("description", ""),
            })

    return result


def _extract_covered_regs_from_ch1(ch1_data: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Build a map of register_name -> {feature_id, stimulus, checking, coverage, path}."""
    covered: dict[str, dict[str, str]] = {}
    for feat in ch1_data.get("features", []):
        fid = feat.get("feature_id", "")
        for sf1 in feat.get("subfeatures_l1", []):
            for sf2 in sf1.get("subfeatures_l2", []):
                stimulus = sf2.get("stimulus", "")
                checking = sf2.get("checking", "")
                coverage = sf2.get("coverage", "")
                path = sf2.get("path", "")
                for reg_name in re.findall(r"(upa_\w+)", stimulus + " " + coverage):
                    if reg_name not in covered:
                        covered[reg_name] = {
                            "feature_id": fid,
                            "stimulus": stimulus,
                            "checking": checking,
                            "coverage": coverage,
                            "path": path,
                        }
    return covered


def cross_ref_ch2(
    ch2_regs: list[dict[str, Any]],
    ch1_data: dict[str, Any],
) -> list[dict[str, Any]]:
    """Cross-reference Ch2 registers with Ch1 features."""
    covered_map = _extract_covered_regs_from_ch1(ch1_data)
    result: list[dict[str, Any]] = []

    for reg in ch2_regs:
        reg_name = reg["name"]
        fields = reg.get("fields", [])

        covered_info = covered_map.get(reg_name)
        if not covered_info:
            base_match = re.match(r"^(.+?)_\d+(/\d+)*$", reg_name)
            if base_match:
                base = base_match.group(1)
                for key in covered_map:
                    if key == base or re.match(r"^" + re.escape(base) + r"_\d+$", key):
                        covered_info = covered_map[key]
                        break

        if covered_info:
            fid = covered_info["feature_id"]
            desc_parts = []
            for field in fields:
                fname = field.get("name", "")
                fdesc = field.get("description", "")
                if fname and fname != "rsv" and fdesc:
                    desc_parts.append(f"{fname}: {fdesc}")

            remarks = "; ".join(desc_parts) if desc_parts else ""
            remarks += f" 【已在功能特性 [{fid}] 中覆盖】"

            result.append({
                "name": reg_name,
                "skip": True,
                "remarks": remarks.strip(),
                "stimulus": covered_info.get("stimulus", ""),
                "checking": covered_info.get("checking", ""),
                "coverage": covered_info.get("coverage", ""),
                "path": covered_info.get("path", ""),
            })
        else:
            desc_parts = []
            config_parts = []
            for field in fields:
                fname = field.get("name", "")
                fdesc = field.get("description", "")
                frange = field.get("range", "")
                faccess = field.get("access", "")
                if fname and fname != "rsv":
                    desc_parts.append(f"{frange} {fname}: {fdesc}")
                    if faccess in ("RW", "RWW"):
                        config_parts.append(f"配置 {reg_name}.{fname} ({frange})")

            stimulus = "【配置】" + "；".join(config_parts) if config_parts else ""

            result.append({
                "name": reg_name,
                "skip": False,
                "remarks": "; ".join(desc_parts) if desc_parts else "",
                "stimulus": stimulus,
                "checking": "",
                "coverage": "",
                "path": "",
            })

    return result


def build_ch2_data(
    ch2_regs: list[dict[str, Any]],
    ch1_data: dict[str, Any],
) -> dict[str, Any]:
    """Build the full Ch2 data dict expected by xlsx_writer."""
    filtered = filter_ch2_registers(ch2_regs)
    grouped = group_similar_registers(filtered)
    xrefed = cross_ref_ch2(grouped, ch1_data)

    registers: list[dict[str, Any]] = []
    for reg_info in xrefed:
        reg_name = reg_info["name"]
        is_skip = reg_info.get("skip", False)

        subfeatures_l2: list[dict[str, Any]] = [{
            "subfeature_l2_overview": "",  # F-column: empty for Ch2
            "subfeature_l2_detail": "",
            "remarks": reg_info.get("remarks", ""),
            "stimulus": reg_info.get("stimulus", ""),
            "checking": reg_info.get("checking", ""),
            "coverage": reg_info.get("coverage", ""),
            "priority": "HIGH" if not is_skip else "",
            "activity": "BT",
            "path": reg_info.get("path", "") or "【反标路径暂无法确定】",
            "skip": is_skip,
        }]

        registers.append({
            "register_name": reg_name,
            "subfeatures_l1": [{
                "subfeature_l1": reg_name,
                "subfeatures_l2": subfeatures_l2,
            }],
        })

    return {
        "chapter": "chapter 2 配置特性",
        "registers": registers,
    }


def _sanitize_path_name(text: str) -> str:
    """Convert text to a valid snake_case path component."""
    s = re.sub(r"[^a-zA-Z0-9_]", "_", text)
    s = re.sub(r"_+", "_", s).strip("_")
    return s.lower()


def validate_jw_correspondence(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and auto-correct J-column (checking) to W-column (path) correspondence.

    Rules:
    - checking=by_direct_tc + empty path -> auto-generate direct_fcov path
    - checking=by_assertion + empty path -> auto-generate assert path
    - checking=by_checker -> leave path unchanged

    Returns the modified data dict.
    """
    module = data.get("module_name", "xxx").lower()
    counter: dict[str, int] = {}

    for feat in data.get("features", []):
        overview = feat.get("feature", "")
        slug = _sanitize_path_name(overview)
        for sf1 in feat.get("subfeatures_l1", []):
            for idx, sf2 in enumerate(sf1.get("subfeatures_l2", [])):
                checking = sf2.get("checking", "")
                path = sf2.get("path", "")

                if checking == "by_direct_tc" and (not path or "【反标路径暂无法确定】" in path):
                    key = f"direct_{slug}"
                    counter[key] = counter.get(key, 0) + 1
                    sf2["path"] = f"Group:$unit::{module}_direct_fcov::cp_direct_{slug}_{counter[key]}"

                elif checking == "by_assertion" and (not path or "【反标路径暂无法确定】" in path):
                    key = f"assert_{slug}"
                    counter[key] = counter.get(key, 0) + 1
                    sf2["path"] = f"Group:$unit::{module}_assert::{slug}_{counter[key]}_c"

    return data


def combine_and_write(
    ch1_path: str,
    reg_path: str,
    output_path: str,
    template_path: str,
) -> dict[str, int]:
    """Main pipeline: load JSON inputs, process Ch2, write xlsx."""
    from .xlsx_writer import write_testpoint_xlsx

    with open(ch1_path, "r", encoding="utf-8") as f:
        ch1_data = json.load(f)

    with open(reg_path, "r", encoding="utf-8") as f:
        reg_data = json.load(f)

    registers = []
    for sheet_data in reg_data.get("sheets", {}).values():
        registers.extend(sheet_data.get("registers", []))

    ch2_data = build_ch2_data(registers, ch1_data)

    chapters = [
        {"type": "ch1", "data": ch1_data},
        {"type": "ch2", "data": ch2_data},
    ]
    return write_testpoint_xlsx(chapters, output_path, template_path)


def orchestrate_testplan(
    spec_path: str,
    reg_path: str,
    output_path: str,
    template_path: str,
    workdir: str | None = None,
) -> dict[str, Any]:
    """Orchestrate full testplan generation: parse docs, generate Ch1, Ch2, combine.

    This is the main entry point for the nbl-testplan-generator skill.

    Parameters
    ----------
    spec_path : str
        Path to functional specification (.md, after docx conversion).
    reg_path : str
        Path to register configuration .xlsx.
    output_path : str
        Destination xlsx file path.
    template_path : str
        Path to the template xlsx.
    workdir : str | None
        Working directory for intermediate files.

    Returns
    -------
    dict[str, Any]
        Statistics and output paths.
    """
    from pathlib import Path
    import json

    workdir = workdir or str(Path(output_path).parent / ".tp_cache")
    Path(workdir).mkdir(parents=True, exist_ok=True)

    # Parse documents
    import sys
    scripts_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(scripts_dir))

    from parsers.md_parser import parse_markdown
    from parsers.reg_parser import parse_xlsx as parse_register_xlsx

    # Parse spec
    spec_data = parse_markdown(spec_path)
    spec_json = str(Path(workdir) / "spec_parsed.json")
    with open(spec_json, "w", encoding="utf-8") as f:
        json.dump(spec_data, f, ensure_ascii=False, indent=2)

    # Parse registers
    reg_data = parse_register_xlsx(reg_path)
    reg_json = str(Path(workdir) / "reg_parsed.json")
    with open(reg_json, "w", encoding="utf-8") as f:
        json.dump(reg_data, f, ensure_ascii=False, indent=2)

    # Generate Ch1 features (placeholder - LLM does this)
    ch1_json = str(Path(workdir) / "ch1_features.json")
    ch1_data = {
        "module_name": spec_data.get("document_title", "UNKNOWN"),
        "spec_name": Path(spec_path).stem,
        "chapter": "chapter 1 功能特性",
        "features": [],
    }
    with open(ch1_json, "w", encoding="utf-8") as f:
        json.dump(ch1_data, f, ensure_ascii=False, indent=2)

    # Combine Ch1 + Ch2
    stats = combine_and_write(ch1_json, reg_json, output_path, template_path)

    return {
        "stats": stats,
        "output_path": output_path,
        "workdir": workdir,
        "spec_json": spec_json,
        "reg_json": reg_json,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Combine Ch1+Ch2 and write testplan xlsx",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Combine existing JSON files
  python combine_writer.py --ch1 ch1.json --reg reg.json --output testplan.xlsx --template template.xlsx

  # Orchestrate full generation (parse + combine)
  python combine_writer.py --spec spec.md --reg manual.xlsx --output testplan.xlsx --template template.xlsx
        """,
    )
    parser.add_argument("--ch1", help="Path to Ch1 features JSON")
    parser.add_argument("--reg", required=True, help="Path to parsed register JSON")
    parser.add_argument("--output", required=True, help="Output xlsx path")
    parser.add_argument("--template", required=True, help="Template xlsx path")
    parser.add_argument("--spec", help="Path to spec markdown (for orchestration)")
    parser.add_argument("--workdir", help="Working directory for intermediate files")
    args = parser.parse_args()

    if args.spec:
        # Orchestration mode
        result = orchestrate_testplan(
            args.spec,
            args.reg,
            args.output,
            args.template,
            args.workdir,
        )
        print(f"Orchestration complete: {result}")
    elif args.ch1:
        # Combine mode
        stats = combine_and_write(args.ch1, args.reg, args.output, args.template)
        print(f"Done: {stats}")
    else:
        parser.error("Either --spec (orchestration) or --ch1 (combine) is required")
