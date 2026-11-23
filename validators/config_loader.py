import json
from pathlib import Path
from typing import Any
import yaml
from readers.base import DataBridgeError

def load_config(config_path: Path):
    if not config_path.exists():
        raise DataBridgeError(f"Файл конфигурации не найден: {config_path}")

    e = config_path.suffix.lower()
    try:
        with open(config_path, mode="r", encoding="utf-8-sig") as f:
            if e in ('.yaml', '.yml'):
                config = yaml.safe_load(f)
            elif e == '.json':
                config = json.load(f)
            else:
                raise DataBridgeError(f"Неподдерживаемый формат конфига: '{e}'")
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise DataBridgeError(f"Ошибка синтаксиса в файле конфигурации {config_path.name}: {e}")

    if not isinstance(config, dict) or "fields" not in config or not isinstance(config["fields"], list):
        raise DataBridgeError(f"Некорректная структура конфига {config_path.name}")

    return config