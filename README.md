# DataBridge — конвертер и валидатор данных

Консольная утилита на Python, которая читает табличные данные из разных форматов, проверяет их по правилам из конфига, преобразует и сообщает об ошибках понятным языком.

Это инструмент обработки данных, а не учётная система: **без базы данных, только файлы**, интерфейс — командная строка плюс HTML-отчёт.

## Возможности

- **Чтение и запись:** CSV (разделитель настраивается, с заголовками и без), JSON (массив объектов), XML (плоская структура), Excel `.xlsx`. Формат определяется по расширению файла.
- **Валидация** по правилам из YAML или JSON-конфига: обязательность, тип, диапазон, регулярное выражение, уникальность, длина строки.
- **Преобразование:** переименование полей (`rename_to`) и трансформации `trim`, `upper`, `lower`, `replace`, `timestamp_to_date`.
- **Некорректные записи** не попадают в результат, а сохраняются в `errors.csv`; остальные записи обрабатываются дальше.
- **Отчёты:** сводка в консоли и `report.html` с таблицей ошибок и статистикой.
- **Понятные ошибки** вместо stack trace: битый JSON, неверная кодировка, неподдерживаемый формат, некорректный конфиг.

## Установка

Нужен Python 3.10+.

```bash
git clone https://github.com/Arseniy-Salistiy/DatabridgeTool.git
cd DatabridgeTool
python -m venv venv
venv\Scripts\activate        # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

## Использование

Три команды: `convert`, `validate`, `stats`.

```bash
# конвертация с валидацией и трансформациями
python main.py convert samples/input.csv --to json --config samples/schema.yaml --output output.json

# только валидация с HTML-отчётом
python main.py validate samples/input.csv --config samples/schema.yaml --report report.html

# статистика по файлу (записи, колонки, пустые значения)
python main.py stats samples/input.csv
```

### Параметры

| Параметр | Команды | Описание |
|---|---|---|
| `--to <формат>` | convert | Целевой формат: `csv`, `json`, `xml`, `xlsx` (если не задан `--output`) |
| `--output <файл>` | convert | Выходной файл; формат берётся из расширения |
| `--config <файл>` | convert, validate | Файл правил (YAML/JSON). Для `validate` обязателен |
| `--errors <файл>` | convert, validate | Куда сохранять некорректные записи (по умолчанию `errors.csv`) |
| `--report <файл>` | convert, validate | HTML-отчёт (по умолчанию `report.html`) |
| `--delimiter` | все | Разделитель CSV (по умолчанию `,`) |
| `--no-headers` | все | В CSV нет строки заголовков; колонки получат имена `колонка_0`, `колонка_1`, … |

`validate` завершается с кодом 1, если найдены ошибки, — это удобно для скриптов и CI. Без `--config` команда `convert` просто конвертирует формат без проверок.

## Конфигурационный файл

```yaml
fields:
  - name: id
    type: integer
    required: true
    unique: true
  - name: name
    rename_to: full_name
    type: string
    required: true
    min_length: 2
    transform: trim
  - name: email
    type: string
    required: true
    pattern: "^[^@]+@[^@]+\\.[^@]+$"
    transform: lower
  - name: age
    type: integer
    min: 16
    max: 100
  - name: birth_date
    type: date
    format: "YYYY-MM-DD"
```

| Ключ | Значение |
|---|---|
| `name` | Имя поля во входных данных (обязательно) |
| `type` | `integer`, `float`, `string`, `date`, `boolean` (по умолчанию `string`) |
| `required` | Поле не может быть пустым |
| `unique` | Значения не должны повторяться |
| `min` / `max` | Границы для чисел и дат (даты задаются в формате поля `format`) |
| `min_length` / `max_length` | Длина строки |
| `pattern` | Регулярное выражение |
| `format` | Формат даты: `YYYY`, `MM`, `DD` |
| `rename_to` | Новое имя колонки в результате |
| `transform` | `trim`, `upper`, `lower`, `replace` (со словарём `replace_map`), `timestamp_to_date` |

Пустые необязательные поля пропускаются без остальных проверок. Трансформации применяются только к записям, прошедшим валидацию.

## Пример «до / после»

Вход `samples/input.csv` — 11 записей с разными ошибками:

```csv
id,name,email,age,birth_date
1,  Иван  ,IVAN@mail.ru,25,1999-01-15
2,Мария,maria.mail.ru,30,1994-05-20
3,Пётр,petr@mail.ru,200,2000-03-10
4,,empty@mail.ru,22,2002-07-01
...
```

Сводка в консоли:

```text
Всего записей: 11
Успешно обработано: 2
Ошибок: 9
  - Строка 2: поле "email" не соответствует формату
  - Строка 3: поле "age" вне диапазона (200)
  - Строка 4: поле "name" обязательно для заполнения
  - Строка 5: поле "age" должно быть целым числом (abc)
  - Строка 6: поле "id" должно быть уникальным (дубликат: 1)
  ...
```

Результат `samples/output.json` — пробелы обрезаны, email в нижнем регистре, `name` переименовано в `full_name`:

```json
[
  { "id": "1", "full_name": "Иван", "email": "ivan@mail.ru", "age": "25", "birth_date": "1999-01-15" },
  { "id": "10", "full_name": "Сергей", "email": "sergey@mail.ru", "age": "35", "birth_date": "1989-06-30" }
]
```

«Строка N» — порядковый номер записи в файле (без строки заголовка). Некорректные записи лежат в `samples/errors.csv`, отчёт — в `samples/report.html`.

## Структура проекта

```text
cli/          команды convert, validate, stats (Click)
readers/      InterfaceReader и читатели CSV, JSON, XML, XLSX + factory
writers/      BaseWriter и писатели CSV, JSON, XML, XLSX + factory
validators/   загрузка конфига и движок валидации
converters/   маппинг полей и трансформации
reporters/    сводка в консоль и HTML-отчёт
samples/      тестовые данные, конфиг, результаты «до/после»
tests/        unit-тесты (pytest)
main.py       точка входа
```

### Как добавить новый формат

1. Создать класс-наследник `InterfaceReader` в `readers/` (и `BaseWriter` в `writers/`).
2. Добавить одну строку в `readers/factory.py` и `writers/factory.py`.

Остальной код менять не нужно: все модули работают с единым представлением — списком словарей.

## Тесты

```bash
python -m pytest -v
```

Покрыто: границы `min`/`max` и длины строк, regex, уникальность, пустые и необязательные поля, неверные типы, диапазон дат, некорректный конфиг, чтение и запись всех четырёх форматов, CSV без заголовков с нестандартным разделителем, битый JSON, неподдерживаемое расширение, маппинг и все трансформации.

## Ограничения

- XML — только плоская структура (`<records><record>…`).
- Excel читается с первого (активного) листа.
- Файл целиком загружается в память — для очень больших файлов нужна потоковая обработка.
- В выходных файлах значения остаются в исходном виде (из CSV всё приходит строками).
