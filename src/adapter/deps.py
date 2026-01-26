from .db import SessionLocal
from .clients.flowshadow import FlowShadowClient
from .clients.deepsoc import DeepSOCClient
from .config import settings

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_flowshadow_client() -> FlowShadowClient:
    return FlowShadowClient(str(settings.flowshadow_base_url), settings.flowshadow_api_key)

def get_deepsoc_client() -> DeepSOCClient:
    return DeepSOCClient(str(settings.deepsoc_base_url), settings.deepsoc_api_key)
