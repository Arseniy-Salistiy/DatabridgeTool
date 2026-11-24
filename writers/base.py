from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class BaseWriter(ABC):
    @abstractmethod
    def write(self, data: list[dict[str, Any]], file_path: Path) -> None:
        pass
