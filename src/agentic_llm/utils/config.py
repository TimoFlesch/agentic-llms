import json
from pathlib import Path


def load_config(
    config_name: str = "default_config",
    config_dir: str = "./configs/",
) -> dict:
    if not config_name.endswith(".json"):
        config_name = config_name + ".json"
    with open(Path(config_dir) / config_name, "r") as f:
        cfg = json.load(f)
    return cfg


def save_config(
    cfg: dict,
    config_name: str = "default_config",
    config_dir: str = "./configs/",
):
    Path(config_dir).mkdir(parents=True, exist_ok=True)
    if not config_name.endswith(".json"):
        config_name = config_name + ".json"
    with open(Path(config_dir) / config_name, "w") as f:
        json.dump(cfg, f)
