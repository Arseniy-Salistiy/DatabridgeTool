import json
from pathlib import Path
from typing import Any
from writers.base import BaseWriter

class JsonWriter(BaseWriter):
    def write(self, data: list[dict[str, Any]], file_path: Path) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, mode="w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
