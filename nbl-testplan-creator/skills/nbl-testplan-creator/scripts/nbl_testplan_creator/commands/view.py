"""View command: show node details."""

import json


def cmd_view(manager, args) -> int:
    manager.load()
    try:
        node = manager.find_node(args.path)
    except KeyError as e:
        print(f"错误: {e}")
        return 1

    if args.json:
        print(json.dumps(node, ensure_ascii=False, indent=2))
    else:
        print(f"--- {args.path} ---")
        for k, v in node.items():
            if isinstance(v, list):
                print(f"{k}: [{len(v)} items]")
            else:
                print(f"{k}: {v}")
    return 0
