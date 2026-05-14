"""Tree command: display feature hierarchy."""


def cmd_tree(manager, args) -> int:
    manager.load()
    features = manager.data.get('features', [])
    if not features:
        print("没有 Feature")
        return 0

    for f in features:
        if f.get('skip') and not args.show_skip:
            continue
        skip_mark = " [SKIP]" if f.get('skip') else ""
        print(f"[{f['feature_id']}] {f.get('feature_name', '')}{skip_mark}")
        for sf in f.get('sub_features', []):
            if sf.get('skip') and not args.show_skip:
                continue
            sf_mark = " [SKIP]" if sf.get('skip') else ""
            print(f"    -- [{sf['sub_feature_id']}] {sf.get('sub_feature_name', '')}{sf_mark}")
            for tp in sf.get('testpoints', []):
                if tp.get('skip') and not args.show_skip:
                    continue
                tp_mark = " [SKIP]" if tp.get('skip') else ""
                print(f"        -- [{tp['tp_id']}] {tp.get('tp_name', '')}{tp_mark}")
    return 0
