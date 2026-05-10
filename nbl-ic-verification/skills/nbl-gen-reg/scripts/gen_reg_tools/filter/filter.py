from __future__ import annotations

import re
from dataclasses import dataclass, field as dc_field
from typing import Callable, List, Optional

from gen_reg_tools.core.data_model import Block, Field, Register, Top


def _parse_range_expr(expr: str) -> Callable[[int], bool]:
    """解析范围表达式，返回判断函数。

    支持的格式：
      - "5"       → 等于 5
      - ">5"      → 大于 5
      - ">=5"     → 大于等于 5
      - "<10"     → 小于 10
      - "<=10"    → 小于等于 10
      - "1-10"    → 1 到 10（含）
    """
    expr = expr.strip()
    if expr.startswith(">="):
        val = int(expr[2:].strip())
        return lambda x: x >= val
    elif expr.startswith("<="):
        val = int(expr[2:].strip())
        return lambda x: x <= val
    elif expr.startswith(">"):
        val = int(expr[1:].strip())
        return lambda x: x > val
    elif expr.startswith("<"):
        val = int(expr[1:].strip())
        return lambda x: x < val
    elif "-" in expr:
        parts = expr.split("-")
        low = int(parts[0].strip())
        high = int(parts[1].strip())
        return lambda x: low <= x <= high
    else:
        val = int(expr.strip())
        return lambda x: x == val


@dataclass
class FilterConditions:
    """封装所有过滤条件"""

    level: str = "register"                      # "register" | "field"
    bt_names: Optional[List[str]] = None           # Block 名称白名单
    rw_attr: Optional[List[str]] = None            # Field rw_attr 白名单
    reg_type: Optional[List[str]] = None           # Register reg_type 白名单
    name_regex: Optional[str] = None               # Register name 正则
    depth_expr: Optional[Callable[[int], bool]] = None   # depth 范围判断
    width_expr: Optional[Callable[[int], bool]] = None   # width 范围判断
    field_regex: Optional[str] = None              # Field name 正则
    default_value: Optional[int] = None            # Field default_value
    wr_ctrl: Optional[List[str]] = None            # Field wr_ctrl 白名单

    def has_register_conditions(self) -> bool:
        return any([
            self.reg_type,
            self.name_regex,
            self.depth_expr,
            self.width_expr,
        ])

    def has_field_conditions(self) -> bool:
        return any([
            self.rw_attr,
            self.field_regex,
            self.default_value is not None,
            self.wr_ctrl,
        ])

    def is_empty(self) -> bool:
        return not any([
            self.bt_names,
            self.has_register_conditions(),
            self.has_field_conditions(),
        ])


def _match_field(f: Field, conds: FilterConditions) -> bool:
    """判断单个 Field 是否满足所有 field 级别条件"""
    if conds.rw_attr and f.rw_attr not in conds.rw_attr:
        return False
    if conds.field_regex and not re.search(conds.field_regex, f.name):
        return False
    if conds.default_value is not None and f.default_value != conds.default_value:
        return False
    if conds.wr_ctrl and (f.wr_ctrl is None or f.wr_ctrl not in conds.wr_ctrl):
        return False
    return True


def _filter_register_level(reg: Register, conds: FilterConditions) -> tuple[bool, list[Field]]:
    """register 级别过滤：判断 register 是否满足条件，返回 (是否匹配, 保留的 fields)"""
    # register 级别条件检查
    if conds.reg_type and reg.reg_type not in conds.reg_type:
        return False, []
    if conds.name_regex and not re.search(conds.name_regex, reg.name):
        return False, []
    if conds.depth_expr and not conds.depth_expr(reg.depth):
        return False, []
    if conds.width_expr and not conds.width_expr(reg.width):
        return False, []

    # field 级别条件检查
    if conds.has_field_conditions():
        matched = [f for f in reg.subpart if _match_field(f, conds)]
        if not matched:
            return False, []
        return True, matched

    # 无 field 条件，保留所有 fields
    return True, list(reg.subpart)


