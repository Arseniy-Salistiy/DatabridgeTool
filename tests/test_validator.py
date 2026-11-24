from pathlib import Path
import pytest
from validators.validator import DataValidator
from validators.config_loader import load_config
from readers.base import DataBridgeError


def test_valid_record_passes():
    config = {"fields": [{"name": "id", "type": "integer", "required": True}, {"name": "age", "type": "integer", "min": 16, "max": 100}]}
    rows = [{"id": "1", "age": "25"}]
    valid, invalid, errors = DataValidator(config).validate(rows)
    assert len(valid) == 1
    assert len(invalid) == 0
    assert len(errors) == 0


def test_required_field_empty_or_none():
    config = {"fields": [{"name": "name", "type": "string", "required": True}]}
    rows = [{"name": ""}, {"name": "   "}, {"name": None}]
    valid, invalid, errors = DataValidator(config).validate(rows)
    assert len(valid) == 0
    assert len(invalid) == 3
    assert len(errors) == 3


def test_optional_field_empty_skips_other_checks():
    config = {"fields": [{"name": "email", "type": "string", "required": False, "pattern": "^[^@]+@[^@]+\\.[^@]+$"}]}
    rows = [{"email": ""}]
    valid, invalid, errors = DataValidator(config).validate(rows)
    assert len(valid) == 1
    assert len(errors) == 0


@pytest.mark.parametrize("field_type,bad_val", [
    ("integer", "abc"),
    ("integer", "12.5"),
    ("float", "not_a_float"),
    ("boolean", "maybe"),
    ("date", "2026-99-99"),
])
def test_invalid_types(field_type, bad_val):
    config = {"fields": [{"name": "val", "type": field_type, "format": "YYYY-MM-DD"}]}
    valid, invalid, errors = DataValidator(config).validate([{"val": bad_val}])
    assert len(valid) == 0
    assert len(errors) == 1


@pytest.mark.parametrize("age,expected_valid", [
    ("16", True),    # нижняя граница
    ("100", True),   # верхняя граница
    ("15", False),   # меньше минимума
    ("101", False),  # больше максимума
])
def test_numeric_range_boundaries(age, expected_valid):
    config = {"fields": [{"name": "age", "type": "integer", "min": 16, "max": 100}]}
    valid, invalid, _ = DataValidator(config).validate([{"age": age}])
    assert (len(valid) == 1) == expected_valid


def test_string_length_boundaries():
    config = {"fields": [{"name": "code", "type": "string", "min_length": 3, "max_length": 5}]}
    rows = [{"code": "ab"}, {"code": "abc"}, {"code": "abcde"}, {"code": "abcdef"}]
    valid, invalid, _ = DataValidator(config).validate(rows)
    assert len(valid) == 2
    assert len(invalid) == 2


def test_regex_pattern():
    config = {"fields": [{"name": "email", "type": "string", "pattern": "^[^@]+@[^@]+\\.[^@]+$"}]}
    rows = [{"email": "good@test.ru"}, {"email": "bad.test.ru"}]
    valid, invalid, _ = DataValidator(config).validate(rows)
    assert len(valid) == 1
    assert len(invalid) == 1


def test_unique_constraint():
    config = {"fields": [{"name": "id", "type": "integer", "unique": True}]}
    rows = [{"id": "1"}, {"id": "2"}, {"id": "1"}, {"id": "02"}]
    valid, invalid, errors = DataValidator(config).validate(rows)
    assert len(valid) == 2
    assert len(invalid) == 2
    assert "дубликат" in errors[0].message


def test_date_range():
    config = {"fields": [{"name": "dt", "type": "date", "format": "YYYY-MM-DD", "min": "2000-01-01", "max": "2020-12-31"}]}
    rows = [{"dt": "2010-05-05"}, {"dt": "1995-01-01"}]
    valid, invalid, _ = DataValidator(config).validate(rows)
    assert len(valid) == 1
    assert len(invalid) == 1


def test_invalid_config_raises_error(tmp_path: Path):
    bad_cfg = tmp_path / "bad.yaml"
    bad_cfg.write_text("wrong_root: 123", encoding="utf-8")
    with pytest.raises(DataBridgeError):
        load_config(bad_cfg)
