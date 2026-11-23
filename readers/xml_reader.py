import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from readers.base import InterfaceReader, DataBridgeError

class XmlReader(InterfaceReader):
    def read(self, file_path: Path) -> list[dict[str, Any]]:
        if not file_path.exists():
            raise DataBridgeError(f"Файл не найден: {file_path}")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise DataBridgeError(f"Ошибка разбора XML в файле {file_path.name}: {e}")

        records: list[dict[str, Any]] = []
        for item in root:
            row = {child.tag: (child.text if child.text is not None else "") for child in item}
            records.append(row)

        return records