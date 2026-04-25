"""Import command: append markdown testpoints to existing json."""

from pathlib import Path

from nbl_testplan_creator.parser.markdown import parse_markdown_document
from nbl_testplan_creator.core.validators import validate_priority, validate_checking

REQUIRED_TP_COLS = ['tp_name', 'stimulus', 'checking', 'priority']


def _next_tp_id(tps: list) -> str:
    if not tps:
        return 't000'
    nums = []
    for tp in tps:
        tid = tp.get('tp_id', '')
        if tid.startswith('t') and tid[1:].isdigit():
            nums.append(int(tid[1:]))
    if not nums:
        return 't000'
    return f't{max(nums) + 1:03d}'


def cmd_import(manager, args) -> int:
    md_file = Path(args.md_file)
    if not md_file.exists():
        print(f"错误: 文件不存在: {md_file}")
        return 1

    text = md_file.read_text(encoding='utf-8')
    doc = parse_markdown_document(text)

    manager.load()

    for fb in doc['features']:
        feature = manager.find_feature_by_name(fb.heading)
        if not feature:
            print(f"跳过未知 Feature: {fb.heading}")
            continue

        for k, v in fb.properties.items():
            if k == 'priority':
                try:
                    feature['priority'] = validate_priority(v)
                except ValueError:
                    pass
            elif k == 'sections_covered':
                feature['sections_covered'] = [s.strip() for s in v.split(',') if s.strip()]
            elif k in ('description', 'feature_name'):
                feature[k] = v

        for sf_block in fb.subfeatures:
            if not sf_block.heading:
                continue
            subfeature = manager.find_subfeature_by_name(feature, sf_block.heading)
            if not subfeature:
                print(f"跳过未知 SubFeature: {fb.heading}/{sf_block.heading}")
                continue

            for k, v in sf_block.properties.items():
                if k == 'priority':
                    try:
                        subfeature['priority'] = validate_priority(v)
                    except ValueError:
                        pass
                elif k in ('description', 'spec_id', 'sub_feature_name'):
                    subfeature[k] = v

            for tbl in sf_block.tables:
                if not tbl.get('rows'):
                    continue
                headers = [h.lower() for h in tbl['headers']]
                for row in tbl['rows']:
                    if 'tp_name' not in headers:
                        continue
                    tp_name = row.get('tp_name', '').strip()
                    if not tp_name:
                        continue
                    skip = False
                    if tp_name.startswith('[SKIP] '):
                        tp_name = tp_name[7:]
                        skip = True

                    tp_id = _next_tp_id(subfeature.get('testpoints', []))
                    tp = {
                        'tp_id': tp_id,
                        'tp_name': tp_name,
                        'source': row.get('source', '').strip(),
                        'stimulus': row.get('stimulus', '').strip(),
                        'checking': validate_checking(row.get('checking', '结果一致性校验（checker）')),
                        'coverage_requirements': row.get('coverage_requirements', '').strip(),
                        'priority': validate_priority(row.get('priority', 'MID')),
                        'category': row.get('category', 'normal').strip(),
                        'path2source': row.get('path2source', '').strip(),
                        'skip': skip,
                    }
                    subfeature['testpoints'].append(tp)

    manager.save()
    stats = manager.get_stats()
    print(f"Import 完成: features={stats['features']}, sub_features={stats['sub_features']}, testpoints={stats['testpoints']}")
    return 0
