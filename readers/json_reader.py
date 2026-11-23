import json
from pathlib import Path
from typing import Any
from readers.base import InterfaceReader, DataBridgeError

class JsonReader(InterfaceReader):
    def read(self, file_path: Path) -> list[dict[str, Any]]:
        if not file_path.exists():
            raise DataBridgeError(f"Файл {file_path} не найден")

        records: list[dict[str, Any]] = []
        try:
            with open(file_path, mode='r', encoding="utf-8-sig") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataBridgeError(f"Невалидный JSON в файле {file_path.name}: {e.msg} (строка {e.lineno})")
        except UnicodeDecodeError:
            raise DataBridgeError(f"Неверная кодировка файла {file_path.name} (ожидается UTF-8)")

        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise DataBridgeError(f"Файл {file_path.name} должен содержать массив JSON-объектов")

        return data