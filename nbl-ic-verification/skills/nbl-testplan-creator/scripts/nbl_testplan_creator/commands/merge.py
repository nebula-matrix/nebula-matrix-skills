"""Merge command: combine multiple partial markdown files."""

from pathlib import Path
from dataclasses import dataclass, field

from nbl_testplan_creator.parser.markdown import parse_markdown_document
from nbl_testplan_creator.core.name_encoder import encode_name
from nbl_testplan_creator.commands.check import check_markdown, CheckIssue, AI_HINT


@dataclass
class _SubFeatureBlock:
    heading: str
    name: str
    properties: dict
    tables: list


@dataclass
class _FeatureBlock:
    heading: str
    name: str
    properties: dict
    subfeatures: list


def _merge_features(blocks: list[_FeatureBlock]) -> list[_FeatureBlock]:
    merged: dict[str, _FeatureBlock] = {}
    order: list[str] = []
    for block in blocks:
        key = encode_name(block.name)
        if key not in merged:
            merged[key] = _FeatureBlock(
                heading=block.heading,
                name=block.name,
                properties=block.properties.copy(),
                subfeatures=[],
            )
            order.append(key)
        else:
            merged[key].properties.update(block.properties)

        existing_sf = {encode_name(sf.name): sf for sf in merged[key].subfeatures}
        for sf in block.subfeatures:
            sf_key = encode_name(sf.name)
            if sf_key not in existing_sf:
                existing_sf[sf_key] = sf
                merged[key].subfeatures.append(sf)
            else:
                existing_sf[sf_key].properties.update(sf.properties)
                existing_sf[sf_key].tables.extend(sf.tables)

    return [merged[k] for k in order]


def cmd_merge(_manager, args) -> int:
    output = Path(args.output)
    all_features: list[_FeatureBlock] = []
    doc_title = None
    metadata = None

    # Pre-check all partials
    for ppath in args.partials:
        path = Path(ppath)
        if not path.exists():
            continue
        errors, warnings = check_markdown(path)
        if errors:
            print(f"❌ {path.name} 格式检查未通过，发现 {len(errors)} 个错误，合并已中止:")
            for e in errors:
                print(f"  [ERROR] 第 {e.line} 行 | {e.error_type}")
                if e.content:
                    print(f"    内容: {e.content}")
                print(f"    问题: {e.message}")
                if e.hint:
                    print(f"    修复建议: {e.hint}")
                print()
            print("请先修复上述格式问题后再执行 merge 命令。")
            print(f"AI 提示: {AI_HINT}")
            return 1

    for ppath in args.partials:
        path = Path(ppath)
        if not path.exists():
            print(f"跳过不存在的文件: {path}")
            continue
        text = path.read_text(encoding='utf-8')
        doc = parse_markdown_document(text)

        if doc_title is None and doc['title']:
            doc_title = doc['title']
        if metadata is None and doc['metadata']:
            metadata = doc['metadata']

        for fb in doc['features']:
            all_features.append(_FeatureBlock(
                heading=fb.heading,
                name=fb.heading,
                properties=fb.properties,
                subfeatures=[
                    _SubFeatureBlock(
                        heading=sf.heading,
                        name=sf.heading,
                        properties=sf.properties,
                        tables=sf.tables,
                    )
                    for sf in fb.subfeatures
                ],
            ))

    if not all_features:
        print("错误: 没有任何 Feature 块")
        return 1

    merged = _merge_features(all_features)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, 'w', encoding='utf-8') as f:
        if doc_title:
            f.write(f"# {doc_title}\n\n")
        if metadata:
            f.write(f"{metadata}\n\n")
        for i, block in enumerate(merged):
            f.write(f"## {block.heading}\n\n")
            for k, v in sorted(block.properties.items()):
                f.write(f"- {k}: {v}\n")
            f.write("\n")
            for sf in block.subfeatures:
                f.write(f"### {sf.heading}\n\n")
                for k, v in sorted(sf.properties.items()):
                    f.write(f"- {k}: {v}\n")
                f.write("\n")
                for tbl in sf.tables:
                    headers = tbl['headers']
                    f.write("| " + " | ".join(headers) + " |\n")
                    f.write("|" + "|".join(" --- " for _ in headers) + "|\n")
                    for row in tbl['rows']:
                        cells = [str(row.get(h, '')) for h in headers]
                        f.write("| " + " | ".join(cells) + " |\n")
                    f.write("\n")
            if i < len(merged) - 1:
                f.write("\n")

    print(f"合并完成: {output}")
    return 0
