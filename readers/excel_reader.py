from pathlib import Path
from typing import Any
import openpyxl
from readers.base import InterfaceReader, DataBridgeError

class ExcelReader(InterfaceReader):
    def read(self, file_path: Path) -> list[dict[str, Any]]:
        if not file_path.exists():
            raise DataBridgeError(f"Файл не найден: {file_path}")

        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
        except Exception as e:
            raise DataBridgeError(f"Ошибка чтения Excel-файла {file_path.name}: {e}")

        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return []

        headers = [str(h).strip() if h is not None else f"col_{i}" for i, h in enumerate(rows[0])]
        records: list[dict[str, Any]] = []

        for row in rows[1:]:
            if all(cell is None for cell in row):
                continue
            record = {
                headers[i]: (row[i] if i < len(row) and row[i] is not None else "")
                for i in range(len(headers))
            }
            records.append(record)

        return records