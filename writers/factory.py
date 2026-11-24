from pathlib import Path
from readers.base import DataBridgeError
from writers.base import BaseWriter
from writers.csv_writer import CsvWriter
from writers.json_writer import JsonWriter
from writers.xml_writer import XmlWriter
from writers.excel_writer import ExcelWriter

def get_writer(file_path: Path, delimiter: str = ",") -> BaseWriter:
    ext = file_path.suffix.lower()

    if ext == ".csv":
        return CsvWriter(delimiter=delimiter)
    elif ext == ".json":
        return JsonWriter()
    elif ext == ".xml":
        return XmlWriter()
    elif ext == ".xlsx":
        return ExcelWriter()
    else:
        raise DataBridgeError(f"Неподдерживаемый формат выходного файла: '{ext}'. Доступны: .csv, .json, .xml, .xlsx")