def _filter_field_level(reg: Register, conds: FilterConditions) -> list[Field]:
    """field 级别过滤：返回 register 中满足所有条件的 fields 列表"""
    # 先检查 register 级别条件
    if conds.reg_type and reg.reg_type not in conds.reg_type:
        return []
    if conds.name_regex and not re.search(conds.name_regex, reg.name):
        return []
    if conds.depth_expr and not conds.depth_expr(reg.depth):
        return []
    if conds.width_expr and not conds.width_expr(reg.width):
        return []

    # 再检查 field 级别条件
    matched = [f for f in reg.subpart if _match_field(f, conds)]
    return matched


class RegFilter:
    @staticmethod
    def by_bt(data: Top, bt_names: List[str]) -> Top:
        """按 BT 名称筛选（向后兼容）"""
        filtered_blocks = []
        for block in data.subpart:
            if block.name in bt_names:
                filtered_blocks.append(block)
        return Top(name=data.name, subpart=filtered_blocks)

    @staticmethod
    def by_it(data: Top, it_names: List[str]) -> Top:
        return RegFilter.by_bt(data, it_names)

    @staticmethod
    def filter_data(
        data: Top,
        *,
        level: str = "register",
        bt_names: Optional[List[str]] = None,
        rw_attr: Optional[List[str]] = None,
        reg_type: Optional[List[str]] = None,
        name_regex: Optional[str] = None,
        depth_expr: Optional[str] = None,
        width_expr: Optional[str] = None,
        field_regex: Optional[str] = None,
        default_value: Optional[int] = None,
        wr_ctrl: Optional[List[str]] = None,
    ) -> Top:
        """多维度综合过滤

        所有指定条件之间为"与"逻辑。

        - level="register"：保留满足所有条件的 registers；
          若指定了 field 条件，register 中只保留匹配的 fields。
        - level="field"：保留满足所有条件的 fields；
          register 级别条件作用于 field 的父 register。
        """
        conds = FilterConditions(
            level=level,
            bt_names=bt_names,
            rw_attr=rw_attr,
            reg_type=reg_type,
            name_regex=name_regex,
            depth_expr=_parse_range_expr(depth_expr) if depth_expr else None,
            width_expr=_parse_range_expr(width_expr) if width_expr else None,
            field_regex=field_regex,
            default_value=default_value,
            wr_ctrl=wr_ctrl,
        )

        result_blocks: list[Block] = []

        for blk in data.subpart:
            # BT 白名单过滤
            if conds.bt_names and blk.name not in conds.bt_names:
                continue

            matched_regs: list[Register] = []

            for reg in blk.subpart:
                if level == "register":
                    ok, kept_fields = _filter_register_level(reg, conds)
                    if ok:
                        matched_regs.append(
                            Register(
                                name=reg.name,
                                offset_addr=reg.offset_addr,
                                width=reg.width,
                                depth=reg.depth,
                                reg_type=reg.reg_type,
                                clock_domain=reg.clock_domain,
                                vld_bits=reg.vld_bits,
                                snapshot_en=reg.snapshot_en,
                                subpart=kept_fields,
                            )
                        )
                else:  # level == "field"
                    kept_fields = _filter_field_level(reg, conds)
                    if kept_fields:
                        matched_regs.append(
                            Register(
                                name=reg.name,
                                offset_addr=reg.offset_addr,
                                width=reg.width,
                                depth=reg.depth,
                                reg_type=reg.reg_type,
                                clock_domain=reg.clock_domain,
                                vld_bits=reg.vld_bits,
                                snapshot_en=reg.snapshot_en,
                                subpart=kept_fields,
                            )
                        )

            if matched_regs:
                result_blocks.append(
                    Block(
                        name=blk.name,
                        offset_addr=blk.offset_addr,
                        block_type=blk.block_type,
                        subpart=matched_regs,
                        inst_num=blk.inst_num,
                        baseaddr=blk.baseaddr,
                        size=blk.size,
                    )
                )

        return Top(name=data.name, subpart=result_blocks)
