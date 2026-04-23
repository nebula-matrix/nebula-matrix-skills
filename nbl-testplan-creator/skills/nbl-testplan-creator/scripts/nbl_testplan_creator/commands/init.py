"""Init command: create a new features.json file."""

import json
import shutil
from datetime import datetime
from pathlib import Path


def cmd_init(_manager, args) -> int:
    path = Path(args.file)
    if path.exists():
        bk = path.with_suffix(path.suffix + '.bk')
        if bk.exists():
            old = path.with_suffix(path.suffix + '.old')
            if old.exists():
                ts = datetime.now().strftime('%Y%m%d-%H%M%S')
                bk = path.with_suffix(path.suffix + f'.bk.{ts}')
            else:
                shutil.move(str(bk), str(old))
        shutil.copy2(path, bk)
        print(f"已备份旧文件: {bk}")

    data = {
        "document_title": args.title,
        "metadata": {
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "version": "1.0.0",
        },
        "features": [],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已初始化: {path}")
    return 0
