from typing import List, Optional
from gen_reg_tools.core.data_model import Top, Block, Register, Field


class RegDataTraverser:
    """寄存器数据树遍历器"""

    LEVEL_ORDER = ["top", "it", "bt", "reg", "field"]

    @staticmethod
    def walk(
        node,
        level_filter: Optional[List[str]] = None,
        it_filter: Optional[List[str]] = None,
        bt_filter: Optional[List[str]] = None,
        iter_path: Optional[List[str]] = None,
        _visited=None,
    ):
        if iter_path is None:
            iter_path = []
        if _visited is None:
            _visited = set()

        node_id = id(node)
        if node_id in _visited:
            return
        _visited.add(node_id)

        if isinstance(node, Top):
            level = "top"
        elif isinstance(node, Block):
            level = "bt"
        elif isinstance(node, Register):
            level = "reg"
        elif isinstance(node, Field):
            level = "field"
        else:
            level = ""

        if level_filter is None or level in level_filter:
            yield node, iter_path

        if level == "it" and it_filter is not None and getattr(node, "name", "") not in it_filter:
            return

        if level == "bt" and bt_filter is not None and getattr(node, "name", "") not in bt_filter:
            return

        if level_filter is not None:
            depth_ls = [RegDataTraverser.LEVEL_ORDER.index(l) for l in level_filter]
            max_depth = max(depth_ls)
            cur_depth = RegDataTraverser.LEVEL_ORDER.index(level)
            if cur_depth >= max_depth:
                return

        if level == "field":
            return

        current_path = iter_path + [getattr(node, "name", "")]
        for child in getattr(node, "subpart", []):
            yield from RegDataTraverser.walk(
                child, level_filter, it_filter, bt_filter, current_path, _visited
            )

    @staticmethod
    def get_all_bt_names(data) -> List[str]:
        """获取 RegData 中所有 block_type 为 'bt' 的 Block 名称列表"""
        bt_names = []
        for node, _ in RegDataTraverser.walk(data, level_filter=["bt"]):
            if getattr(node, "block_type", "") == "bt":
                bt_names.append(node.name)
        return bt_names

    @staticmethod
    def find_bt(data: Top, bt_name: str) -> Optional[Block]:
        for node, _ in RegDataTraverser.walk(data, level_filter=["bt"]):
            if node.name == bt_name:
                return node
        return None

    @staticmethod
    def filter_by_bt(data: Top, bt_names: List[str]) -> Top:
        filtered_blocks = []
        for block in data.subpart:
            if block.name in bt_names:
                filtered_blocks.append(block)
        return Top(name=data.name, subpart=filtered_blocks)
