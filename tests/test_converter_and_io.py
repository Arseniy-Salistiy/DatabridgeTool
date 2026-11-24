from pathlib import Path
import pytest
from converters.transformer import DataTransformer
from readers.factory import get_reader
from writers.factory import get_writer
from readers.base import DataBridgeError


def test_mapping_and_transformations():
    config = {
        "fields": [
            {"name": "raw_name", "rename_to": "full_name", "transform": "trim"},
            {"name": "email", "transform": "lower"},
            {"name": "role", "transform": "upper"},
            {"name": "gender", "transform": "replace", "replace_map": {"M": "Мужской", "F": "Женский"}},
            {"name": "ts", "rename_to": "date", "transform": "timestamp_to_date", "format": "YYYY-MM-DD"},
        ]
    }
    rows = [{"raw_name": "  Иван  ", "email": "TEST@MAIL.RU", "role": "admin", "gender": "M", "ts": 1700000000}]
    res = DataTransformer(config).transform(rows)

    assert res[0]["full_name"] == "Иван"
    assert res[0]["email"] == "test@mail.ru"
    assert res[0]["role"] == "ADMIN"
    assert res[0]["gender"] == "Мужской"
    assert res[0]["date"] == "2023-11-14"


@pytest.mark.parametrize("ext", [".csv", ".json", ".xml", ".xlsx"])
def test_read_write_all_formats(tmp_path: Path, ext: str):
    file_path = tmp_path / f"data{ext}"
    sample = [{"id": "1", "name": "Анна"}, {"id": "2", "name": "Олег"}]

    writer = get_writer(file_path)
    writer.write(sample, file_path)

    reader = get_reader(file_path)
    loaded = reader.read(file_path)

    assert len(loaded) == 2
    assert str(loaded[0]["id"]) == "1"
    assert loaded[0]["name"] == "Анна"


def test_csv_without_headers_and_custom_delimiter(tmp_path: Path):
    csv_file = tmp_path / "no_headers.csv"
    csv_file.write_text("1;Иван;25\n2;Мария;30\n", encoding="utf-8")

    reader = get_reader(csv_file, delimiter=";", has_headers=False)
    rows = reader.read(csv_file)

    assert len(rows) == 2
    assert rows[0] == {"колонка_0": "1", "колонка_1": "Иван", "колонка_2": "25"}


def test_unsupported_extension_raises_error(tmp_path: Path):
    txt_file = tmp_path / "data.txt"
    txt_file.write_text("hello", encoding="utf-8")
    with pytest.raises(DataBridgeError):
        get_reader(txt_file)


def test_corrupted_json_raises_error(tmp_path: Path):
    bad_json = tmp_path / "broken.json"
    bad_json.write_text('[{"id": 1, broken]', encoding="utf-8")
    with pytest.raises(DataBridgeError):
        get_reader(bad_json).read(bad_json)
