from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class DataBridgeError(Exception):
    pass

class InterfaceReader(ABC):
    @abstractmethod
    def read(self, file: Path) -> list[dict[str, Any]]:
        pass