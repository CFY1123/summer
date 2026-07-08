from datetime import date, datetime
from decimal import Decimal
from typing import Any


def snake_to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.isoformat()
    return value


def camel_row(row: Any) -> dict[str, Any]:
    data = dict(row._mapping)
    return {snake_to_camel(key): json_value(value) for key, value in data.items()}
