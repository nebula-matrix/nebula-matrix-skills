#!/usr/bin/env python3
"""
统一 Feature CLI - 三级Feature结构统一管理工具
提供 Feature、Sub-Feature、Testpoint 的完整生命周期管理
"""

import json
import argparse
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class FeatureManager:
    """三级Feature结构管理器"""

    def __init__(self, json_path: str):
        """初始化并加载数据"""
        self.json_path = Path(json_path)
        self.data = self._load_json()

    def _load_json(self) -> Dict[str, Any]:
        """加载JSON文件"""
        if not self.json_path.exists():
            print(f"❌ 错误：文件不存在: {self.json_path}")
            print(f"💡 请先使用 'init' 命令创建文件")
            sys.exit(1)

        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ 错误：JSON格式无效: {e}")
            sys.exit(1)

        return data

    def _save_json(self):
        """保存JSON文件（自动更新时间戳）"""
        self.data['metadata']['modified'] = datetime.now().isoformat()

        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _encode_name(name: str) -> str:
        """编码 name 为合法 ID：去掉前后空白、所有空格和点号"""
        return re.sub(r'[\s\.]+', '', name.strip()).lower()

    def _parse_path(self, path: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        解析路径 feature_name.sub_feature_name.tp_id
        """
        parts = path.split('.')

        feature_id = parts[0]
        sub_feature_id = parts[1] if len(parts) > 1 else None
        tp_id = parts[2] if len(parts) > 2 else None

        return feature_id, sub_feature_id, tp_id

    def _get_next_tp_id(self, feature_id: str, sub_feature_id: str) -> str:
        """获取sub_feature内的下一个tp_id"""
        path = f"{feature_id}.{sub_feature_id}"
        sub_feature = self._find_node(path)
        if not sub_feature or not sub_feature.get('testpoints'):
            return 't000'

        max_id = max(
            int(tp['tp_id'][1:])
            for tp in sub_feature['testpoints']
        )
        return f't{max_id + 1:03d}'

    def _find_node(self, path: str) -> Optional[Dict[str, Any]]:
        """根据路径查找节点"""
        feature_id, sub_feature_id, tp_id = self._parse_path(path)

        # 查找 feature
        feature = next(
            (f for f in self.data.get('features', [])
             if f['feature_id'] == feature_id),
            None
        )

        if not feature:
            return None

        if not sub_feature_id:
            return feature

        # 查找 sub_feature
        sub_feature = next(
            (sf for sf in feature.get('sub_features', [])
             if sf['sub_feature_id'] == sub_feature_id),
            None
        )

        if not sub_feature or not tp_id:
            return sub_feature

        # 查找 testpoint
        testpoint = next(
            (tp for tp in sub_feature.get('testpoints', [])
             if tp['tp_id'] == tp_id),
            None
        )

        return testpoint

    def _validate_priority(self, value: str) -> bool:
        """验证优先级"""
        return value.upper() in ['LOW', 'MID', 'HIGH']

    def _validate_checking(self, value: str) -> bool:
        """验证检查方式（非空即可，推荐值为 by_checker/by_direct_tc/by_assertion）"""
        return bool(value.strip())

    def _parse_sections(self, sections_str: str) -> List[str]:
        """解析章节列表"""
        sections = [s.strip() for s in sections_str.split(',')]
        for s in sections:
            if not re.match(r'^S\d+$', s):
                raise ValueError(f"无效的章节ID: {s}")
        return sections

    @staticmethod
    def cmd_init(json_path: str, title: str = ""):
        """init命令实现（静态方法，不需要实例）"""
        path = Path(json_path)

        # 如果文件存在，创建备份
        if path.exists():
            backup_path = path.with_suffix('.bk')

            if backup_path.exists():
                backup_path = path.with_suffix('.old')

            if backup_path.exists():
                # 添加时间戳
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                backup_path = path.with_suffix(f'.bk.{timestamp}')

            # 移动现有文件到备份
            path.rename(backup_path)
            print(f"💾 已备份现有文件到: {backup_path}")

        # 创建新文件
        initial_data = {
            "document_title": title,
            "metadata": {
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "features": []
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 已初始化: {json_path}")

    def cmd_tree(self, show_skip: bool = False):
        """tree命令实现"""
        lines = []

        for feature in self.data.get('features', []):
            if not show_skip and feature.get('skip', False):
                continue

            f_id = feature['feature_id']
            f_name = feature['feature_name']
            skip_mark = " [SKIP]" if feature.get('skip') else ""

            lines.append(f"[{f_id}] {f_name}{skip_mark}")

            for sub_feature in feature.get('sub_features', []):
                if not show_skip and sub_feature.get('skip', False):
                    continue

                sf_id = sub_feature['sub_feature_id']
                sf_desc = sub_feature['description'][:40]
                skip_mark = " [SKIP]" if sub_feature.get('skip') else ""

                lines.append(f"    -- [{sf_id}] {sf_desc}{skip_mark}")

                for tp in sub_feature.get('testpoints', []):
                    if not show_skip and tp.get('skip', False):
                        continue

                    tp_id = tp['tp_id']
                    tp_name = tp.get('tp_name', '') or tp_id
                    skip_mark = " [SKIP]" if tp.get('skip') else ""

                    lines.append(f"        -- [{tp_id}] {tp_name}{skip_mark}")

        print('\n'.join(lines))

    def cmd_add_feature(self, **kwargs):
        """add feature命令实现"""
        required = ['feature_name', 'description', 'priority']
        for field in required:
            if field not in kwargs:
                print(f"❌ 错误：缺少必需字段 '{field}'")
                print(f"💡 必需字段: {', '.join(required)}")
                return False

        # 验证优先级
        if not self._validate_priority(kwargs['priority']):
            print(f"❌ 错误：无效的优先级 '{kwargs['priority']}'")
            print(f"💡 有效值: LOW, MID, HIGH")
            return False

        # 编码名称作为 feature_id
        feature_name = kwargs['feature_name'].strip()
        feature_id = self._encode_name(feature_name)
        if not feature_id:
            print(f"❌ 错误：feature_name 编码后为空，请使用有效的名称")
            return False

        # 检查全局唯一性
        existing = [f['feature_id'] for f in self.data.get('features', [])]
        if feature_id in existing:
            print(f"❌ 错误：Feature ID '{feature_id}' 已存在")
            print(f"💡 已存在的 Feature: {', '.join(existing)}")
            return False

        # 创建新feature
        new_feature = {
            "feature_id": feature_id,
            "feature_name": feature_name,
            "description": kwargs['description'],
            "priority": kwargs['priority'].upper(),
            "sections_covered": [],
            "skip": False,
            "sub_features": []
        }

        # 处理可选字段
        if 'sections_covered' in kwargs:
            try:
                new_feature['sections_covered'] = self._parse_sections(kwargs['sections_covered'])
            except ValueError as e:
                print(f"❌ 错误：{e}")
                return False

        self.data['features'].append(new_feature)
        self._save_json()

        print(f"✅ 成功添加Feature: {new_feature['feature_id']} ({new_feature['feature_name']})")
        return True

    def cmd_add_subfeature(self, feature_id: str, **kwargs):
        """add subfeature命令实现"""
        # 查找父feature
        feature = self._find_node(feature_id)
        if not feature:
            print(f"❌ 错误：Feature ID '{feature_id}' 不存在")
            available = [f['feature_id'] for f in self.data.get('features', [])]
            print(f"💡 可用的Feature: {', '.join(available)}")
            return False

        required = ['sub_feature_name', 'description', 'spec_id', 'priority']
        for field in required:
            if field not in kwargs:
                print(f"❌ 错误：缺少必需字段 '{field}'")
                print(f"💡 必需字段: {', '.join(required)}")
                return False

        # 验证优先级
        if not self._validate_priority(kwargs['priority']):
            print(f"❌ 错误：无效的优先级 '{kwargs['priority']}'")
            print(f"💡 有效值: LOW, MID, HIGH")
            return False

        # 编码名称作为 sub_feature_id
        sub_feature_name = kwargs['sub_feature_name'].strip()
        sub_feature_id = self._encode_name(sub_feature_name)
        if not sub_feature_id:
            print(f"❌ 错误：sub_feature_name 编码后为空，请使用有效的名称")
            return False

        # 检查同 feature 唯一性
        existing = [sf['sub_feature_id'] for sf in feature.get('sub_features', [])]
        if sub_feature_id in existing:
            print(f"❌ 错误：SubFeature ID '{sub_feature_id}' 在该 Feature 下已存在")
            print(f"💡 已存在的 SubFeature: {', '.join(existing)}")
            return False

        # 创建新sub_feature
        new_subfeature = {
            "sub_feature_id": sub_feature_id,
            "sub_feature_name": sub_feature_name,
            "description": kwargs['description'],
            "spec_id": kwargs['spec_id'],
            "priority": kwargs['priority'].upper(),
            "skip": False,
            "testpoints": []
        }

        if 'sub_features' not in feature:
            feature['sub_features'] = []

        feature['sub_features'].append(new_subfeature)
        self._save_json()

        print(f"✅ 成功添加Sub-Feature: {feature_id}.{sub_feature_id} ({sub_feature_name})")
        return True

    def _find_feature_by_name(self, name: str) -> Optional[str]:
        """根据原始名称查找 feature_id（编码后匹配）"""
        encoded = self._encode_name(name)
        for f in self.data.get('features', []):
            if f['feature_id'] == encoded:
                return f['feature_id']
        return None

    def _find_subfeature_by_name(self, feature_id: str, name: str) -> Optional[str]:
        """根据原始名称在指定 feature 下查找 sub_feature_id（编码后匹配）"""
        encoded = self._encode_name(name)
        feature = self._find_node(feature_id)
        if not feature:
            return None
        for sf in feature.get('sub_features', []):
            if sf['sub_feature_id'] == encoded:
                return sf['sub_feature_id']
        return None

    def _parse_md_with_headings(self, lines: list, strict: bool = True) -> Tuple[dict, dict, list, list, dict, dict]:
        """解析带 heading 的 markdown 文件

        Args:
            strict: True=import模式（heading必须对应已有节点，否则跳过/报错）
                    False=build模式（不验证存在性，所有heading都解析）

        返回:
            feature_updates: dict {feature_id: (attrs, line_no)}
            subfeature_updates: dict {path: (attrs, line_no)}
            tp_tables: list of {'path': str, 'headers': list, 'rows': list, 'line_no': int}
            errors: list of str
            feature_texts: dict {feature_id: original heading text}
            subfeature_texts: dict {path: original heading text}
        """
        heading_re = re.compile(r'^(#{1,6})\s+(.*)$')

        feature_updates = {}
        subfeature_updates = {}
        tp_tables = []
        errors = []
        feature_texts = {}
        subfeature_texts = {}

        current_feature = None
        current_path = None
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            heading_match = heading_re.match(stripped)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()

                if level == 1:
                    # # 文档标题/元数据，不参与路径映射
                    pass

                elif level == 2:
                    # ## Feature heading：去除编号前缀，文本编码后作为 feature_id
                    clean_text = re.sub(r'^\d+(\.\d+)*\.?\s*', '', text).strip()
                    encoded_fid = self._encode_name(clean_text)
                    if not encoded_fid:
                        # 空标题，跳过
                        i += 1
                        continue

                    if strict:
                        # import 模式：只解析已存在于 json 中的 feature
                        matched_fid = self._find_feature_by_name(clean_text)
                        if not matched_fid:
                            # 不是已知 feature，当作文档标题跳过
                            i += 1
                            continue
                        encoded_fid = matched_fid

                    current_feature = encoded_fid
                    current_path = None
                    attrs, i = self._parse_property_block(lines, i + 1)
                    feature_updates[current_feature] = (attrs, i + 1)
                    feature_texts[current_feature] = clean_text

                elif level == 3:
                    # ### SubFeature heading：去除编号前缀
                    clean_text = re.sub(r'^\d+(\.\d+)*\.?\s*', '', text).strip()
                    parts = clean_text.split('.')
                    if len(parts) == 2:
                        # 完整路径写法: feature_name.sub_feature_name
                        feat_part = self._encode_name(parts[0])
                        sf_part = self._encode_name(parts[1])
                        if feat_part and sf_part:
                            current_path = f"{feat_part}.{sf_part}"
                            current_feature = feat_part
                            attrs, i = self._parse_property_block(lines, i + 1)
                            subfeature_updates[current_path] = (attrs, i + 1)
                            subfeature_texts[current_path] = parts[1]
                        else:
                            errors.append(f"❌ 错误：第 {i + 1} 行 ### heading '{text}' 编码后路径无效")
                    elif current_feature:
                        # 简写: 仅 sub_feature_name（编码后拼接当前 feature）
                        encoded_sfid = self._encode_name(clean_text)
                        if not encoded_sfid:
                            errors.append(f"❌ 错误：第 {i + 1} 行 ### heading '{text}' 编码后为空")
                            i += 1
                            continue

                        if strict:
                            matched_sfid = self._find_subfeature_by_name(current_feature, clean_text)
                            if not matched_sfid:
                                feature = self._find_node(current_feature)
                                available = [sf.get('sub_feature_name', sf['sub_feature_id']) for sf in feature.get('sub_features', [])]
                                errors.append(f"❌ 错误：路径 '{text}' 不存在（第 {i + 1} 行 heading）。可用 SubFeature: {', '.join(available)}")
                                i += 1
                                continue
                            encoded_sfid = matched_sfid

                        current_path = f"{current_feature}.{encoded_sfid}"
                        attrs, i = self._parse_property_block(lines, i + 1)
                        subfeature_updates[current_path] = (attrs, i + 1)
                        subfeature_texts[current_path] = clean_text
                    else:
                        # strict 模式下：如果 current_feature 为 None（前面无有效 ## heading），
                        # 该 ### 可能属于文档结构，跳过不报错；
                        # 仅在非 strict（build）或已有 current_feature 时报错
                        if not strict:
                            errors.append(f"❌ 错误：第 {i + 1} 行 ### heading '{text}' 缺少 Feature 上下文（请在上方添加 ## Feature heading）")

                i += 1
                continue

            # 检测表格开始
            if stripped.startswith('|'):
                table_data, i = self._parse_markdown_table(lines, i)
                if table_data and table_data['rows']:
                    if 'tp_name' not in table_data['headers']:
                        # 不以 tp_name 开头的表格通常是上一表格的断裂行或格式错误
                        errors.append(f"❌ 错误：第 {table_data['line_no']} 行开始的表格缺少必需的 'tp_name' 列。请检查上一行是否存在未闭合的 `|` 或列数不足，修复 markdown 格式后重试")
                    else:
                        tp_tables.append({
                            'path': current_path,
                            'headers': table_data['headers'],
                            'rows': table_data['rows'],
                            'line_no': table_data['line_no']
                        })
                continue

            i += 1

        return feature_updates, subfeature_updates, tp_tables, errors, feature_texts, subfeature_texts

    def _parse_property_block(self, lines: list, start_idx: int) -> tuple:
        """从指定行开始解析属性块（连续以 - 或 > 开头的行，> 为兼容旧格式）"""
        attrs = {}
        i = start_idx
        # 跳过 heading 后的空行
        while i < len(lines) and not lines[i].strip():
            i += 1
        while i < len(lines) and (lines[i].strip().startswith('-') or lines[i].strip().startswith('>')):
            line = lines[i].strip()
            # 去掉开头的列表符号和空格
            if line.startswith('- '):
                line = line[2:]
            elif line.startswith('-'):
                line = line[1:]
            elif line.startswith('> '):
                line = line[2:]
            elif line.startswith('>'):
                line = line[1:]

            if ':' in line:
                key, value = line.split(':', 1)
                attrs[key.strip()] = value.strip()
            i += 1
        return attrs, i - 1

    def _parse_markdown_table(self, lines: list, start_idx: int) -> tuple:
        """解析 markdown 表格块

        返回: (dict {'headers': [...], 'rows': [...], 'line_no': int}, end_idx)
        或 (None, start_idx) 如果解析失败
        """
        i = start_idx
        headers = None
        rows = []
        line_no = i + 1

        while i < len(lines):
            line = lines[i].strip()

            # 空行或不以 | 开头的行结束表格
            if not line or not line.startswith('|'):
                break

            parts = [p.strip() for p in line.split('|')]
            # 去掉首尾的空字符串
            if parts and not parts[0]:
                parts = parts[1:]
            if parts and not parts[-1]:
                parts = parts[:-1]

            # 跳过分隔行 |---|---|
            if all(set(p) <= {'-', ':', ' '} for p in parts):
                i += 1
                continue

            if not headers:
                headers = parts
            else:
                if len(parts) != len(headers):
                    # 列数不匹配，结束当前表格
                    break
                rows.append(dict(zip(headers, parts)))

            i += 1

        if headers and rows:
            return {'headers': headers, 'rows': rows, 'line_no': line_no}, i
        return None, i

    def _apply_attributes(self, node: dict, attrs: dict, line_no: int) -> bool:
        """将属性字典应用到节点

        返回 True 表示成功，False 表示有错误
        """
        for key, value in attrs.items():
            try:
                if key == 'priority':
                    if not self._validate_priority(value):
                        print(f"❌ 错误：第 {line_no} 行 heading 的属性 '{key}' 值 '{value}' 无效，请使用 LOW/MID/HIGH")
                        return False
                    node['priority'] = value.upper()
                elif key == 'sections_covered':
                    try:
                        node['sections_covered'] = self._parse_sections(value)
                    except ValueError as e:
                        print(f"❌ 错误：第 {line_no} 行 heading 的属性 '{key}' 值无效: {e}")
                        return False
                elif key == 'skip':
                    node['skip'] = value.lower() in ('true', 'yes', '1')
                elif key == 'feature_name':
                    node['feature_name'] = value
                elif key == 'description':
                    node['description'] = value
                elif key == 'sub_feature_name':
                    node['sub_feature_name'] = value
                elif key == 'spec_id':
                    node['spec_id'] = value
                else:
                    # 未知属性直接保存
                    node[key] = value
            except Exception as e:
                print(f"❌ 错误：第 {line_no} 行 heading 的属性 '{key}' 处理失败: {e}")
                return False
        return True

    def cmd_import(self, md_file: str):
        """import命令实现：从markdown heading+表格批量导入（仅支持heading模式）"""
        md_path = Path(md_file)
        if not md_path.exists():
            print(f"❌ 错误：文件不存在: {md_file}")
            return False

        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        feature_updates, subfeature_updates, tp_tables, errors, feature_texts, subfeature_texts = self._parse_md_with_headings(lines)

        if errors:
            print('\n'.join(errors))
            return False

        has_headings = bool(feature_updates or subfeature_updates or tp_tables)
        if not has_headings:
            print(f"❌ 错误：文件中未找到有效的 markdown heading")
            print(f"💡 请确保 markdown 文件包含 ## Feature / ### SubFeature heading 和表格")
            return False

        # ===== 校验与写入 =====

        # 1. 校验 feature 更新
        for fid, (attrs, line_no) in feature_updates.items():
            feature = self._find_node(fid)
            if not feature:
                available = [f['feature_id'] for f in self.data.get('features', [])]
                print(f"❌ 错误：路径 '{fid}' 不存在（第 {line_no} 行 heading）")
                print(f"💡 可用的Feature: {', '.join(available)}")
                return False
            if not self._apply_attributes(feature, attrs, line_no):
                return False

        # 2. 校验 subfeature 更新
        for spath, (attrs, line_no) in subfeature_updates.items():
            subfeature = self._find_node(spath)
            if not subfeature:
                fid, sfid, _ = self._parse_path(spath)
                feat = self._find_node(fid)
                available = []
                if feat:
                    available = [f"{fid}.{sf['sub_feature_id']}" for sf in feat.get('sub_features', [])]
                print(f"❌ 错误：路径 '{spath}' 不存在（第 {line_no} 行 heading）")
                print(f"💡 可用路径: {', '.join(available) if available else '无'}")
                return False
            if not self._apply_attributes(subfeature, attrs, line_no):
                return False

        # 3. 校验并添加 testpoints
        total_tps = 0
        for table_info in tp_tables:
            table_path = table_info['path']
            table_line_no = table_info['line_no']

            if not table_path:
                print(f"❌ 错误：第 {table_line_no} 行开始的表格缺少归属的 ### SubFeature heading")
                return False

            # 校验 subfeature 存在
            subfeature = self._find_node(table_path)
            if not subfeature:
                fid, sfid, _ = self._parse_path(table_path)
                feat = self._find_node(fid)
                available = []
                if feat:
                    available = [f"{fid}.{sf['sub_feature_id']}" for sf in feat.get('sub_features', [])]
                print(f"❌ 错误：路径 '{table_path}' 不存在")
                print(f"💡 可用路径: {', '.join(available) if available else '无'}")
                return False

            # 校验表格行
            headers = table_info['headers']
            rows = table_info['rows']

            required_cols = ['tp_name', 'stimulus', 'checking', 'priority']
            for col in required_cols:
                if col not in headers:
                    print(f"❌ 错误：表格缺少必需列 '{col}'")
                    return False

            for idx, row in enumerate(rows, start=1):
                for col in required_cols:
                    if not row.get(col, '').strip():
                        print(f"❌ 错误：第 {idx} 行（归属 {table_path}）缺少必填值 '{col}'，请补充后重新导入。")
                        return False

                priority = row['priority'].strip()
                if not self._validate_priority(priority):
                    print(f"❌ 错误：第 {idx} 行（归属 {table_path}）priority 值 '{priority}' 无效，请使用 LOW/MID/HIGH")
                    return False

                checking = row['checking'].strip()
                if not self._validate_checking(checking):
                    print(f"❌ 错误：第 {idx} 行（归属 {table_path}）checking 值 '{checking}' 无效")
                    return False

            total_tps += len(rows)

        # 全部校验通过，执行写入
        # 1. 应用属性更新
        for fid, (attrs, _) in feature_updates.items():
            feature = self._find_node(fid)
            self._apply_attributes(feature, attrs, 0)

        for spath, (attrs, _) in subfeature_updates.items():
            subfeature = self._find_node(spath)
            self._apply_attributes(subfeature, attrs, 0)

        # 2. 添加 testpoints
        for table_info in tp_tables:
            table_path = table_info['path']
            fid, sfid, _ = self._parse_path(table_path)
            subfeature = self._find_node(table_path)

            if 'testpoints' not in subfeature:
                subfeature['testpoints'] = []

            for row in table_info['rows']:
                priority = row['priority'].strip()
                checking = row['checking'].strip()

                tp_name = row['tp_name'].strip()
                skip = False
                if tp_name.startswith('[SKIP] '):
                    tp_name = tp_name[7:]
                    skip = True
                new_tp = {
                    "tp_id": self._get_next_tp_id(fid, sfid),
                    "tp_name": tp_name,
                    "source": row.get('source', row.get('remarks', '')).strip(),
                    "stimulus": row['stimulus'].strip(),
                    "checking": checking.lower(),
                    "coverage_requirements": row.get('coverage_requirements', '').strip(),
                    "priority": priority.upper(),
                    "skip": skip,
                    "category": row.get('category', 'normal').strip(),
                    "path2source": row.get('path2source', '').strip()
                }
                subfeature['testpoints'].append(new_tp)

        self._save_json()

        # 打印汇总
        parts = []
        if feature_updates:
            parts.append(f"{len(feature_updates)} 个 Feature 属性已更新")
        if subfeature_updates:
            parts.append(f"{len(subfeature_updates)} 个 SubFeature 属性已更新")
        if tp_tables:
            parts.append(f"{total_tps} 个 Testpoint 已导入")
        print(f"✅ {'；'.join(parts) if parts else '导入完成'}")

        return True

    def cmd_build(self, md_file: str):
        """build命令：从markdown文件重建features.json"""
        md_path = Path(md_file)
        if not md_path.exists():
            print(f"❌ 错误：文件不存在: {md_file}")
            return False

        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        feature_updates, subfeature_updates, tp_tables, errors, feature_texts, subfeature_texts = self._parse_md_with_headings(lines, strict=False)

        # 分离警告和错误：⚠️ 警告打印后继续，❌ 错误则中断
        warnings = [e for e in errors if e.startswith('⚠️')]
        fatal_errors = [e for e in errors if e.startswith('❌')]
        if warnings:
            print('\n'.join(warnings))
        if fatal_errors:
            print('\n'.join(fatal_errors))
            return False

        # 清空现有features，重建
        self.data['features'] = []

        # 1. 创建所有Feature
        for fid, (attrs, line_no) in feature_updates.items():
            display_name = attrs.get('feature_name', feature_texts.get(fid, fid))

            # 校验必填字段
            if 'description' not in attrs:
                print(f"❌ 错误：第 {line_no} 行 ## heading 缺少 `description`，创建 Feature 时必填")
                return False
            if 'priority' not in attrs:
                print(f"❌ 错误：第 {line_no} 行 ## heading 缺少 `priority`，创建 Feature 时必填")
                return False
            if not self._validate_priority(attrs['priority']):
                print(f"❌ 错误：第 {line_no} 行 heading 的 priority 值 '{attrs['priority']}' 无效，请使用 LOW/MID/HIGH")
                return False

            feature = {
                "feature_id": fid,
                "feature_name": display_name,
                "description": attrs['description'],
                "priority": attrs['priority'].upper(),
                "sections_covered": [],
                "skip": False,
                "sub_features": []
            }

            # 处理可选字段
            if 'sections_covered' in attrs:
                try:
                    feature['sections_covered'] = self._parse_sections(attrs['sections_covered'])
                except ValueError as e:
                    print(f"❌ 错误：第 {line_no} 行 heading 的 sections_covered 无效: {e}")
                    return False
            if 'skip' in attrs:
                feature['skip'] = attrs['skip'].lower() in ('true', 'yes', '1')

            self.data['features'].append(feature)

        # 2. 创建所有SubFeature
        for spath, (attrs, line_no) in subfeature_updates.items():
            fid, sfid, _ = self._parse_path(spath)
            feature = self._find_node(fid)
            if not feature:
                print(f"❌ 错误：路径 '{spath}' 的父 Feature '{fid}' 未在 ## heading 中声明")
                return False

            display_name = attrs.get('sub_feature_name', subfeature_texts.get(spath, sfid))

            required_sf = ['description', 'spec_id', 'priority']
            for field in required_sf:
                if field not in attrs:
                    print(f"❌ 错误：第 {line_no} 行 ### heading 缺少 `{field}`，创建 SubFeature 时必填")
                    return False
            if not self._validate_priority(attrs['priority']):
                print(f"❌ 错误：第 {line_no} 行 heading 的 priority 值 '{attrs['priority']}' 无效，请使用 LOW/MID/HIGH")
                return False

            subfeature = {
                "sub_feature_id": sfid,
                "sub_feature_name": display_name,
                "description": attrs['description'],
                "spec_id": attrs['spec_id'],
                "priority": attrs['priority'].upper(),
                "skip": False,
                "testpoints": []
            }

            feature['sub_features'].append(subfeature)

        # 3. 添加Testpoints
        total_tps = 0
        for table_info in tp_tables:
            table_path = table_info['path']
            if not table_path:
                print(f"❌ 错误：第 {table_info['line_no']} 行开始的表格缺少归属的 ### SubFeature heading")
                return False

            fid, sfid, _ = self._parse_path(table_path)
            subfeature = self._find_node(table_path)
            if not subfeature:
                print(f"❌ 错误：路径 '{table_path}' 不存在（该 SubFeature 可能未通过 ### heading 声明）")
                return False

            headers = table_info['headers']
            rows = table_info['rows']

            required_cols = ['tp_name', 'stimulus', 'checking', 'priority']
            for col in required_cols:
                if col not in headers:
                    print(f"❌ 错误：表格缺少必需列 '{col}'")
                    return False

            for idx, row in enumerate(rows, start=1):
                for col in required_cols:
                    if not row.get(col, '').strip():
                        print(f"❌ 错误：第 {idx} 行（归属 {table_path}）缺少必填值 '{col}'")
                        return False
                priority = row['priority'].strip()
                if not self._validate_priority(priority):
                    print(f"❌ 错误：第 {idx} 行 priority 值 '{priority}' 无效")
                    return False
                checking = row['checking'].strip()
                if not self._validate_checking(checking):
                    print(f"❌ 错误：第 {idx} 行 checking 值 '{checking}' 无效")
                    return False

            for row in rows:
                priority = row['priority'].strip()
                checking = row['checking'].strip()
                tp_name = row['tp_name'].strip()
                skip = False
                if tp_name.startswith('[SKIP] '):
                    tp_name = tp_name[7:]
                    skip = True
                new_tp = {
                    "tp_id": self._get_next_tp_id(fid, sfid),
                    "tp_name": tp_name,
                    "source": row.get('source', row.get('remarks', '')).strip(),
                    "stimulus": row['stimulus'].strip(),
                    "checking": checking.lower(),
                    "coverage_requirements": row.get('coverage_requirements', '').strip(),
                    "priority": priority.upper(),
                    "skip": skip,
                    "category": row.get('category', 'normal').strip(),
                    "path2source": row.get('path2source', '').strip()
                }
                subfeature['testpoints'].append(new_tp)

            total_tps += len(rows)

        self._save_json()

        parts = []
        if feature_updates:
            parts.append(f"{len(feature_updates)} 个 Feature 已创建")
        if subfeature_updates:
            parts.append(f"{len(subfeature_updates)} 个 SubFeature 已创建")
        if tp_tables:
            parts.append(f"{total_tps} 个 Testpoint 已导入")
        print(f"✅ {'；'.join(parts) if parts else '构建完成'}")
        return True


    def cmd_add_tp(self, path: str, **kwargs):
        """add tp命令实现"""
        feature_id, sub_feature_id, _ = self._parse_path(path)

        if not sub_feature_id:
            print(f"❌ 错误：路径必须包含Sub-Feature")
            print(f"💡 格式应为: feature_name.sub_feature_name（如: 队列管理.队列深度配置）")
            return False

        sub_feature = self._find_node(f"{feature_id}.{sub_feature_id}")
        if not sub_feature:
            print(f"❌ 错误：路径 '{path}' 不存在")
            return False

        required = ['tp_name', 'stimulus', 'checking', 'priority']
        for field in required:
            if field not in kwargs:
                print(f"❌ 错误：缺少必需字段 '{field}'")
                print(f"💡 必需字段: {', '.join(required)}")
                return False

        # 验证优先级
        if not self._validate_priority(kwargs['priority']):
            print(f"❌ 错误：无效的优先级 '{kwargs['priority']}'")
            print(f"💡 有效值: LOW, MID, HIGH")
            return False

        # 验证checking
        if not self._validate_checking(kwargs['checking']):
            print(f"❌ 错误：无效的检查方式 '{kwargs['checking']}'")
            print(f"💡 有效值: by_checker, by_direct_tc, by_assertion")
            return False

        # 创建新testpoint
        new_tp = {
            "tp_id": self._get_next_tp_id(feature_id, sub_feature_id),
            "tp_name": kwargs['tp_name'],
            "source": kwargs.get('source', kwargs.get('remarks', '')),
            "stimulus": kwargs['stimulus'],
            "checking": kwargs['checking'].lower(),
            "coverage_requirements": kwargs.get('coverage_requirements', ''),
            "priority": kwargs['priority'].upper(),
            "skip": False,
            "category": kwargs.get('category', 'normal')
        }

        if 'testpoints' not in sub_feature:
            sub_feature['testpoints'] = []

        sub_feature['testpoints'].append(new_tp)
        self._save_json()

        print(f"✅ 成功添加Testpoint: {path}.{new_tp['tp_id']}")
        return True

    def cmd_view(self, path: str, output_format: str = "plain"):
        """view命令实现"""
        node = self._find_node(path)

        if not node:
            print(f"❌ 错误：路径 '{path}' 不存在")
            return False

        if output_format == 'json':
            print(json.dumps(node, ensure_ascii=False, indent=2))
        else:
            # 纯文本格式
            feature_id, sub_feature_id, tp_id = self._parse_path(path)

            if tp_id:
                # Testpoint
                print(f"【Testpoint {path}】")
                print(f"  名称: {node.get('tp_name', '')}")
                print(f"  来源: {node.get('source', '')}")
                print(f"  激励: {node.get('stimulus', '')}")
                print(f"  检查: {node.get('checking', '')}")
                print(f"  覆盖率需求: {node.get('coverage_requirements', '')}")
                print(f"  优先级: {node.get('priority', '')}")
                print(f"  跳过: {'是' if node.get('skip') else '否'}")
                print(f"  类别: {node.get('category', '')}")
            elif sub_feature_id:
                # Sub-Feature
                print(f"【Sub-Feature {path}】")
                print(f"  名称: {node.get('sub_feature_name', '')}")
                print(f"  描述: {node.get('description', '')}")
                print(f"  规格ID: {node.get('spec_id', '')}")
                print(f"  优先级: {node.get('priority', '')}")
                print(f"  跳过: {'是' if node.get('skip') else '否'}")
                print(f"  测试点数: {len(node.get('testpoints', []))}")
            else:
                # Feature
                print(f"【Feature {path}】")
                print(f"  名称: {node.get('feature_name', '')}")
                print(f"  描述: {node.get('description', '')}")
                print(f"  优先级: {node.get('priority', '')}")
                print(f"  覆盖章节: {', '.join(node.get('sections_covered', []))}")
                print(f"  跳过: {'是' if node.get('skip') else '否'}")
                print(f"  子特征数: {len(node.get('sub_features', []))}")

                # 统计测试点
                total_tps = sum(
                    len(sf.get('testpoints', []))
                    for sf in node.get('sub_features', [])
                )
                print(f"  测试点总数: {total_tps}")

        return True

    def cmd_del(self, path: str, force: bool = False):
        """del命令实现"""
        node = self._find_node(path)
        if not node:
            print(f"❌ 错误：路径 '{path}' 不存在")
            return False

        # 显示预览
        print("\n即将删除以下内容:")
        self._print_deletion_preview(path, node)

        # 统计
        count = self._count_descendants(path)
        if count['sub_features'] > 0 or count['testpoints'] > 0:
            print(f"\n共删除 {count['sub_features']} 个 sub-feature 和 {count['testpoints']} 个 testpoint")

        if not force:
            response = input("确认删除？(y/N): ").lower()
            if response != 'y':
                print("❌ 已取消删除")
                return False

        # 执行删除
        self._delete_node(path)
        self._save_json()

        print("✅ 删除成功")
        return True

    def _print_deletion_preview(self, path: str, node: Dict[str, Any]):
        """打印删除预览"""
        feature_id, sub_feature_id, tp_id = self._parse_path(path)

        if tp_id:
            print(f"[{feature_id}] Feature")
            print(f"  -- [{sub_feature_id}] Sub-Feature")
            print(f"      -- [{tp_id}] {node.get('tp_name') or node.get('source', '')[:30]}")
        elif sub_feature_id:
            print(f"[{feature_id}] Feature")
            print(f"  -- [{sub_feature_id}] {node['description'][:40]}")
            for tp in node.get('testpoints', []):
                print(f"      -- [{tp['tp_id']}] {tp.get('tp_name') or tp.get('source', '')[:30]}")
        else:
            print(f"[{feature_id}] {node['feature_name']}")
            for sf in node.get('sub_features', []):
                print(f"  -- [{sf['sub_feature_id']}] {sf['description'][:40]}")
                for tp in sf.get('testpoints', []):
                    print(f"      -- [{tp['tp_id']}] {tp.get('tp_name') or tp.get('source', '')[:30]}")

    def _count_descendants(self, path: str) -> Dict[str, int]:
        """统计子节点数量"""
        node = self._find_node(path)
        feature_id, sub_feature_id, tp_id = self._parse_path(path)

        result = {'sub_features': 0, 'testpoints': 0}

        if tp_id:
            return result
        elif sub_feature_id:
            result['testpoints'] = len(node.get('testpoints', []))
        else:
            result['sub_features'] = len(node.get('sub_features', []))
            result['testpoints'] = sum(
                len(sf.get('testpoints', []))
                for sf in node.get('sub_features', [])
            )

        return result

    def _delete_node(self, path: str):
        """执行节点删除"""
        feature_id, sub_feature_id, tp_id = self._parse_path(path)

        if tp_id:
            # 删除 testpoint
            sub_feature = self._find_node(f"{feature_id}.{sub_feature_id}")
            sub_feature['testpoints'] = [
                tp for tp in sub_feature['testpoints']
                if tp['tp_id'] != tp_id
            ]
        elif sub_feature_id:
            # 删除 sub_feature
            feature = self._find_node(feature_id)
            feature['sub_features'] = [
                sf for sf in feature['sub_features']
                if sf['sub_feature_id'] != sub_feature_id
            ]
        else:
            # 删除 feature
            self.data['features'] = [
                f for f in self.data['features']
                if f['feature_id'] != feature_id
            ]

    def cmd_edit(self, path: str, **kwargs):
        """edit命令实现"""
        node = self._find_node(path)
        if not node:
            print(f"❌ 错误：路径 '{path}' 不存在")
            return False

        feature_id, sub_feature_id, tp_id = self._parse_path(path)

        # 验证和更新字段
        for key, value in kwargs.items():
            if key == 'priority':
                if not self._validate_priority(value):
                    print(f"❌ 错误：无效的优先级 '{value}'")
                    print(f"💡 有效值: LOW, MID, HIGH")
                    return False
                node[key] = value.upper()
            elif key == 'checking' and tp_id:
                if not self._validate_checking(value):
                    print(f"❌ 错误：无效的检查方式 '{value}'")
                    print(f"💡 有效值: by_checker, by_direct_tc, by_assertion")
                    return False
                node[key] = value.lower()
            elif key == 'sections_covered' and not sub_feature_id:
                try:
                    node[key] = self._parse_sections(value)
                except ValueError as e:
                    print(f"❌ 错误：{e}")
                    return False
            else:
                node[key] = value

        self._save_json()
        print(f"✅ 成功编辑节点: {path}")
        return True

    def cmd_replace(self, path: str, **kwargs):
        """replace命令实现"""
        node = self._find_node(path)
        if not node:
            print(f"❌ 错误：路径 '{path}' 不存在")
            return False

        feature_id, sub_feature_id, tp_id = self._parse_path(path)

        # 清空内容字段（保留ID和结构）
        if tp_id:
            # Testpoint: 保留 tp_id
            content_fields = [
                'tp_name', 'source', 'stimulus', 'checking',
                'coverage_requirements', 'priority', 'skip', 'category'
            ]
            for field in content_fields:
                if field in node:
                    del node[field]

            # 设置新值
            if 'priority' in kwargs:
                if not self._validate_priority(kwargs['priority']):
                    print(f"❌ 错误：无效的优先级 '{kwargs['priority']}'")
                    return False
                kwargs['priority'] = kwargs['priority'].upper()

            if 'checking' in kwargs:
                if not self._validate_checking(kwargs['checking']):
                    print(f"❌ 错误：无效的检查方式 '{kwargs['checking']}'")
                    return False
                kwargs['checking'] = kwargs['checking'].lower()

            node.update(kwargs)

        elif sub_feature_id:
            # Sub-Feature: 保留 sub_feature_id
            content_fields = ['sub_feature_name', 'description', 'spec_id', 'priority', 'skip']
            for field in content_fields:
                if field in node:
                    del node[field]

            if 'priority' in kwargs:
                if not self._validate_priority(kwargs['priority']):
                    print(f"❌ 错误：无效的优先级 '{kwargs['priority']}'")
                    return False
                kwargs['priority'] = kwargs['priority'].upper()

            node.update(kwargs)

        else:
            # Feature: 保留 feature_id
            content_fields = ['feature_name', 'description', 'priority', 'sections_covered', 'skip']
            for field in content_fields:
                if field in node:
                    del node[field]

            if 'priority' in kwargs:
                if not self._validate_priority(kwargs['priority']):
                    print(f"❌ 错误：无效的优先级 '{kwargs['priority']}'")
                    return False
                kwargs['priority'] = kwargs['priority'].upper()

            if 'sections_covered' in kwargs:
                try:
                    kwargs['sections_covered'] = self._parse_sections(kwargs['sections_covered'])
                except ValueError as e:
                    print(f"❌ 错误：{e}")
                    return False

            node.update(kwargs)

        self._save_json()
        print(f"✅ 成功替换节点内容: {path}")
        return True

    def cmd_skip(self, path: str, unskip: bool = False):
        """skip命令实现"""
        node = self._find_node(path)
        if not node:
            print(f"❌ 错误：路径 '{path}' 不存在")
            return False

        if unskip:
            node['skip'] = False
            print(f"✅ 已取消跳过标记: {path}")
        else:
            node['skip'] = True
            print(f"✅ 已标记为跳过: {path}")

        self._save_json()
        return True


def parse_key_value_pairs(args: List[str]) -> Dict[str, str]:
    """解析 key=value 参数对"""
    result = {}
    for arg in args:
        if '=' not in arg:
            raise ValueError(f"无效的参数格式: {arg}。使用 key=value")
        key, value = arg.split('=', 1)
        result[key.strip()] = value.strip()
    return result


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description='三级Feature结构统一管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 创建子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化JSON文件')
    init_parser.add_argument('file', help='JSON文件路径')
    init_parser.add_argument('--title', default='', help='文档标题')

    # tree 命令
    tree_parser = subparsers.add_parser('tree', help='显示Feature树结构')
    tree_parser.add_argument('file', help='JSON文件路径')
    tree_parser.add_argument('--show-skip', action='store_true',
                            help='显示被跳过的节点')

    # add 命令（带子命令）
    add_parser = subparsers.add_parser('add', help='添加节点')
    add_subparsers = add_parser.add_subparsers(dest='add_type', help='添加类型')

    # add feature
    add_feat_parser = add_subparsers.add_parser('feature', help='添加Feature')
    add_feat_parser.add_argument('file', help='JSON文件路径')
    add_feat_parser.add_argument('kwargs', nargs='+', help='key=value参数对')

    # add subfeature
    add_sub_parser = add_subparsers.add_parser('subfeature', help='添加Sub-Feature')
    add_sub_parser.add_argument('file', help='JSON文件路径')
    add_sub_parser.add_argument('feature_id', help='父Feature ID')
    add_sub_parser.add_argument('kwargs', nargs='+', help='key=value参数对')

    # add tp
    add_tp_parser = add_subparsers.add_parser('tp', help='添加Testpoint')
    add_tp_parser.add_argument('file', help='JSON文件路径')
    add_tp_parser.add_argument('path', help='Feature.SubFeature路径')
    add_tp_parser.add_argument('kwargs', nargs='+', help='key=value参数对')

    # view 命令
    view_parser = subparsers.add_parser('view', help='查看节点详情')
    view_parser.add_argument('file', help='JSON文件路径')
    view_parser.add_argument('path', help='节点路径')
    view_parser.add_argument('--json', action='store_true', help='JSON格式输出')
    view_parser.add_argument('--plain', action='store_true', default=True,
                            help='纯文本格式输出（默认）')

    # del 命令
    del_parser = subparsers.add_parser('del', help='删除节点')
    del_parser.add_argument('file', help='JSON文件路径')
    del_parser.add_argument('path', help='节点路径')
    del_parser.add_argument('--force', action='store_true', help='跳过确认')

    # edit 命令
    edit_parser = subparsers.add_parser('edit', help='编辑节点字段')
    edit_parser.add_argument('file', help='JSON文件路径')
    edit_parser.add_argument('path', help='节点路径')
    edit_parser.add_argument('kwargs', nargs='+', help='key=value参数对')

    # replace 命令
    replace_parser = subparsers.add_parser('replace', help='替换节点内容')
    replace_parser.add_argument('file', help='JSON文件路径')
    replace_parser.add_argument('path', help='节点路径')
    replace_parser.add_argument('kwargs', nargs='+', help='key=value参数对')

    # import 命令
    import_parser = subparsers.add_parser('import', help='从markdown heading+表格批量导入')
    import_parser.add_argument('file', help='JSON文件路径')
    import_parser.add_argument('md_file', help='markdown文件路径（需包含 ## Feature / ### SubFeature heading）')

    # build 命令：从 markdown 重建 json
    build_parser = subparsers.add_parser('build', help='从markdown文件重建features.json')
    build_parser.add_argument('file', help='JSON文件路径')
    build_parser.add_argument('md_file', help='markdown文件路径')

    # skip 命令
    skip_parser = subparsers.add_parser('skip', help='标记节点为跳过')
    skip_parser.add_argument('file', help='JSON文件路径')
    skip_parser.add_argument('path', help='节点路径')
    skip_parser.add_argument('--unskip', action='store_true', help='取消跳过标记')

    args = parser.parse_args()

    # 命令分发逻辑
    if args.command == 'init':
        FeatureManager.cmd_init(args.file, args.title)

    elif args.command == 'tree':
        cli = FeatureManager(args.file)
        cli.cmd_tree(show_skip=args.show_skip)

    elif args.command == 'add':
        if not hasattr(args, 'add_type') or not args.add_type:
            print("❌ 错误：请指定添加类型: feature, subfeature, tp")
            sys.exit(1)

        try:
            kwargs = parse_key_value_pairs(args.kwargs)
        except ValueError as e:
            print(f"❌ 错误：{e}")
            sys.exit(1)

        cli = FeatureManager(args.file)

        if args.add_type == 'feature':
            cli.cmd_add_feature(**kwargs)
        elif args.add_type == 'subfeature':
            cli.cmd_add_subfeature(args.feature_id, **kwargs)
        elif args.add_type == 'tp':
            cli.cmd_add_tp(args.path, **kwargs)

    elif args.command == 'view':
        cli = FeatureManager(args.file)
        output_format = 'json' if args.json else 'plain'
        cli.cmd_view(args.path, output_format)

    elif args.command == 'del':
        cli = FeatureManager(args.file)
        cli.cmd_del(args.path, force=args.force)

    elif args.command == 'edit':
        try:
            kwargs = parse_key_value_pairs(args.kwargs)
        except ValueError as e:
            print(f"❌ 错误：{e}")
            sys.exit(1)

        cli = FeatureManager(args.file)
        cli.cmd_edit(args.path, **kwargs)

    elif args.command == 'replace':
        try:
            kwargs = parse_key_value_pairs(args.kwargs)
        except ValueError as e:
            print(f"❌ 错误：{e}")
            sys.exit(1)

        cli = FeatureManager(args.file)
        cli.cmd_replace(args.path, **kwargs)

    elif args.command == 'import':
        cli = FeatureManager(args.file)
        if not cli.cmd_import(args.md_file):
            sys.exit(1)

    elif args.command == 'build':
        cli = FeatureManager(args.file)
        if not cli.cmd_build(args.md_file):
            sys.exit(1)

    elif args.command == 'skip':
        cli = FeatureManager(args.file)
        cli.cmd_skip(args.path, unskip=args.unskip)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
