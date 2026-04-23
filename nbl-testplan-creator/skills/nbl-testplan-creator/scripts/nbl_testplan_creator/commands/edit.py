"""Edit and replace commands: modify node fields."""

from nbl_testplan_creator.core.validators import validate_priority, validate_checking, parse_sections, parse_bool


def _parse_pair(args_list: list[str]) -> dict[str, str]:
    result = {}
    for arg in args_list:
        if '=' not in arg:
            raise ValueError(f"参数格式错误: {arg}")
        k, v = arg.split('=', 1)
        result[k.strip()] = v.strip()
    return result


def cmd_edit(manager, args) -> int:
    manager.load()
    try:
        node = manager.find_node(args.path)
    except KeyError as e:
        print(f"错误: {e}")
        return 1

    kwargs = _parse_pair(getattr(args, 'kwargs', []))

    if getattr(args, 'replace', False):
        _do_replace(node, kwargs)
    else:
        _do_edit(node, kwargs)

    manager.save()
    print(f"已更新: {args.path}")
    return 0


def _do_edit(node: dict, kwargs: dict) -> None:
    for k, v in kwargs.items():
        if k == 'priority':
            node[k] = validate_priority(v)
        elif k == 'checking':
            node[k] = validate_checking(v)
        elif k == 'sections_covered':
            node[k] = parse_sections(v)
        elif k == 'skip':
            node[k] = parse_bool(v)
        else:
            node[k] = v


def _do_replace(node: dict, kwargs: dict) -> None:
    for key in list(node.keys()):
        if key not in ('feature_id', 'sub_feature_id', 'tp_id'):
            del node[key]
    _do_edit(node, kwargs)


def cmd_replace(manager, args) -> int:
    args.replace = True
    return cmd_edit(manager, args)
