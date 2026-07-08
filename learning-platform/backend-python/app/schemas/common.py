from typing import Any


def ok(data: Any = None) -> dict[str, Any]:
    return {"code": 200, "message": "success", "data": data}


def fail(message: str, code: int = 400) -> dict[str, Any]:
    return {"code": code, "message": message, "data": None}
