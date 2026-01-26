from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 必须导入中间件
from .db import init_db
from .scheduler import start_scheduler
from .api.routes_health import router as health_router
from .api.routes_evidence import router as evidence_router
from .api.routes_sync import router as sync_router
from .api.routes_event import router as event_router
from adapter.clients.deepsoc_auth import DeepSOCAuth

def create_app() -> FastAPI:
    app = FastAPI(title="ly-deepsoc-adapter", version="0.1.0")

    # --- 新增 CORS 配置开始 ---
    # 允许来自 http://10.20.30.25:18080 的请求
    origins = [
        "http://10.20.30.25:18080",
        "http://localhost:18080", # 建议也带上本地测试地址
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,            # 允许的源
        allow_credentials=True,           # 允许携带 Cookie
        allow_methods=["*"],              # 允许所有方法 (GET, POST, OPTIONS 等)
        allow_headers=["*"],              # 允许所有请求头
    )
    # --- 新增 CORS 配置结束 ---
    
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

@app.on_event("startup")
def startup():
    # 启动即验证 DeepSOC 登录
    DeepSOCAuth.get_token()