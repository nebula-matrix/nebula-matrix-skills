"""Add command: create features, subfeatures, or testpoints."""

from nbl_testplan_creator.core.validators import validate_priority, validate_checking


def _parse_pair(args_list: list[str]) -> dict[str, str]:
    result = {}
    for arg in args_list:
        if '=' not in arg:
            raise ValueError(f"参数格式错误: {arg}，期望 key=value")
        k, v = arg.split('=', 1)
        result[k.strip()] = v.strip()
    return result


def cmd_add(manager, args) -> int:
    manager.load()
    raw = getattr(args, 'kwargs', [])

    if args.add_type == 'feature':
        kwargs = _parse_pair(raw)
        return _add_feature(manager, kwargs)
    elif args.add_type == 'subfeature':
        if not raw:
            print("错误: add subfeature 需要 feature_id 和 key=value 参数")
            return 1
        feature_id = raw[0]
        kwargs = _parse_pair(raw[1:])
        return _add_subfeature(manager, feature_id, kwargs)
    elif args.add_type == 'tp':
        if not raw:
            print("错误: add tp 需要 path (如 f000.s000) 和 key=value 参数")
            return 1
        path = raw[0]
        kwargs = _parse_pair(raw[1:])
        return _add_tp(manager, path, kwargs)
    else:
        print("错误: 未知 add 类型")
        return 1


def _add_feature(manager, kwargs: dict) -> int:
    name = kwargs.get('feature_name') or kwargs.get('name')
    if not name:
        print("错误: 需要 feature_name=...")
        return 1

    fid = manager.next_feature_id()
    feature = {
        'feature_id': fid,
        'feature_name': name,
        'description': kwargs.get('description', ''),
        'priority': 'MID',
        'sections_covered': [],
        'skip': False,
        'sub_features': [],
    }

    if 'priority' in kwargs:
        try:
            feature['priority'] = validate_priority(kwargs['priority'])
        except ValueError as e:
            print(f"错误: {e}")
            return 1

    manager.data.setdefault('features', []).append(feature)
    manager.save()
    print(f"已添加 Feature [{fid}]: {name}")
    return 0


def _add_subfeature(manager, feature_id: str, kwargs: dict) -> int:
    try:
        feature = manager._find_feature(feature_id)
    except KeyError:
        print(f"错误: Feature 不存在: {feature_id}")
        return 1

    name = kwargs.get('sub_feature_name') or kwargs.get('description')
    if not name:
        print("错误: 需要 sub_feature_name=... 或 description=...")
        return 1

    sfid = manager.next_subfeature_id(feature_id)
    sf = {
        'sub_feature_id': sfid,
        'sub_feature_name': name,
        'description': kwargs.get('description', name),
        'spec_id': kwargs.get('spec_id', ''),
        'priority': 'MID',
        'skip': False,
        'testpoints': [],
    }

    if 'priority' in kwargs:
        try:
            sf['priority'] = validate_priority(kwargs['priority'])
        except ValueError as e:
            print(f"错误: {e}")
            return 1

    feature.setdefault('sub_features', []).append(sf)
    manager.save()
    print(f"已添加 SubFeature [{feature_id}.{sfid}]: {name}")
    return 0


def _add_tp(manager, path: str, kwargs: dict) -> int:
    parts = path.lower().split('.')
    if len(parts) != 2:
        print("错误: Testpoint 路径格式: f001.s000")
        return 1

    fid, sfid = parts[0], parts[1]
    try:
        sf = manager._find_subfeature(fid, sfid)
    except KeyError as e:
        print(f"错误: {e}")
        return 1

    tp_name = kwargs.get('tp_name')
    if not tp_name:
        print("错误: 需要 tp_name=...")
        return 1

    tp_id = manager.next_tp_id(fid, sfid)
    tp = {
        'tp_id': tp_id,
        'tp_name': tp_name,
        'source': kwargs.get('source', ''),
        'stimulus': kwargs.get('stimulus', ''),
        'checking': kwargs.get('checking', 'by_checker'),
        'coverage_requirements': kwargs.get('coverage_requirements', ''),
        'priority': 'MID',
        'category': kwargs.get('category', 'normal'),
        'path2source': kwargs.get('path2source', ''),
        'skip': False,
    }

    if 'priority' in kwargs:
        try:
            tp['priority'] = validate_priority(kwargs['priority'])
        except ValueError as e:
            print(f"错误: {e}")
            return 1
    if 'checking' in kwargs:
        try:
            tp['checking'] = validate_checking(kwargs['checking'])
        except ValueError as e:
            print(f"错误: {e}")
            return 1

    sf.setdefault('testpoints', []).append(tp)
    manager.save()
    print(f"已添加 Testpoint [{fid}.{sfid}.{tp_id}]: {tp_name}")
    return 0
