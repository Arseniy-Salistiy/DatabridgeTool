import csv
from pathlib import Path
from typing import Any
from readers.base import InterfaceReader, DataBridgeError

class CsvReader(InterfaceReader):
    def __init__(self, delimiter: str = ",", has_headers: bool = True):
        self.delimiter = delimiter
        self.has_headers = has_headers

    def read(self, file_path: Path) -> list[dict[str, Any]]:
        if not file_path.exists():
            raise DataBridgeError(f"Файл {file_path} не найден")

        records: list[dict[str, Any]] = []
        try:
            with open(file_path, mode='r', encoding="utf-8-sig", newline="") as f:
                reader = csv.reader(f, delimiter=self.delimiter)
                first_row = next(reader, None)

                if first_row is None:
                    return records

                if self.has_headers:
                    headers = [i.strip() for i in first_row]
                else:
                    headers = [f"колонка_{i}" for i in range(len(first_row))]
                    records.append(self._map_row(headers, first_row))

                for row in reader:
                    if not row:
                        continue
                    records.append(self._map_row(headers, row))
            
        except csv.Error as e:
            raise DataBridgeError(f"Ошибка формата CSV в файле {file_path.name}: {e}")
        except UnicodeDecodeError:
            raise DataBridgeError(f"Неверная кодировка файла {file_path.name} (ожидается UTF-8)")

        return records
    
    def _map_row(self, headers: list[str], values: list[str]) -> dict[str, Any]:
        return {
            headers[i]: (values[i] if i < len(values) else "")
            for i in range(len(headers))
        }