#!/usr/bin/env python3
"""
从统一的 features.json 生成测试计划文档
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


def generate_markdown(features_file: str, output_file: str = None):
    """生成 Markdown 格式的测试计划"""
    with open(features_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    lines = []

    # 标题
    doc_title = data.get('metadata', {}).get('document_title', 'IC模块验证测试计划')
    lines.append(f"# {doc_title} - 验证测试计划\n")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("---\n")

    # 统计信息
    total_features = len(data.get('features', []))
    total_sub_features = 0
    total_testpoints = 0

    for feature in data['features']:
        sfs = len(feature.get('sub_features', []))
        tps = sum(len(sf.get('testpoints', [])) for sf in feature.get('sub_features', []))
        total_sub_features += sfs
        total_testpoints += tps

    lines.append("## 测试计划统计\n")
    lines.append(f"- **Feature 总数**: {total_features}\n")
    lines.append(f"- **Sub-Feature 总数**: {total_sub_features}\n")
    lines.append(f"- **Testpoint 总数**: {total_testpoints}\n")
    lines.append("\n---\n\n")

    # 按优先级分类
    lines.append("## 优先级分布\n")
    high_count = sum(1 for f in data['features'] if f.get('priority') == 'HIGH')
    mid_count = sum(1 for f in data['features'] if f.get('priority') == 'MID')
    low_count = sum(1 for f in data['features'] if f.get('priority') == 'LOW')
    lines.append(f"- **HIGH**: {high_count} features\n")
    lines.append(f"- **MID**: {mid_count} features\n")
    lines.append(f"- **LOW**: {low_count} features\n")
    lines.append("\n---\n\n")

    # Feature 树状结构
    lines.append("## Feature 树状结构\n\n")

    for feature in data['features']:
        fid = feature['feature_id']
        fname = feature['feature_name']
        fpriority = feature.get('priority', 'M')
        fdesc = feature.get('description', '')
        fskip = feature.get('skip', False)

        skip_mark = " [SKIPPED]" if fskip else ""
        lines.append(f"### {fid}: {fname}{skip_mark}\n")
        lines.append(f"- **优先级**: {fpriority}\n")
        lines.append(f"- **描述**: {fdesc}\n")

        sections = feature.get('sections_covered', [])
        if sections:
            lines.append(f"- **覆盖章节**: {', '.join(sections)}\n")

        sfs = feature.get('sub_features', [])
        if sfs:
            lines.append(f"- **Sub-Features**: {len(sfs)}\n")

            for sf in sfs:
                sfid = sf['sub_feature_id']
                sfdesc = sf.get('description', 'N/A')
                sfspec = sf.get('spec_id', '')
                sfpriority = sf.get('priority', 'M')
                sfskip = sf.get('skip', False)

                sf_skip_mark = " [SKIPPED]" if sfskip else ""
                lines.append(f"\n#### {fid}.{sfid}: {sfdesc}{sf_skip_mark}\n")
                if sfspec:
                    lines.append(f"- **规格编号**: {sfspec}\n")
                lines.append(f"- **优先级**: {sfpriority}\n")

                tps = sf.get('testpoints', [])
                if tps:
                    lines.append(f"- **测试点数**: {len(tps)}\n")
                    lines.append("\n| ID | 名称 | 类型 | 优先级 | 备注 | 激励 | 检查方式 |\n")
                    lines.append("|----|------|------|--------|------|------|----------|\n")

                    for tp in tps:
                        tid = tp.get('tp_id', 'N/A')
                        tname = tp.get('tp_name', tid)
                        tcategory = tp.get('category', 'normal')
                        tpriority = tp.get('priority', 'MID')
                        tsource = tp.get('source', '').replace('\n', '<br>')
                        tstimulus = tp.get('stimulus', '').replace('\n', '<br>')
                        tchecking = tp.get('checking', 'checker')
                        tskip = tp.get('skip', False)

                        skip_tp_mark = " ~~" if tskip else ""
                        lines.append(f"| {tid}{skip_tp_mark} | {tname} | {tcategory} | {tpriority} | {tsource} | {tstimulus} | {tchecking} |\n")

        lines.append("\n---\n\n")

    output = ''.join(lines)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ 已生成 Markdown 测试计划: {output_file}")
    else:
        print(output)

    return output


def main():
    parser = argparse.ArgumentParser(description='从 features.json 生成测试计划文档')
    parser.add_argument('features_file', help='features.json 文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（可选）')

    args = parser.parse_args()
    generate_markdown(args.features_file, args.output)


if __name__ == '__main__':
    main()
