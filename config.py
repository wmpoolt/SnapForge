import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".smart-screenshot.json"
DEFAULT_SAVE_DIR = str(Path.home() / "Screenshots")


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_save_dir():
    return Path(load_config().get("save_dir", DEFAULT_SAVE_DIR))


def set_save_dir(path):
    cfg = load_config()
    cfg["save_dir"] = str(path)
    save_config(cfg)
