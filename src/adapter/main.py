from fastapi import FastAPI
from .db import init_db
from .scheduler import start_scheduler
from .api.routes_health import router as health_router
from .api.routes_evidence import router as evidence_router
from .api.routes_sync import router as sync_router
from .api.routes_event import router as event_router

def create_app() -> FastAPI:
    app = FastAPI(title="ly-deepsoc-adapter", version="0.1.0")

    @app.on_event("startup")
    def _startup():
        init_db()
        start_scheduler()

    app.include_router(health_router)
    app.include_router(evidence_router)
    app.include_router(event_router)
    app.include_router(sync_router)
    return app

app = create_app()
