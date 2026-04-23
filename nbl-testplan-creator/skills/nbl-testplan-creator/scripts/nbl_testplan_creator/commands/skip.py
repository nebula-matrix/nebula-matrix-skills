"""Skip command: toggle skip flag on a node."""


def cmd_skip(manager, args) -> int:
    manager.load()
    try:
        node = manager.find_node(args.path)
    except KeyError as e:
        print(f"错误: {e}")
        return 1

    target = not getattr(args, 'unskip', False)
    node['skip'] = target
    manager.save()
    action = "跳过" if target else "取消跳过"
    print(f"{action}: {args.path}")
    return 0
