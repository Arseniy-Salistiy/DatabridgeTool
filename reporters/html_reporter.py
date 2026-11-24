import html
from pathlib import Path
from validators.validator import ValidationError

def generate_html_report(
    total: int,
    valid_count: int,
    invalid_count: int,
    errors: list[ValidationError],
    report_path: Path,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    rows_html = ""
    for err in errors:
        rows_html += f"""
        <tr>
            <td>{err.row_number}</td>
            <td>{html.escape(str(err.field_name))}</td>
            <td>{html.escape(str(err.invalid_value))}</td>
            <td>{html.escape(str(err.message))}</td>
        </tr>
        """

    if not rows_html:
        rows_html = '<tr><td colspan="4" style="text-align:center; color:green;">Ошибок не обнаружено!</td></tr>'

    content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>DataBridge — Отчёт о валидации</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
        .stats {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .card {{ padding: 15px 25px; border-radius: 8px; background: #f4f6f8; border: 1px solid #ddd; }}
        .card h3 {{ margin: 0 0 5px 0; font-size: 14px; color: #666; }}
        .card p {{ margin: 0; font-size: 24px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #2c3e50; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Отчёт об обработке данных (DataBridge)</h1>
    <div class="stats">
        <div class="card"><h3>Всего записей</h3><p>{total}</p></div>
        <div class="card"><h3>Успешно</h3><p style="color: green;">{valid_count}</p></div>
        <div class="card"><h3>С ошибками</h3><p style="color: red;">{invalid_count}</p></div>
    </div>
    <h2>Детализация ошибок</h2>
    <table>
        <thead>
            <tr>
                <th>Строка</th>
                <th>Поле</th>
                <th>Значение</th>
                <th>Описание ошибки</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
</body>
</html>
"""
    report_path.write_text(content, encoding="utf-8")
