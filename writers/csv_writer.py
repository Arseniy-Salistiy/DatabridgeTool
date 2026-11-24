import csv
from pathlib import Path
from typing import Any
from writers.base import BaseWriter

class CsvWriter(BaseWriter):
    def __init__(self, delimiter: str = ","):
        self.delimiter = delimiter

    def write(self, data: list[dict[str, Any]], file_path: Path) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not data:
            file_path.write_text("", encoding="utf-8")
            return

        headers = list(data[0].keys())
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=self.delimiter, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(data)
