import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from writers.base import BaseWriter

class XmlWriter(BaseWriter):
    def write(self, data: list[dict[str, Any]], file_path: Path) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        root = ET.Element("records")

        for row in data:
            item = ET.SubElement(root, "record")
            for key, val in row.items():
                child = ET.SubElement(item, str(key))
                child.text = "" if val is None else str(val)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(file_path, encoding="utf-8", xml_declaration=True)