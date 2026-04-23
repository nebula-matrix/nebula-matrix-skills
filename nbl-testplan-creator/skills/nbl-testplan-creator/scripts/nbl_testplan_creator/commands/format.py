"""Format command: json -> md/csv/excel."""

from pathlib import Path
import csv


def cmd_format(manager, args) -> int:
    manager.load()
    fmt = args.format
    output = Path(args.output) if args.output else None

    if fmt == 'md':
        from nbl_testplan_creator.generator.markdown import generate_markdown
        content = generate_markdown(manager.data, full=args.full, numbered=not args.no_number)
        if output:
            output.write_text(content, encoding='utf-8')
            print(f"已生成: {output}")
        else:
            print(content)
        return 0

    elif fmt == 'csv':
        return _format_csv(manager.data, output)

    elif fmt == 'excel':
        return _format_excel(manager.data, output)

    else:
        print(f"错误: 未知格式: {fmt}")
        return 1


def _format_csv(data: dict, output: Path | None) -> int:
    import io
    headers = ['feature_id', 'feature_name', 'sub_feature_id', 'sub_feature_name',
               'tp_id', 'tp_name', 'stimulus', 'checking', 'priority', 'category', 'source']

    rows = []
    for f in data.get('features', []):
        for sf in f.get('sub_features', []):
            for tp in sf.get('testpoints', []):
                rows.append({
                    'feature_id': f['feature_id'],
                    'feature_name': f.get('feature_name', ''),
                    'sub_feature_id': sf['sub_feature_id'],
                    'sub_feature_name': sf.get('sub_feature_name', ''),
                    'tp_id': tp['tp_id'],
                    'tp_name': tp.get('tp_name', ''),
                    'stimulus': tp.get('stimulus', '').replace('\n', ' '),
                    'checking': tp.get('checking', ''),
                    'priority': tp.get('priority', ''),
                    'category': tp.get('category', ''),
                    'source': tp.get('source', ''),
                })

    if output:
        with open(output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        print(f"已生成 CSV: {output}")
    else:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
        print(buf.getvalue())
    return 0


def _format_excel(data: dict, output: Path | None) -> int:
    try:
        import openpyxl
    except ImportError:
        print("错误: 生成 Excel 需要 openpyxl: uv add openpyxl")
        return 1

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "测试计划"

    headers = ['Feature', 'SubFeature', 'TP_ID', 'TP名称', '激励', '检查方式',
               '优先级', '类型', '来源']
    ws.append(headers)

    for f in data.get('features', []):
        for sf in f.get('sub_features', []):
            for tp in sf.get('testpoints', []):
                ws.append([
                    f.get('feature_name', ''),
                    sf.get('sub_feature_name', ''),
                    tp.get('tp_id', ''),
                    tp.get('tp_name', ''),
                    tp.get('stimulus', ''),
                    tp.get('checking', ''),
                    tp.get('priority', ''),
                    tp.get('category', ''),
                    tp.get('source', ''),
                ])

    out_path = output or Path('testplan.xlsx')
    wb.save(out_path)
    print(f"已生成 Excel: {out_path}")
    return 0
