"""Build command: markdown -> json."""

from pathlib import Path

from nbl_testplan_creator.parser.markdown import parse_markdown_document
from nbl_testplan_creator.core.validators import validate_priority
from nbl_testplan_creator.core.name_encoder import encode_name
from nbl_testplan_creator.commands.check import check_markdown, CheckIssue, AI_HINT

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


def _print_check_errors(md_file: Path, errors: list[CheckIssue]) -> None:
    print(f"❌ {md_file.name} 格式检查未通过，发现 {len(errors)} 个错误:")
    for e in errors:
        print(f"  [ERROR] 第 {e.line} 行 | {e.error_type}")
        if e.content:
            print(f"    内容: {e.content}")
        print(f"    问题: {e.message}")
        if e.hint:
            print(f"    修复建议: {e.hint}")
        print()
    print("请先修复上述格式问题后再执行 build/merge 命令。")
    print(f"AI 提示: {AI_HINT}")


def cmd_build(manager, args) -> int:
    md_file = Path(args.md_file)
    if not md_file.exists():
        print(f"错误: 文件不存在: {md_file}")
        return 1

    errors, warnings = check_markdown(md_file)
    if errors:
        _print_check_errors(md_file, errors)
        if warnings:
            print(f"（还有 {len(warnings)} 个警告可忽略）")
        return 1

    text = md_file.read_text(encoding='utf-8')
    doc = parse_markdown_document(text)

    if doc['title']:
        manager.data['document_title'] = doc['title']

    features = []

    for fb in doc['features']:
        feature_name = fb.heading
        fid = encode_name(feature_name)[:8]
        if not any(c.isalpha() for c in fid):
            fid = 'f' + fid

        existing = next((f for f in features if f['feature_id'] == fid), None)
        if existing:
            feature = existing
        else:
            feature = {
                'feature_id': fid,
                'feature_name': feature_name,
                'description': fb.properties.get('description', ''),
                'priority': 'MID',
                'sections_covered': [],
                'skip': False,
                'sub_features': [],
            }
            pri = fb.properties.get('priority')
            if pri:
                try:
                    feature['priority'] = validate_priority(pri)
                except ValueError:
                    pass

            secs = fb.properties.get('sections_covered', '')
            if secs:
                feature['sections_covered'] = [s.strip() for s in secs.split(',') if s.strip()]
            features.append(feature)

        for sf_block in fb.subfeatures:
            sf_name = sf_block.heading or 'default'
            sfid = encode_name(sf_name)[:8]
            if not any(c.isalpha() for c in sfid):
                sfid = 's' + sfid

            sf = next((s for s in feature['sub_features'] if s['sub_feature_id'] == sfid), None)
            if not sf and sfid and sf_name:
                sf = {
                    'sub_feature_id': sfid,
                    'sub_feature_name': sf_name,
                    'description': sf_block.properties.get('description', ''),
                    'spec_id': sf_block.properties.get('spec_id', ''),
                    'priority': 'MID',
                    'skip': False,
                    'testpoints': [],
                }
                pri = sf_block.properties.get('priority')
                if pri:
                    try:
                        sf['priority'] = validate_priority(pri)
                    except ValueError:
                        pass
                feature['sub_features'].append(sf)

            if not sf:
                continue

            for tbl in sf_block.tables:
                rows = tbl.get('rows', [])
                if not rows:
                    continue
                headers = [h.lower() for h in tbl.get('headers', [])]
                for row in rows:
                    missing = [c for c in REQUIRED_TP_COLS if c not in headers]
                    if missing:
                        continue
                    tp_name = row.get('tp_name', '').strip()
                    if not tp_name:
                        continue
                    skip = False
                    if tp_name.startswith('[SKIP] '):
                        tp_name = tp_name[7:]
                        skip = True

                    tp_id = _next_tp_id(sf.get('testpoints', []))
                    tp = {
                        'tp_id': tp_id,
                        'tp_name': tp_name,
                        'source': row.get('source', '').strip(),
                        'stimulus': row.get('stimulus', '').strip(),
                        'checking': row.get('checking', 'by_checker').strip(),
                        'coverage_requirements': row.get('coverage_requirements', '').strip(),
                        'priority': validate_priority(row.get('priority', 'MID')),
                        'category': row.get('category', 'normal').strip(),
                        'path2source': row.get('path2source', '').strip(),
                        'skip': skip,
                    }
                    sf.setdefault('testpoints', []).append(tp)

    manager.data['features'] = features
    manager.save()
    stats = manager.get_stats()
    print(f"Build 完成: features={stats['features']}, sub_features={stats['sub_features']}, testpoints={stats['testpoints']}")
    return 0
