"""Extractor Adapter: converts RegData (Top dataclass) to legacy dict format for RAL processors."""

from typing import Any, Dict, List
from gen_reg_tools.core.data_model import Block, Register, Field, Top


def _infer_tbl_rw_attr(reg: Register) -> str:
    """Infer tbl_rw_attr from register fields (rw if any non-rsv field is rw)."""
    if reg.reg_type != "tbl":
        return "rw"
    for fld in reg.subpart:
        if fld.name != "rsv" and fld.rw_attr == "rw":
            return "rw"
    return "ro"


def field_to_dict(field: Field) -> Dict[str, Any]:
    """Convert a Field dataclass to legacy field dict."""
    result: Dict[str, Any] = {
        "field": field.name,
        "name": field.name,
        "bits": field.bits,
        "lsb": field.lsb,
        "rw_attr": field.rw_attr,
        "default_value": field.default_value,
        "wr_ctrl": field.wr_ctrl,
        "type": "field",
        "level": "field",
    }
    if field.fcov is not None:
        result["fcov"] = field.fcov
    return result


def register_to_dict(reg: Register) -> Dict[str, Any]:
    """Convert a Register dataclass to legacy register dict."""
    vld_bits = reg.vld_bits if reg.vld_bits is not None else reg.width
    subpart: List[Dict[str, Any]] = [field_to_dict(f) for f in reg.subpart]

    result: Dict[str, Any] = {
        "name": reg.name,
        "type": reg.reg_type,
        "level": "reg",
        "offset_addr": reg.offset_addr,
        "width": reg.width,
        "depth": reg.depth,
        "clock_domain": reg.clock_domain,
        "vld_bits": vld_bits,
        "snapshot_en": reg.snapshot_en,
        "tbl_rw_attr": _infer_tbl_rw_attr(reg),
        "subpart": subpart,
    }
    return result


def block_to_dict(block: Block) -> Dict[str, Any]:
    """Convert a Block dataclass to legacy block dict."""
    subpart: List[Dict[str, Any]] = [register_to_dict(r) for r in block.subpart]
    return {
        "name": block.name,
        "type": block.block_type,
        "level": "bt",
        "offset_addr": block.offset_addr,
        "inst_num": block.inst_num,
        "baseaddr": block.baseaddr,
        "size": block.size,
        "subpart": subpart,
    }


def top_to_dict(top: Top) -> Dict[str, Any]:
    """Convert a Top dataclass to legacy all_data_dict format."""
    return {
        "top_name": top.name,
        "level": "top",
        "subpart": [block_to_dict(b) for b in top.subpart],
    }
