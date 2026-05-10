"""Extractor Adapter: converts RegData (Block/Top) to legacy dict-list format."""

from typing import List, Dict, Any
from gen_reg_tools.core.data_model import Block, Register, Field, Top


def _infer_tbl_rw_attr(reg: Register) -> str:
    """Infer tbl_rw_attr from register fields (rw if any non-rsv field is rw)."""
    if reg.reg_type != "tbl":
        return "rw"
    for fld in reg.subpart:
        if fld.name != "rsv" and fld.rw_attr == "rw":
            return "rw"
    return "ro"


def register_to_dict(reg: Register) -> Dict[str, Any]:
    """Convert a single Register dataclass to the legacy dict format."""
    tbl_rw_attr = _infer_tbl_rw_attr(reg)
    vld_bits = reg.vld_bits if reg.vld_bits is not None else reg.width

    subpart: List[Dict[str, Any]] = []
    for fld in reg.subpart:
        field_dict: Dict[str, Any] = {
            "field": fld.name,
            "bits": fld.bits,
            "lsb": fld.lsb,
            "rw_attr": fld.rw_attr,
            "default_value": fld.default_value,
            "wr_ctrl": fld.wr_ctrl,
            "snapshot_en": reg.snapshot_en,
            "have_wr_ctrl": "y" if fld.wr_ctrl == "y" else None,
        }
        subpart.append(field_dict)

    return {
        "name": reg.name,
        "type": reg.reg_type,
        "offset_addr": reg.offset_addr,
        "width": reg.width,
        "depth": reg.depth,
        "clock_domain": reg.clock_domain,
        "vld_bits": vld_bits,
        "snapshot_en": reg.snapshot_en,
        "tbl_rw_attr": tbl_rw_attr,
        "subpart": subpart,
    }


def block_to_dict_list(block: Block) -> List[Dict[str, Any]]:
    """Convert a Block to a flat list of register dicts (legacy all_data_ls format)."""
    return [register_to_dict(reg) for reg in block.subpart]


def block_to_domain_dict_lists(block: Block) -> List[List[Dict[str, Any]]]:
    """Split block registers by clock domain for multi-clock processing."""
    all_data = block_to_dict_list(block)
    # Collect unique clock domains in order of first appearance
    domains: List[str] = []
    seen_domains = set()
    for reg_dict in all_data:
        cd = reg_dict.get("clock_domain", "")
        if cd and cd not in seen_domains:
            seen_domains.add(cd)
            domains.append(cd)
    if not domains:
        return [all_data]
    return [
        [reg_dict for reg_dict in all_data if reg_dict.get("clock_domain") == cd]
        for cd in domains
    ]


def top_to_dict_list(top: Top, bt_name: str = "") -> List[Dict[str, Any]]:
    """Convert a Top to a flat list of register dicts, optionally filtering by block name."""
    result: List[Dict[str, Any]] = []
    for block in top.subpart:
        if bt_name and block.name != bt_name:
            continue
        result.extend(block_to_dict_list(block))
    return result
