from fastapi import APIRouter

from app.db.session import ping_database
from app.schemas.common import ok


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check() -> dict:
    return ok({"database": "ok" if ping_database() else "error"})
