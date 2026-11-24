from pathlib import Path
from typing import Optional
from validators.validator import ValidationError

def print_summary(
    total: int,
    valid_count: int,
    errors: list[ValidationError],
    output_path: Optional[Path] = None,
    errors_csv_path: Optional[Path] = None,
    report_html_path: Optional[Path] = None,
) -> None:
    invalid_rows_count = len({err.row_number for err in errors})

    print(f"Всего записей: {total}")
    print(f"Успешно обработано: {valid_count}")
    print(f"Ошибок: {invalid_rows_count}")

    for err in errors:
        print(f"  - Строка {err.row_number}: {err.message}")

    if output_path:
        print(f"Результат сохранён: {output_path}")
    if errors_csv_path and invalid_rows_count > 0:
        print(f"Ошибки сохранены: {errors_csv_path}")
    if report_html_path:
        print(f"Отчёт сохранён: {report_html_path}")
