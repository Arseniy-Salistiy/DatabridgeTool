import re
from dataclasses import dataclass
from datetime import datetime, date
from typing import Any

@dataclass(frozen=True)
class ValidationError:
    row_number: int
    field_name: str
    invalid_value: Any
    message: str

class DataValidator:
    def __init__(self, config: dict[str, Any]):
        self.rules: list[dict[str, Any]] = config.get("fields", [])
    
    def validate(self, rows: list[dict[str, Any]]):
        valid_rows: list[dict[str, Any]] = []
        invalid_rows: list[dict[str, Any]] = []
        all_errors: list[ValidationError] = []

        seen_values: dict[str, set[Any]] = {
            rule["name"]: set() for rule in self.rules if rule.get("unique")
        }

        for idx, row in enumerate(rows, start=1):
            row_errors: list[ValidationError] = []

            for rule in self.rules:
                field = rule["name"]
                raw_value = row.get(field)
                is_empty = raw_value is None or str(raw_value).strip() == ""

                if is_empty:
                    if rule.get("required"):
                        row_errors.append(ValidationError(idx, field, raw_value, f"поле \"{field}\" обязательно для заполнения"))
                    continue

                expected_type = rule.get("type", "string")
                date_format = rule.get("format", "YYYY-MM-DD")
                ok, typed_value, type_err = self._check_type(raw_value, expected_type, date_format)

                if not ok:
                    row_errors.append(ValidationError(idx, field, raw_value, f"поле \"{field}\" {type_err} ({raw_value})"))
                    continue

                if "min" in rule or "max" in rule:
                    range_err = self._check_range(typed_value, rule.get("min"), rule.get("max"), expected_type, date_format)
                    if range_err:
                        row_errors.append(ValidationError(idx, field, raw_value, f"поле \"{field}\" {range_err} ({raw_value})"))

                str_val = str(raw_value)
                if "min_length" in rule and len(str_val) < rule["min_length"]:
                    row_errors.append(ValidationError(idx, field, raw_value, f"поле \"{field}\" короче {rule['min_length']} символов"))
                if "max_length" in rule and len(str_val) > rule["max_length"]:
                    row_errors.append(ValidationError(idx, field, raw_value, f"поле \"{field}\" длиннее {rule['max_length']} символов"))

                if "pattern" in rule:
                    if not re.match(rule["pattern"], str_val):
                        row_errors.append(ValidationError(idx, field, raw_value, f"поле \"{field}\" не соответствует формату"))

                if rule.get("unique"):
                    if typed_value in seen_values[field]:
                        row_errors.append(ValidationError(idx, field, raw_value, f"поле \"{field}\" должно быть уникальным (дубликат: {raw_value})"))
                    else:
                        seen_values[field].add(typed_value)

            if row_errors:
                invalid_rows.append(row)
                all_errors.extend(row_errors)
            else:
                valid_rows.append(row)

        return valid_rows, invalid_rows, all_errors

    def _check_type(self, value: Any, expected_type: str, date_format: str) -> tuple[bool, Any, str]:
        str_val = str(value).strip()

        if expected_type == "string":
            return True, str_val, ""

        elif expected_type == "integer":
            try:
                if isinstance(value, float) and not value.is_integer():
                    return False, None, "должно быть целым числом"
                return True, int(str_val), ""
            except ValueError:
                return False, None, "должно быть целым числом"

        elif expected_type == "float":
            try:
                return True, float(str_val.replace(",", ".")), ""
            except ValueError:
                return False, None, "должно быть дробным числом"

        elif expected_type == "boolean":
            low = str_val.lower()
            if low in ("true", "1", "yes", "да"):
                return True, True, ""
            if low in ("false", "0", "no", "нет"):
                return True, False, ""
            return False, None, "должно быть логическим значением (true/false)"

        elif expected_type == "date":
            if isinstance(value, (date, datetime)):
                return True, value.date() if isinstance(value, datetime) else value, ""
            py_fmt = self._convert_date_format(date_format)
            try:
                parsed_date = datetime.strptime(str_val, py_fmt).date()
                return True, parsed_date, ""
            except ValueError:
                return False, None, f"не соответствует формату даты {date_format}"

        return True, value, ""

    def _check_range(self, typed_val: Any, min_val: Any, max_val: Any, expected_type: str, date_format: str) -> str:
        if expected_type == "date":
            py_fmt = self._convert_date_format(date_format)
            if isinstance(min_val, str):
                min_val = datetime.strptime(min_val, py_fmt).date()
            if isinstance(max_val, str):
                max_val = datetime.strptime(max_val, py_fmt).date()

        if min_val is not None and typed_val < min_val:
            return "вне диапазона"
        if max_val is not None and typed_val > max_val:
            return "вне диапазона"
        return ""

    @staticmethod
    def _convert_date_format(user_fmt: str) -> str:
        return (
            user_fmt.replace("YYYY", "%Y")
            .replace("MM", "%m")
            .replace("DD", "%d")
        )