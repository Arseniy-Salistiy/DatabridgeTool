from pathlib import Path
from readers.csv_reader import CsvReader
from readers.xml_reader import XmlReader
from readers.excel_reader import ExcelReader
from readers.json_reader import JsonReader
from readers.base import DataBridgeError

def get_reader(file_path: Path, delimiter: str = ",", has_headers: bool = True):
    e = file_path.suffix.lower()

    if e == ".csv":
        return CsvReader(delimiter, has_headers)
    elif e == ".json":
        return JsonReader()
    elif e == ".xlsx":
        return ExcelReader()
    elif e == ".xml":
        return XmlReader()
    else:
        raise DataBridgeError("Неподдерживаемый формат файла")