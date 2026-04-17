from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapter.api.routes_admin import router as admin_router
from adapter.clients.deepsoc_auth import DeepSOCAuth

from .api.routes_event import router as event_router
from .api.routes_evidence import router as evidence_router
from .api.routes_health import router as health_router
from .api.routes_sso import router as sso_router
from .api.routes_sync import router as sync_router
from .db import init_db
from .scheduler import start_scheduler


def create_app() -> FastAPI:
    app = FastAPI(title="ly-deepsoc-adapter", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    @app.on_event("startup")
    def _startup():
        init_db()
        start_scheduler()

    app.include_router(health_router)
    app.include_router(evidence_router)
    app.include_router(event_router)
    app.include_router(sync_router)
    app.include_router(admin_router)
    app.include_router(sso_router)
    return app


app = create_app()


@app.on_event("startup")
def startup():
    DeepSOCAuth.get_token()
