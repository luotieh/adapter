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

    # 1. 更加宽松的 CORS 配置，确保错误响应也能正常返回
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],             # 临时改为 * 确保不是这里的问题
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]             # 暴露所有头部
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