"""Unified markdown generator from features.json."""

from datetime import datetime

from nbl_testplan_creator.parser.table import render_table

FULL_TABLE_COLUMNS = [
    'tp_name', 'source', 'stimulus', 'checking',
    'coverage_requirements', 'priority', 'category', 'path2source',
]

SIMPLE_TABLE_COLUMNS = [
    'tp_name', 'source', 'stimulus', 'checking',
    'coverage_requirements', 'priority', 'category',
]


def generate_markdown(data: dict, *, full: bool = True, numbered: bool = True) -> str:
    """
    Generate markdown tree from features.json data.

    Args:
        data: The loaded features.json dict.
        full: If True, include path2source column; if False, skip it.
        numbered: If True, add sequence numbers to headings.
    """
    lines = []
    doc_title = data.get('metadata', {}).get('document_title', 'IC模块验证测试计划')
    lines.append(f"# {doc_title}")
    lines.append("")

    # Stats as metadata list under title, not as ## heading
    stats = _collect_stats(data)
    lines.append(f"- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(
        f"- 总Feature数: {stats['features']} | "
        f"总Sub-Feature数: {stats['sub_features']} | "
        f"总测试点数: {stats['testpoints']}"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    headers = FULL_TABLE_COLUMNS if full else SIMPLE_TABLE_COLUMNS
    features = data.get('features', [])

    for fi, feature in enumerate(features, 1):
        f_name = feature.get('feature_name', '')
        f_heading = f"{fi}. {f_name}" if numbered else f_name
        f_skip = " [SKIPPED]" if feature.get('skip') else ""
        lines.append(f"## {f_heading}{f_skip}")
        lines.append("")

        desc = feature.get('description', '')
        if desc:
            lines.append(f"- description: {desc}")
        pri = feature.get('priority', 'MID')
        lines.append(f"- priority: {pri}")
        secs = feature.get('sections_covered', [])
        if secs:
            lines.append(f"- sections_covered: {', '.join(secs)}")
        lines.append("")

        subfeatures = feature.get('sub_features', [])
        for sfi, sf in enumerate(subfeatures, 1):
            sf_name = sf.get('sub_feature_name', '')
            sf_heading = f"{fi}.{sfi}. {sf_name}" if numbered else sf_name
            sf_skip = " [SKIPPED]" if sf.get('skip') else ""
            lines.append(f"### {sf_heading}{sf_skip}")
            lines.append("")

            sf_desc = sf.get('description', '')
            if sf_desc:
                lines.append(f"- description: {sf_desc}")
            sf_spec = sf.get('spec_id', '')
            if sf_spec:
                lines.append(f"- spec_id: {sf_spec}")
            sf_pri = sf.get('priority', 'MID')
            lines.append(f"- priority: {sf_pri}")
            lines.append("")

            tps = sf.get('testpoints', [])
            if tps:
                rows = []
                for tp in tps:
                    row = {k: tp.get(k, '') for k in headers}
                    if tp.get('skip'):
                        row['tp_name'] = f"[SKIP] {row['tp_name']}"
                    rows.append(row)
                lines.extend(render_table(headers, rows))
                lines.append("")

    while lines and lines[-1] == '':
        lines.pop()

    return '\n'.join(lines) + '\n'


def _collect_stats(data: dict) -> dict:
    features = data.get('features', [])
    sf_count = sum(len(f.get('sub_features', [])) for f in features)
    tp_count = sum(
        sum(len(sf.get('testpoints', [])) for sf in f.get('sub_features', []))
        for f in features
    )
    return {'features': len(features), 'sub_features': sf_count, 'testpoints': tp_count}
