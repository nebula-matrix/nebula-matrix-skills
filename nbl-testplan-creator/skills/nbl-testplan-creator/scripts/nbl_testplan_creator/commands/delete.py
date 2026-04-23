"""Delete command: remove nodes by path."""


def cmd_delete(manager, args) -> int:
    manager.load()
    parts = args.path.lower().split('.')

    if len(parts) == 1:
        feature_id = parts[0]
        for i, f in enumerate(manager.data['features']):
            if f['feature_id'].lower() == feature_id:
                if not args.force:
                    sfs = len(f.get('sub_features', []))
                    tps = sum(len(sf.get('testpoints', [])) for sf in f.get('sub_features', []))
                    print(f"将删除 Feature [{feature_id}], 包含 {sfs} SubFeatures, {tps} Testpoints")
                    print("加 --force 确认删除")
                    return 1
                manager.data['features'].pop(i)
                manager.save()
                print(f"已删除 Feature [{feature_id}]")
                return 0
        print(f"错误: Feature 不存在: {feature_id}")
        return 1

    elif len(parts) == 2:
        feature_id, subfeature_id = parts
        try:
            feature = manager._find_feature(feature_id)
        except KeyError:
            print(f"错误: Feature 不存在: {feature_id}")
            return 1
        sfs = feature.get('sub_features', [])
        for i, sf in enumerate(sfs):
            if sf['sub_feature_id'].lower() == subfeature_id:
                if not args.force:
                    tps = len(sf.get('testpoints', []))
                    print(f"将删除 SubFeature [{args.path}], 包含 {tps} Testpoints")
                    print("加 --force 确认删除")
                    return 1
                sfs.pop(i)
                manager.save()
                print(f"已删除 SubFeature [{args.path}]")
                return 0
        print(f"错误: SubFeature 不存在: {args.path}")
        return 1

    elif len(parts) == 3:
        feature_id, subfeature_id, tp_id = parts
        try:
            sf = manager._find_subfeature(feature_id, subfeature_id)
        except KeyError:
            print(f"错误: 路径不存在: {args.path}")
            return 1
        tps = sf.get('testpoints', [])
        for i, tp in enumerate(tps):
            if tp['tp_id'].lower() == tp_id:
                tps.pop(i)
                manager.save()
                print(f"已删除 Testpoint [{args.path}]")
                return 0
        print(f"错误: Testpoint 不存在: {args.path}")
        return 1

    else:
        print("错误: 路径格式: f001 | f001.s000 | f001.s000.t000")
        return 1
