# 安装指南

## 前置要求

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) 包管理工具

## 有网环境安装

进入 `nbl-testplan-creator/scripts/` 目录执行：

```bash
cd nbl-testplan-creator/scripts
uv tool install -e .
```

安装完成后，`nbl-testplan` 命令全局可用：

```bash
nbl-testplan --version
```

## 离线环境安装

项目已预置所有依赖的 whl 包于 `offline-packages/` 目录，支持完全离线安装：

```bash
cd nbl-testplan-creator/scripts
uv tool install -e --offline . --find-links offline-packages/
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `-e`, `--editable` | 以 editable 模式安装，修改脚本后无需重新安装即可生效 |
| `--offline` | 禁止网络访问，完全使用本地包 |
| `--find-links` | 指定本地 whl 包目录，uv 会从中查找并安装依赖 |

### 离线包清单

`offline-packages/` 目录包含以下预下载的 whl 包：

- `openpyxl-3.1.5-py2.py3-none-any.whl`
- `et_xmlfile-2.0.0-py3-none-any.whl`
- `hatchling-1.29.0-py3-none-any.whl`（构建后端）
- `packaging-26.2-py3-none-any.whl`
- `pathspec-1.1.1-py3-none-any.whl`
- `pluggy-1.6.0-py3-none-any.whl`
- `trove_classifiers-2026.5.7.17-py3-none-any.whl`

### 验证安装

```bash
nbl-testplan --version
nbl-testplan --help
```

## 更新离线包

如需更新依赖版本或添加新依赖：

1. 修改 `pyproject.toml`
2. 重新生成 `uv.lock`：`uv lock`
3. 重新下载 whl：`pip download -d offline-packages/ -r pyproject.toml`
4. 提交更新后的 `uv.lock` 和 `offline-packages/` 目录
