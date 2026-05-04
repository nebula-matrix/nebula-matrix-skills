import os
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader


class BaseRenderer:
    """通用 Jinja2 渲染器基类"""

    def __init__(self, template_dir: str):
        self.template_dir = template_dir
        self.env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            loader=FileSystemLoader(template_dir),
        )
        self.env.filters["lalign"] = self._lalign
        self.env.filters["ralign"] = self._ralign

    @staticmethod
    def _lalign(value, length):
        if not isinstance(value, str):
            value = str(value)
        if len(value) >= length:
            return value
        padding = length - len(value)
        return value + " " * padding

    @staticmethod
    def _ralign(value, length):
        if not isinstance(value, str):
            value = str(value)
        if len(value) >= length:
            return value
        padding = length - len(value)
        return " " * padding + value

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self.env.get_template(template_name)
        return template.render(tpl_dict=context, **context)

    def render_to_file(self, template_name: str, context: Dict[str, Any], output_path: str) -> None:
        content = self.render(template_name, context)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
