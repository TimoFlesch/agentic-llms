import json
import typing
from pathlib import Path

import toml


def load_json(file_path: typing.Union[str, Path]) -> dict:
    file_path = Path(file_path)
    assert file_path.suffix == ".json"
    with open(file_path, "r") as f:
        loaded_file = json.load(f)
    return loaded_file


def save_json(file: typing.Dict, file_path: typing.Union[str, Path]):
    file_path = Path(file_path)
    assert file_path.suffix == ".json"
    with open(file_path, "w") as f:
        json.dump(file, f)


def load_toml(file_path: typing.Union[str, Path]) -> dict:
    file_path = Path(file_path)
    assert file_path.suffix == ".toml"
    return toml.load(file_path)


def save_toml(file: typing.Dict, file_path: typing.Union[str, Path]):
    file_path = Path(file_path)
    assert file_path.suffix == ".toml"
    with open(file_path, "w") as f:
        toml.dump(file, f)


def load_config(
    file_path: typing.Union[str, Path],
) -> dict:
    file_path = Path(file_path)
    if file_path.suffix == ".json":
        cfg = load_json(file_path)
    elif file_path.suffix == ".toml":
        cfg = load_toml(file_path)
    else:
        raise ValueError(f"unsupported file format: {file_path.suffix}")
    return cfg


def save_config(
    cfg: dict,
    config_name: str = "default_config.toml",
    config_dir: str = "./configs/",
):
    Path(config_dir).mkdir(parents=True, exist_ok=True)

    file_path = Path(config_dir) / config_name

    if file_path.suffix == ".json":
        save_json(cfg, file_path)
    elif file_path.suffix == ".toml":
        save_toml(cfg, file_path)
    else:
        raise ValueError(f"unsupported file format: {file_path.suffix}")
    return cfg
