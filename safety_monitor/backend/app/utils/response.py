from typing import Any


def success_response(data: Any, message: str = "success"):
    return {"code": 200, "message": message, "data": data}


def error_response(code: int, message: str):
    return {"code": code, "message": message, "data": None}
