from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import compat_v1, health, learning, project
from app.db.session import SessionLocal
from app.services.learning_service import ensure_default_user


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(project.router, prefix="/api")
app.include_router(learning.router, prefix="/api")
app.include_router(compat_v1.router)


@app.on_event("startup")
def startup() -> None:
    db = SessionLocal()
    try:
        ensure_default_user(db)
    finally:
        db.close()
