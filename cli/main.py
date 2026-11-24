import sys
from pathlib import Path
from typing import Optional
import click

from readers.base import DataBridgeError
from readers.factory import get_reader
from writers.factory import get_writer
from validators.config_loader import load_config
from validators.validator import DataValidator
from converters.transformer import DataTransformer
from reporters.console import print_summary
from reporters.html_reporter import generate_html_report

@click.group()
def cli():
    pass

@cli.command()
@click.argument("input_file", type=click.Path(path_type=Path))
@click.option("--to", "target_format", required=False, help="Целевой формат (csv, json, xml, xlsx).")
@click.option("--config", "config_path", type=click.Path(path_type=Path), required=False, help="Путь к файлу правил (YAML/JSON).")
@click.option("--output", "output_path", type=click.Path(path_type=Path), required=False, help="Путь к выходному файлу.")
@click.option("--errors", "errors_path", type=click.Path(path_type=Path), default=Path("errors.csv"), show_default=True, help="Файл для некорректных записей.")
@click.option("--report", "report_path", type=click.Path(path_type=Path), default=Path("report.html"), show_default=True, help="Путь к HTML-отчёту.")
@click.option("--delimiter", default=",", show_default=True, help="Разделитель для CSV.")
@click.option("--no-headers", is_flag=True, default=False, help="Указать, если в CSV нет строки заголовков.")
def convert(
    input_file: Path,
    target_format: Optional[str],
    config_path: Optional[Path],
    output_path: Optional[Path],
    errors_path: Path,
    report_path: Path,
    delimiter: str,
    no_headers: bool,
):
    try:
        if not output_path:
            if not target_format:
                raise DataBridgeError("Укажите либо --output <файл>, либо --to <формат>.")
            ext = target_format.lower().lstrip(".")
            output_path = input_file.with_suffix(f".{ext}")

        reader = get_reader(input_file, delimiter=delimiter, has_headers=not no_headers)
        rows = reader.read(input_file)

        if config_path:
            config = load_config(config_path)
            valid_rows, invalid_rows, errors = DataValidator(config).validate(rows)
            processed_rows = DataTransformer(config).transform(valid_rows)
        else:
            valid_rows = rows
            invalid_rows = []
            errors = []
            processed_rows = rows

        writer = get_writer(output_path, delimiter=delimiter)
        writer.write(processed_rows, output_path)

        saved_errors_path = None
        if invalid_rows:
            get_writer(errors_path, delimiter=delimiter).write(invalid_rows, errors_path)
            saved_errors_path = errors_path

        generate_html_report(len(rows), len(valid_rows), len(invalid_rows), errors, report_path)
        print_summary(
            total=len(rows),
            valid_count=len(valid_rows),
            errors=errors,
            output_path=output_path,
            errors_csv_path=saved_errors_path,
            report_html_path=report_path,
        )

    except DataBridgeError as e:
        click.secho(f"Ошибка: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(path_type=Path))
@click.option("--config", "config_path", type=click.Path(path_type=Path), required=True, help="Путь к файлу правил (YAML/JSON).")
@click.option("--report", "report_path", type=click.Path(path_type=Path), default=Path("report.html"), show_default=True, help="Путь к HTML-отчёту.")
@click.option("--errors", "errors_path", type=click.Path(path_type=Path), default=Path("errors.csv"), show_default=True, help="Файл для некорректных записей.")
@click.option("--delimiter", default=",", show_default=True, help="Разделитель для CSV.")
@click.option("--no-headers", is_flag=True, default=False, help="Указать, если в CSV нет строки заголовков.")
def validate(
    input_file: Path,
    config_path: Path,
    report_path: Path,
    errors_path: Path,
    delimiter: str,
    no_headers: bool,
):
    try:
        reader = get_reader(input_file, delimiter=delimiter, has_headers=not no_headers)
        rows = reader.read(input_file)
        config = load_config(config_path)

        valid_rows, invalid_rows, errors = DataValidator(config).validate(rows)

        saved_errors_path = None
        if invalid_rows:
            get_writer(errors_path, delimiter=delimiter).write(invalid_rows, errors_path)
            saved_errors_path = errors_path

        generate_html_report(len(rows), len(valid_rows), len(invalid_rows), errors, report_path)
        print_summary(
            total=len(rows),
            valid_count=len(valid_rows),
            errors=errors,
            errors_csv_path=saved_errors_path,
            report_html_path=report_path,
        )

        if invalid_rows:
            sys.exit(1)

    except DataBridgeError as e:
        click.secho(f"Ошибка: {e}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(path_type=Path))
@click.option("--delimiter", default=",", show_default=True, help="Разделитель для CSV.")
@click.option("--no-headers", is_flag=True, default=False, help="Указать, если в CSV нет строки заголовков.")
def stats(input_file: Path, delimiter: str, no_headers: bool):
    """Выводит базовую статистику по файлу (строки, колонки, пустые значения)."""
    try:
        reader = get_reader(input_file, delimiter=delimiter, has_headers=not no_headers)
        rows = reader.read(input_file)

        print(f"Файл: {input_file}")
        print(f"Всего записей: {len(rows)}")

        if not rows:
            return

        columns = list(rows[0].keys())
        print(f"Колонок: {len(columns)} ({', '.join(columns)})")
        print("\nСтатистика по колонкам:")
        for col in columns:
            empty_count = sum(1 for r in rows if r.get(col) is None or str(r.get(col)).strip() == "")
            filled_count = len(rows) - empty_count
            print(f"  - {col}: заполнено {filled_count}, пустых {empty_count}")

    except DataBridgeError as e:
        click.secho(f"Ошибка: {e}", fg="red", err=True)
        sys.exit(1)
