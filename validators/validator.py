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
    