"""from pathlib import Path
from readers.factory import get_reader
from readers.base import DataBridgeError

test_files = [
    Path("samples/test.csv"),
    Path("samples/test.json"),
    Path("samples/test.xml"),
    Path("samples/test.xlsx"),
    Path("samples/non_existent.csv"),
]

for file_path in test_files:
    try:
        reader = get_reader(file_path)
        rows = reader.read(file_path)
        for row in rows:
            print(row)
    except DataBridgeError as e:
        print(f"Поймана ошибка: {e}")
"""

from cli.main import cli

if __name__ == "__main__":
    cli()
