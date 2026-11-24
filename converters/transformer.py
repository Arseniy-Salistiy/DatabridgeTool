from datetime import datetime, timezone
from typing import Any


class DataTransformer:
    def __init__(self, config: dict[str, Any]):
        self.rules_by_name: dict[str, dict[str, Any]] = {
            rule["name"]: rule for rule in config.get("fields", [])
        }

    def transform(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        transformed_rows: list[dict[str, Any]] = []

        for row in rows:
            new_row: dict[str, Any] = {}

            for key, value in row.items():
                rule = self.rules_by_name.get(key)

                if not rule:
                    new_row[key] = value
                    continue

                transform_type = rule.get("transform")
                if transform_type and value is not None and str(value) != "":
                    value = self._apply_transform(value, transform_type, rule)

                target_key = rule.get("rename_to") or key
                new_row[target_key] = value

            transformed_rows.append(new_row)

        return transformed_rows

    def _apply_transform(self, value: Any, transform_type: str, rule: dict[str, Any]) -> Any:
        if transform_type == "trim":
            return str(value).strip()

        elif transform_type == "upper":
            return str(value).upper()

        elif transform_type == "lower":
            return str(value).lower()

        elif transform_type == "replace":
            replace_map = rule.get("replace_map", {})
            return replace_map.get(str(value), value)

        elif transform_type == "timestamp_to_date":
            try:
                ts = float(value)
                date_fmt = rule.get("format", "YYYY-MM-DD").replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d")
                return datetime.fromtimestamp(ts, tz=timezone.utc).strftime(date_fmt)
            except (ValueError, TypeError, OSError):
                return value

        return value
