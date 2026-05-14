"""JSON data management for features."""

import json
from datetime import datetime
from pathlib import Path

from .name_encoder import encode_name


class FeatureJSON:
    """Manages the features.json lifecycle: load, save, find, ID generation."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.data: dict = {}

    def exists(self) -> bool:
        return self.path.exists()

    def load(self) -> dict:
        if not self.path.exists():
            raise FileNotFoundError(f"文件不存在: {self.path}")
        with open(self.path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        return self.data

    def save(self) -> None:
        if not self.data:
            raise RuntimeError("数据为空，未加载或初始化")
        self.data.setdefault('metadata', {})
        self.data['metadata']['modified'] = datetime.now().isoformat()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    # -- ID generation --

    def next_feature_id(self) -> str:
        features = self.data.get('features', [])
        if not features:
            return 'f000'
        max_id = max(int(f['feature_id'][1:]) for f in features)
        return f'f{max_id + 1:03d}'

    def next_subfeature_id(self, feature_id: str) -> str:
        feature = self._find_feature(feature_id)
        sfs = feature.get('sub_features', [])
        if not sfs:
            return 's000'
        max_id = max(int(sf['sub_feature_id'][1:]) for sf in sfs)
        return f's{max_id + 1:03d}'

    def next_tp_id(self, feature_id: str, subfeature_id: str) -> str:
        sf = self._find_subfeature(feature_id, subfeature_id)
        tps = sf.get('testpoints', [])
        if not tps:
            return 't000'
        max_id = max(int(tp['tp_id'][1:]) for tp in tps)
        return f't{max_id + 1:03d}'

    # -- Node lookup --

    def _find_feature(self, feature_id: str) -> dict:
        features = self.data.get('features', [])
        target = feature_id.lower()
        for f in features:
            if f['feature_id'].lower() == target:
                return f
        raise KeyError(f"Feature not found: {feature_id}")

    def _find_subfeature(self, feature_id: str, subfeature_id: str) -> dict:
        feature = self._find_feature(feature_id)
        target = subfeature_id.lower()
        for sf in feature.get('sub_features', []):
            if sf['sub_feature_id'].lower() == target:
                return sf
        raise KeyError(f"SubFeature not found: {feature_id}.{subfeature_id}")

    def find_node(self, path: str) -> dict:
        """Resolve a dot-separated path (f001 | f001.s000 | f001.s000.t000)."""
        parts = path.lower().split('.')
        feature = self._find_feature(parts[0])
        if len(parts) == 1:
            return feature
        subfeature = self._find_subfeature(parts[0], parts[1])
        if len(parts) == 2:
            return subfeature
        target = parts[2]
        for tp in subfeature.get('testpoints', []):
            if tp['tp_id'].lower() == target:
                return tp
        raise KeyError(f"Testpoint not found: {path}")

    def get_stats(self) -> dict:
        features = self.data.get('features', [])
        sf_count = sum(len(f.get('sub_features', [])) for f in features)
        tp_count = sum(
            sum(len(sf.get('testpoints', [])) for sf in f.get('sub_features', []))
            for f in features
        )
        return {'features': len(features), 'sub_features': sf_count, 'testpoints': tp_count}

    # -- Convenience for build/import --

    def find_feature_by_name(self, name: str) -> dict | None:
        """Find feature by encoded name (used in import)."""
        encoded = encode_name(name)
        for f in self.data.get('features', []):
            if encode_name(f.get('feature_name', '')) == encoded:
                return f
        return None

    def find_subfeature_by_name(self, feature: dict, name: str) -> dict | None:
        """Find subfeature under a feature by encoded name."""
        encoded = encode_name(name)
        for sf in feature.get('sub_features', []):
            if encode_name(sf.get('sub_feature_name', '')) == encoded:
                return sf
        return None
