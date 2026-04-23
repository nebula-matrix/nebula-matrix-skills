"""CLI entry point with argparse subcommands."""

import argparse
import sys
from pathlib import Path

from nbl_testplan_creator.core.json_manager import FeatureJSON
from nbl_testplan_creator.commands import init, tree, add, view, delete, edit, build, import_cmd, skip, format as fmt, merge, check


def _add_file_arg(parser):
    parser.add_argument('file', help='features.json 文件路径')


def _add_path_arg(parser):
    parser.add_argument('path', help='节点路径 (f001 | f001.s000 | f001.s000.t000)')


def _add_pair_args(parser):
    parser.add_argument('kwargs', nargs='*', help='key=value 参数')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='nbl-testplan',
        description='NBL 测试计划管理工具',
    )
    sub = parser.add_subparsers(dest='command')

    # init
    p_init = sub.add_parser('init', help='初始化 features.json')
    p_init.add_argument('file', help='输出文件路径')
    p_init.add_argument('--title', default='Test Plan', help='文档标题')

    # tree
    p_tree = sub.add_parser('tree', help='显示 Feature 树')
    _add_file_arg(p_tree)
    p_tree.add_argument('--show-skip', action='store_true', help='显示跳过的节点')

    # view
    p_view = sub.add_parser('view', help='查看节点详情')
    _add_file_arg(p_view)
    _add_path_arg(p_view)
    p_view.add_argument('--json', action='store_true', help='JSON 格式输出')

    # skip
    p_skip = sub.add_parser('skip', help='标记跳过')
    _add_file_arg(p_skip)
    _add_path_arg(p_skip)
    p_skip.add_argument('--unskip', action='store_true', help='取消跳过')

    p_add = sub.add_parser('add', help='添加节点')
    p_add.add_argument('add_type', choices=['feature', 'subfeature', 'tp'])
    _add_file_arg(p_add)
    _add_pair_args(p_add)

    # del
    p_del = sub.add_parser('del', help='删除节点')
    _add_file_arg(p_del)
    _add_path_arg(p_del)
    p_del.add_argument('--force', action='store_true', help='强制删除')

    # edit
    p_edit = sub.add_parser('edit', help='编辑节点字段')
    _add_file_arg(p_edit)
    _add_path_arg(p_edit)
    _add_pair_args(p_edit)

    # replace
    p_replace = sub.add_parser('replace', help='替换节点内容')
    _add_file_arg(p_replace)
    _add_path_arg(p_replace)
    _add_pair_args(p_replace)

    # build
    p_build = sub.add_parser('build', help='从 markdown 重建 json（清空后重建，允许新建节点）')
    _add_file_arg(p_build)
    p_build.add_argument('md_file', help='输入 markdown 文件')

    # import -- 增量导入
    p_import = sub.add_parser('import', help='从 markdown 增量导入到 json（仅在现有节点上追加 Testpoint）')
    _add_file_arg(p_import)
    p_import.add_argument('md_file', help='输入 markdown 文件')

    # format
    p_format = sub.add_parser('format', help='格式化输出')
    _add_file_arg(p_format)
    p_format.add_argument('--format', choices=['md', 'csv', 'excel'], default='md')
    p_format.add_argument('-o', '--output', help='输出文件路径')
    p_format.add_argument('--full', action='store_true', default=True, help='完整表格（包含 path2source）')
    p_format.add_argument('--no-number', action='store_true', help='不添加 heading 编号')

    # merge
    p_merge_cmd = sub.add_parser('merge', help='合并 partial markdown 文件')
    p_merge_cmd.add_argument('output', help='输出文件')
    p_merge_cmd.add_argument('partials', nargs='+', help='一个或多个 partial markdown 文件')

    # check
    p_check = sub.add_parser('check', help='检查 markdown 格式完整性')
    p_check.add_argument('md_file', help='输入 markdown 文件')

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Commands that don't need FeatureJSON
    if args.command == 'init':
        sys.exit(init.cmd_init(None, args))
    elif args.command == 'merge':
        sys.exit(merge.cmd_merge(None, args))
    elif args.command == 'check':
        sys.exit(check.cmd_check(None, args))

    # Commands needing FeatureJSON
    manager = FeatureJSON(args.file)

    if args.command == 'tree':
        sys.exit(tree.cmd_tree(manager, args))
    elif args.command == 'view':
        sys.exit(view.cmd_view(manager, args))
    elif args.command == 'skip':
        sys.exit(skip.cmd_skip(manager, args))
    elif args.command == 'add':
        sys.exit(add.cmd_add(manager, args))
    elif args.command == 'del':
        sys.exit(delete.cmd_delete(manager, args))
    elif args.command == 'edit':
        sys.exit(edit.cmd_edit(manager, args))
    elif args.command == 'replace':
        sys.exit(edit.cmd_replace(manager, args))
    elif args.command == 'build':
        sys.exit(build.cmd_build(manager, args))
    elif args.command == 'import':
        sys.exit(import_cmd.cmd_import(manager, args))
    elif args.command == 'format':
        sys.exit(fmt.cmd_format(manager, args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
