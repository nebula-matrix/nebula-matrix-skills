from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json


@dataclass
class Field:
    name: str
    bits: int
    lsb: int
    rw_attr: str
    default_value: int = 0
    wr_ctrl: Optional[str] = None
    fcov: Optional[str] = None


@dataclass
class Register:
    name: str
    offset_addr: int
    width: int
    depth: int
    reg_type: str
    clock_domain: str = ""
    vld_bits: Optional[int] = None
    snapshot_en: str = "na"
    subpart: List[Field] = field(default_factory=list)


@dataclass
class Block:
    name: str
    offset_addr: Optional[int] = None
    block_type: str = "bt"
    subpart: List[Register] = field(default_factory=list)
    inst_num: int = 1
    baseaddr: int = 0
    size: Optional[int] = None


@dataclass
class Top:
    name: str = "TOP"
    top_type: str = "top"
    level: str = "top"
    subpart: List[Block] = field(default_factory=list)

    def to_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=4)

    @classmethod
    def from_json(cls, path: str) -> "Top":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> "Top":
        blocks = []
        for block_data in data.get("subpart", []):
            registers = []
            for reg_data in block_data.get("subpart", []):
                fields = []
                for field_data in reg_data.get("subpart", []):
                    fields.append(Field(**field_data))
                reg_kwargs = {k: v for k, v in reg_data.items() if k != "subpart"}
                reg_kwargs["subpart"] = fields
                registers.append(Register(**reg_kwargs))
            block_kwargs = {k: v for k, v in block_data.items() if k != "subpart"}
            block_kwargs["subpart"] = registers
            blocks.append(Block(**block_kwargs))
        top_kwargs = {k: v for k, v in data.items() if k != "subpart"}
        top_kwargs["subpart"] = blocks
        return cls(**top_kwargs)


RegData = Top
