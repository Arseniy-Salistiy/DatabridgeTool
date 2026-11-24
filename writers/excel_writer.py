from pathlib import Path
from typing import Any
import openpyxl
from writers.base import BaseWriter

class ExcelWriter(BaseWriter):
    def write(self, data: list[dict[str, Any]], file_path: Path) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        wb = openpyxl.Workbook()
        ws = wb.active

        if data:
            headers = list(data[0].keys())
            ws.append(headers)
            for row in data:
                ws.append([row.get(h, "") for h in headers])

        wb.save(file_path)